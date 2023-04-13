locals {
  google_cloud_scheduler_job-timetree-todays-events-to-slack = {}
}

resource "google_cloud_scheduler_job" "timetree-todays-events-to-slack" {
  for_each = local.google_cloud_scheduler_job-timetree-todays-events-to-slack

  name        = "timetree-todays-events-to-slack-${each.key}"
  description = "Cron ${each.value.schedule} to ${each.value.user}"
  schedule    = each.value.schedule
  time_zone   = each.value.time_zone

  pubsub_target {
    topic_name = google_pubsub_topic.timetree-todays-events-to-slack.id
    data       = base64encode(each.value.user)
  }
}

