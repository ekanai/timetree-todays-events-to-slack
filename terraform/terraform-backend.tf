terraform {
  backend "gcs" {
    bucket = "tools-terraform"
    prefix = "state"
  }
}
