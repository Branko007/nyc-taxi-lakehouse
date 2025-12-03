# Data Lake: Google Cloud Storage Bucket
resource "google_storage_bucket" "data_lake" {
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = true # Permite borrar el bucket aunque tenga datos (útil para dev)

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 # Limpieza automática de archivos viejos (ahorro de costos)
    }
  }
}

# Data Warehouse: BigQuery Dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.bq_dataset_name
  friendly_name              = "NYC Taxi DWH"
  description                = "Dataset principal para el Lakehouse"
  location                   = var.region
  delete_contents_on_destroy = true # Cuidado en prod, útil aquí
}
