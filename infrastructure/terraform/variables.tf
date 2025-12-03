variable "project_id" {
  description = "nyc-lakehouse-prod"
  type        = string
}

variable "region" {
  description = "Región predeterminada"
  type        = string
  default     = "us-central1" 
}

variable "gcs_bucket_name" {
  description = "Nombre único del bucket para el Data Lake"
  type        = string
}

variable "bq_dataset_name" {
  description = "Nombre del dataset de BigQuery"
  type        = string
  default     = "nyc_taxi_wh"
}
