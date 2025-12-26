# Data Lake: Google Cloud Storage Bucket
resource "google_storage_bucket" "data_lake" {
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = true # Permite borrar el bucket aunque tenga datos (útil para dev)

  uniform_bucket_level_access = true # Sirve para que todos los archivos dentro del bucket tengan el mismo nivel de acceso
  
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

# Data Warehouse: BigQuery Dataset (Bronze Layer)
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.bq_dataset_name
  friendly_name              = "NYC Taxi DWH - Bronze"
  description                = "Capa Bronze: Datos crudos y tablas externas"
  location                   = var.region
  delete_contents_on_destroy = true 
}

# Data Warehouse: BigQuery Dataset (Silver Layer)
resource "google_bigquery_dataset" "silver_dataset" {
  dataset_id                 = "nyc_taxi_silver"
  friendly_name              = "NYC Taxi DWH - Silver"
  description                = "Capa Silver: Datos limpios y deduplicados"
  location                   = var.region
  delete_contents_on_destroy = true
}

# Tabla Externa en BigQuery (Capa Bronze/Raw)
resource "google_bigquery_table" "external_yellow_taxi" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "external_yellow_taxi"
  description = "Tabla externa que apunta a los datos crudos en GCS"
  deletion_protection = false

  external_data_configuration {
    autodetect    = true
    source_format = "PARQUET"
    # El comodín * permite leer todos los archivos dentro de la estructura de carpetas
    source_uris   = ["gs://${var.gcs_bucket_name}/raw/yellow_tripdata/*.parquet"]
  }
}
