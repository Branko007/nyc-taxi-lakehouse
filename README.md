# 🚕 NYC Taxi Data Lakehouse

![Data Engineering](https://img.shields.io/badge/Data%20Engineering-blue)
![GCP](https://img.shields.io/badge/Cloud-GCP-green)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![Python](https://img.shields.io/badge/Language-Python%203.10-yellow)
![Airflow](https://img.shields.io/badge/Orchestration-Airflow-red)

Este proyecto implementa una arquitectura de **Data Lakehouse** profesional para el procesamiento de datos masivos de los taxis de Nueva York (NYC Taxi & Limousine Commission). El objetivo es demostrar un flujo end-to-end robusto, escalable y automatizado, siguiendo las mejores prácticas de la industria.

## 🏗️ Arquitectura y Tecnologías

El sistema está diseñado bajo el paradigma de **Infraestructura como Código (IaC)** y procesamiento eficiente en memoria:

*   **Cloud Provider**: Google Cloud Platform (GCP).
*   **Infraestructura**: Terraform (GCS Buckets, BigQuery Datasets).
*   **Procesamiento**: Python 3.10+ con **Polars** (alto rendimiento).
*   **Transformación**: **dbt** (Data Build Tool) para la lógica de negocio en SQL.
*   **Arquitectura**: **Medallion Architecture** (Bronze, Silver).
*   **Gestión de Dependencias**: `uv` (el gestor de paquetes más rápido).
*   **Contenerización**: Docker (Imágenes especializadas para Ingesta y dbt).
*   **Orquestación**: Apache Airflow (vía Docker Compose).
*   **Almacenamiento**: Data Lake (GCS) + Data Warehouse (BigQuery).

## 📂 Estructura del Proyecto

```text
.
├── dags/                   # Definiciones de flujos en Airflow
├── dbt_project/            # Modelos de transformación (Medallion Architecture)
├── infrastructure/         # Código de Terraform para la nube
│   └── terraform/          # Definición de recursos GCP
├── src/                    # Código fuente de la lógica de negocio
│   └── ingestion/          # Scripts de ingesta y transformación inicial
├── gcp_credentials/        # 🔒 Directorio para llaves JSON (ignorado en Git)
├── Dockerfile              # Receta para el contenedor de ingesta
├── Dockerfile.dbt          # Receta para el contenedor de dbt
├── docker-compose.yml      # Configuración de la plataforma Airflow
├── pyproject.toml          # Configuración de dependencias (uv)
└── tutorial.md             # Guía detallada paso a paso
```

## 🚀 Puesta en Marcha

Como Data Engineer, he diseñado este proceso para que sea reproducible y seguro.

### 1. Preparación de Credenciales
1. Crea un proyecto en GCP.
2. Habilita las APIs de Storage, BigQuery y Compute Engine.
3. Crea una Service Account con rol de `Owner` (para desarrollo) y descarga la llave JSON.
4. Guarda la llave en `gcp_credentials/terraform-key.json`.

### 2. Despliegue de Infraestructura (Terraform)
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```
*Esto creará automáticamente tu Bucket en GCS y el Dataset en BigQuery.*

### 3. Configuración del Entorno Local
Usamos `uv` para una gestión de paquetes ultra-rápida:
```bash
uv venv
source .venv/bin/activate
uv sync
```

### 4. Ejecución de la Ingesta (Docker)
Puedes correr el proceso de ingesta de forma aislada:
```bash
# Construir la imagen
docker build -t nyc-taxi-ingestor:v1 .

# Ejecutar para un mes específico
docker run --rm \
  -v $(pwd)/gcp_credentials:/app/gcp_credentials \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/gcp_credentials/terraform-key.json \
  -e GCS_BUCKET_NAME="tu-bucket-name" \
  nyc-taxi-ingestor:v1 --year 2024 --month 1

# Ejecutar transformaciones dbt
docker build -t nyc-taxi-dbt:v1 -f Dockerfile.dbt .
docker run --rm \
  -v $(pwd)/dbt_project:/usr/app/dbt_project \
  -v $(pwd)/gcp_credentials:/usr/app/gcp_credentials \
  nyc-taxi-dbt:v1 run --profiles-dir .
```

### 5. Orquestación con Airflow
Para levantar la plataforma completa de orquestación:
```bash
docker compose up -d
```
Accede a la interfaz en `http://localhost:8080` (User/Pass: `admin`/`admin`).

## 🛠️ Mejores Prácticas Implementadas

*   **Programación Orientada a Objetos (POO)**: El ingestor está encapsulado en clases modulares y testeables.
*   **Particionamiento Hive**: Los datos se almacenan en GCS siguiendo el patrón `year=YYYY/month=MM/` para optimizar costos y velocidad en BigQuery.
*   **Seguridad**: Uso estricto de `.gitignore` para proteger secretos y variables de entorno.
*   **Logging y Observabilidad**: Implementación de logs estructurados para facilitar el debugging en producción.
*   **Docker out of Docker**: Airflow configurado para lanzar tareas en contenedores hermanos, manteniendo el orquestador limpio.

---
