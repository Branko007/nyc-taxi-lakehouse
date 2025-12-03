terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  credentials = file("../../gcp_credentials/terraform-key.json") # Ruta a tu key
  project     = var.project_id
  region      = var.region
}
