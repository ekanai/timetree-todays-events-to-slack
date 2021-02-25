locals {
  google_cloud_scheduler_job-timetree-todays-events-to-slack = {
    fred_10 = {
      schedule  = "0 10 * * *"
      time_zone = "Asia/Tokyo"
      user      = "fred"
    }

    justin_08 = {
      schedule  = "0 8 * * *"
      time_zone = "Asia/Tokyo"
      user      = "justin"
    }

    mark_10 = {
      schedule  = "0 10 * * *"
      time_zone = "Asia/Tokyo"
      user      = "mark"
    }

    miu_08 = {
      schedule  = "0 08 * * *"
      time_zone = "Asia/Tokyo"
      user      = "miu"
    }

    miu_13 = {
      schedule  = "0 13 * * *"
      time_zone = "Asia/Tokyo"
      user      = "miu"
    }

    rio_09 = {
      schedule  = "0 9 * * *"
      time_zone = "Asia/Tokyo"
      user      = "rio"
    }

    miu_17 = {
      schedule  = "0 17 * * *"
      time_zone = "Asia/Tokyo"
      user      = "miu"
    }

    tiger_09 = {
      schedule  = "0 9 * * *"
      time_zone = "Asia/Tokyo"
      user      = "tiger"
    }

    yuu_09 = {
      schedule  = "0 9 * * *"
      time_zone = "Asia/Tokyo"
      user      = "yuu"
    }
  }
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

