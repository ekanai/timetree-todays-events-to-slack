import datetime
import json
import os
import pytz
import requests

from google.cloud import datastore
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

upcoming_events_labels = {}
now = datetime.datetime.now() - datetime.timedelta(minutes=1)


def timetree_todays_events_to_slack(event, context):
    import base64

    print("""This Function was triggered by messageId {} published at {}
    """.format(context.event_id, context.timestamp))

    user = base64.b64decode(event['data']).decode('utf-8')
    print('Hello {}!'.format(user))

    # GCP Datastore
    datastore_client = datastore.Client()
    global tool_user
    tool_user = datastore_client.get(datastore_client.key('User', user))

    # TimeTree
    headers = {
        'Accept': 'application/vnd.timetree.v1+json',
        'Authorization': 'Bearer {}'.format(tool_user.get('timetree_token'))
    }

    # Get my events
    my_upcoming_events = get_my_upcoming_events(headers)
    if my_upcoming_events != []:
        post_to_slack(my_upcoming_events)


def get_my_upcoming_events(headers):
    calendars = get_calendars(headers)

    upcoming_events_events = []
    for calendar in calendars:
        upcoming_events = get_upcoming_events(calendar, headers)
        if 'data' in upcoming_events:
            insert_calendar_info_to_event(calendar, upcoming_events['data'])
            upcoming_events_events.extend(upcoming_events['data'])
        if 'included' in upcoming_events:
            upcoming_events_labels.update(
                parse_labels_from_upcoming_included(
                    upcoming_events['included']))

    my_upcoming_events = filter_upcoming_events(upcoming_events_events,
                                                headers)

    return my_upcoming_events


def get_calendars(headers):
    calendars_responce = get_request('https://timetreeapis.com/calendars',
                                     headers=headers)
    print('get_calendars status code {}!'.format(
        calendars_responce.status_code))
    calendars = calendars_responce.json()['data']
    return calendars


def get_upcoming_events(calendar, headers):
    upcoming_events_responce = get_request(
        'https://timetreeapis.com/calendars/{}/upcoming_events?timezone={}&days={}&include=creator,label,attendees'
        .format(calendar['id'], tool_user.get('time_zone'),
                tool_user.get('days')),
        headers=headers)
    print('upcoming_events_responce status code {}!'.format(
        upcoming_events_responce.status_code))
    upcoming_events = upcoming_events_responce.json()
    return upcoming_events


def insert_calendar_info_to_event(calendar, upcoming_events_events):
    for upcoming_events_event in upcoming_events_events:
        upcoming_events_event['calendar_id'] = calendar['id']
        upcoming_events_event['calendar_name'] = calendar['attributes']['name']
        upcoming_events_event['calendar_image_url'] = calendar['attributes'][
            'image_url']


def parse_labels_from_upcoming_included(upcoming_events_includeds):
    labels = {}
    for upcoming_events_included in upcoming_events_includeds:
        if upcoming_events_included['type'] == 'label':
            labels[upcoming_events_included['id']] = upcoming_events_included

    return labels


def filter_upcoming_events(upcoming_events_events, headers):
    filtered_upcoming_events = []
    filtered_upcoming_events.extend(
        filter_upcoming_events_from_user(
            filter_upcoming_events_from_category(upcoming_events_events),
            headers))

    sorted_filtered_upcoming_events = sorted(
        filtered_upcoming_events, key=lambda x: x['attributes']['start_at'])

    sorted_filtered_upcoming_events = [
        d for d in sorted_filtered_upcoming_events
        if d['attributes']['all_day']
        or datetime_stiring_to_datetime(d['attributes']['start_at']) > now
    ]
    return sorted_filtered_upcoming_events


def filter_upcoming_events_from_category(upcoming_events_events):
    filtered_upcoming_events = []
    for upcoming_event in upcoming_events_events:
        if upcoming_event['attributes']['category'] == 'schedule':
            filtered_upcoming_events.append(upcoming_event)

    return filtered_upcoming_events


def filter_upcoming_events_from_user(upcoming_events_events, headers):
    user_responce = get_request('https://timetreeapis.com/user',
                                headers=headers)
    print('user_responce status code {}!'.format(user_responce.status_code))
    user = user_responce.json()['data']

    filtered_upcoming_events_from_user = []
    for upcoming_event in upcoming_events_events:
        upcoming_event_users_id = []
        upcoming_event_users_id.append(
            get_creater_id_from_upcoming_event(upcoming_event))
        upcoming_event_users_id.extend(
            get_attendees_id_from_upcoming_event(upcoming_event))
        if user['id'] in upcoming_event_users_id:
            filtered_upcoming_events_from_user.append(upcoming_event)

    return filtered_upcoming_events_from_user


def get_creater_id_from_upcoming_event(upcoming_event):
    return upcoming_event['relationships']['creator']['data']['id'].split(
        ',')[1]


def get_attendees_id_from_upcoming_event(upcoming_event):
    attendees = upcoming_event['relationships']['attendees']['data']
    if attendees is None:
        return []

    attendees_id = []
    for attendee in attendees:
        attendees_id.append(attendee['id'].split(',')[1])

    return attendees_id


def post_to_slack(upcoming_events):
    slack_webhook_url = tool_user.get('slack_webhook_url')
    slack_channel = tool_user.get('slack_channel')
    message = {
        "channel": slack_channel,
        "icon_emoji": ":timetree:",
        "username": "TimeTree Todays Events",
        "text": "<@{}> 本日 {} これからの予定です".format(tool_user.key.name,
                                               today_string()),
        "attachments": []
    }
    for upcoming_event in upcoming_events:
        color = upcoming_events_labels[upcoming_event['relationships']['label']
                                       ['data']['id']]['attributes']['color']
        attachment = {
            "author_name":
            upcoming_event['calendar_name'],
            "author_icon":
            upcoming_event['calendar_image_url'],
            "title":
            upcoming_event['attributes']['title'],
            "title_link":
            os.environ['event_link_format'].format(
                upcoming_event['calendar_id'], upcoming_event['id']),
            "color":
            color,
            "fields": [{
                "value": event_range(upcoming_event)
            }]
        }
        message['attachments'].append(attachment)

    print(message)
    requests.post(slack_webhook_url, data=json.dumps(message))


def event_range(upcoming_event):
    if upcoming_event['attributes']['all_day']:
        return 'All Day'

    start_at = format_datetime_to_display(
        upcoming_event['attributes']['start_at'])
    ent_at = format_datetime_to_display(upcoming_event['attributes']['end_at'])

    return '{} - {}'.format(start_at, ent_at)


def format_datetime_to_display(datetime_string):
    return datetime_stiring_to_datetime(datetime_string).astimezone(
        pytz.timezone(tool_user.get('time_zone'))).strftime('%H:%M')


def datetime_stiring_to_datetime(datetime_string):
    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S.%fZ')


def today_string():
    return now.astimezone(pytz.timezone(
        tool_user.get('time_zone'))).strftime('%Y/%m/%d (%a)')


def get_request(url, headers):
    session = requests.Session()
    retries = Retry(total=3,
                    backoff_factor=1,
                    status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    response = session.get(url=url,
                           headers=headers,
                           stream=True,
                           timeout=(3.0, 30.0))
    return response
