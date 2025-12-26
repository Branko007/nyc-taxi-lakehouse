# Bloque de configuración de Terraform: Define los plugins necesarios
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google" # Origen del proveedor oficial de GCP
      version = "4.51.0"           # Se fija la versión para garantizar estabilidad y evitar cambios inesperados
    }
  }
  backend "gcs" {
    bucket  = "nyc-taxi-lakehouse-terraform-state-branko007" # Bucket de GCS donde se almacenará el estado de Terraform
    prefix  = "terraform/state" # Prefijo para organizar el estado de Terraform
  }
}

provider "google" {
  credentials = file("../../gcp_credentials/terraform-key.json") # Ruta a tu key 
  project     = var.project_id # ID del proyecto de GCP
  region      = var.region # Región de GCP
}
