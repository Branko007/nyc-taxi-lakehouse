terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
  backend "gcs" {
    bucket  = "nyc-taxi-lakehouse-terraform-state-branko007"
    prefix  = "terraform/state"
  }
}

provider "google" {
  credentials = file("../../gcp_credentials/terraform-key.json") # Ruta a tu key
  project     = var.project_id
  region      = var.region
}
