# 📘 Guía de Implementación: NYC Taxi Lakehouse

Bienvenido. Esta guía te acompañará paso a paso en la construcción de una plataforma de datos moderna (Lakehouse) utilizando **Google Cloud Platform (GCP)**, **Terraform** y **Python**.

**Objetivo:** Crear un entorno de producción simulado que implemente las mejores prácticas de la industria: Infraestructura como Código (IaC), Integración Continua (CI/CD) y Orquestación de Datos.

---

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas en tu entorno local (recomendado WSL2 en Windows o Linux/macOS):

*   **Git**: Para el control de versiones.
*   **Google Cloud CLI (gcloud)**: Para interactuar con GCP desde la terminal.
*   **Terraform**: Para desplegar la infraestructura.
*   **Python 3.9+**: Lenguaje base del proyecto.
*   **uv**: Gestor de paquetes de Python ultra rápido (lo instalaremos en la Fase 1 si no lo tienes).

---

## 🏗️ Fase 1: Configuración del Entorno Local

El primer paso es preparar un entorno de desarrollo limpio, seguro y escalable.

### 1. Estructura del Proyecto

Vamos a crear el "scaffolding" (andamiaje) del proyecto. Esta estructura separa claramente la infraestructura (Terraform) del código de la aplicación (Python/SQL), facilitando el mantenimiento.

Ejecuta los siguientes comandos en tu terminal:

```bash
# 1. Crear directorio principal
mkdir nyc-taxi-lakehouse
cd nyc-taxi-lakehouse

# 2. Inicializar Git (Control de versiones)
git init
git branch -M main

# 3. Crear estructura de subdirectorios
mkdir -p infrastructure/terraform   # Código Terraform (IaC)
mkdir -p gcp_credentials            # Credenciales (¡Nunca subir a Git!)
mkdir -p src/ingestion              # Scripts de carga de datos
mkdir -p dags                       # Apache Airflow DAGs
mkdir -p dbt_project                # Transformaciones dbt
mkdir -p .github/workflows          # CI/CD (GitHub Actions)
mkdir -p tests                      # Tests unitarios
```

Tu estructura de carpetas debería verse así:

```text
nyc-taxi-lakehouse/
├── dags/
├── dbt_project/
├── gcp_credentials/
├── infrastructure/
│   └── terraform/
├── src/
│   └── ingestion/
├── tests/
└── .github/
```

### 2. Seguridad (.gitignore)

> [!IMPORTANT]
> **Seguridad Crítica**: Nunca subas credenciales, archivos de estado de Terraform o entornos virtuales a un repositorio público.

Crea un archivo llamado `.gitignore` en la raíz del proyecto y añade el siguiente contenido para proteger tu repositorio:

```text
# --- Python ---
.venv/
venv/
__pycache__/
*.pyc

# --- Configuración Local ---
.env
.DS_Store

# --- Google Cloud (¡VITAL!) ---
gcp_credentials/
*.json

# --- Terraform ---
.terraform/
.terraform.lock.hcl
*.tfstate
*.tfstate.backup
```

### 3. Gestión de Dependencias con `uv`

Utilizaremos **uv** en lugar del `pip` tradicional. `uv` es significativamente más rápido y maneja las resoluciones de dependencias de manera más robusta.

```bash
# 1. Inicializar proyecto con uv
uv init

# 2. Crear entorno virtual (.venv)
uv venv

# 3. Activar entorno
# En Linux/macOS/WSL:
source .venv/bin/activate
# En Windows (PowerShell):
# .venv\Scripts\activate

# 4. Instalar librerías base
uv pip install polars pyarrow google-cloud-storage python-dotenv
```

---

## ☁️ Fase 2: Configuración de Google Cloud (Manual)

Aunque automatizaremos la infraestructura, necesitamos un proyecto base y una cuenta de servicio para que Terraform pueda actuar en nuestro nombre.

1.  **Crear Proyecto**: Ve a la [Consola de GCP](https://console.cloud.google.com/) y crea un nuevo proyecto.
    *   *Nombre sugerido*: `nyc-lakehouse-prod`
2.  **Vincular Facturación**: Asegúrate de que el proyecto tenga una cuenta de facturación asociada.
3.  **Habilitar APIs**: Busca y habilita las siguientes APIs:
    *   *Compute Engine API*
    *   *Google Cloud Storage JSON API*
    *   *BigQuery API*
4.  **Crear Service Account para Terraform**:
    *   Ve a **IAM y administración** > **Cuentas de servicio**.
    *   Crea una cuenta llamada `terraform-runner`.
    *   **Rol**: Asignale el rol de **Propietario (Owner)** (Nota: En un entorno real usaríamos roles más restrictivos, pero esto facilita el aprendizaje).
    *   **Clave**: Crea una nueva clave **JSON** y descárgala.
    *   **Acción**: Mueve el archivo descargado a la carpeta `nyc-taxi-lakehouse/gcp_credentials/` y renómbralo a `terraform-key.json`.

---

## 🛠️ Fase 3: Infraestructura como Código (Terraform)

En esta fase, definiremos nuestro Data Lake (GCS) y Data Warehouse (BigQuery) mediante código. Esto permite que nuestra infraestructura sea reproducible y versionable.

**Directorio de trabajo:** `infrastructure/terraform/`

### 1. Proveedor (`provider.tf`)

Este archivo le dice a Terraform que vamos a trabajar con Google Cloud y cómo autenticarse.

```hcl
# infrastructure/terraform/provider.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  # Ruta a la clave que descargamos en la Fase 2
  credentials = file("../../gcp_credentials/terraform-key.json")
  project     = var.project_id
  region      = var.region
}
```

### 2. Variables (`variables.tf`)

Definimos variables para hacer nuestro código reutilizable y limpio.

```hcl
# infrastructure/terraform/variables.tf

variable "project_id" {
  description = "ID del proyecto en GCP"
  type        = string
}

variable "region" {
  description = "Región predeterminada para los recursos"
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
```

### 3. Recursos Principales (`main.tf`)

Aquí ocurre la magia. Definimos el Bucket de almacenamiento y el Dataset de BigQuery.

```hcl
# infrastructure/terraform/main.tf

# --- Data Lake: Google Cloud Storage Bucket ---
resource "google_storage_bucket" "data_lake" {
  name          = var.gcs_bucket_name
  location      = var.region
  
  # ¡CUIDADO! Esto permite borrar el bucket aunque tenga datos.
  # Útil para desarrollo, peligroso en producción.
  force_destroy = true 
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  # Regla de ciclo de vida: Borrar objetos antiguos automáticamente
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 # Días
    }
  }
}

# --- Data Warehouse: BigQuery Dataset ---
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.bq_dataset_name
  friendly_name              = "NYC Taxi DWH"
  description                = "Dataset principal para el Lakehouse"
  location                   = var.region
  delete_contents_on_destroy = true # Solo para desarrollo
}
```

### 4. Valores de Variables (`terraform.tfvars`)

Crea este archivo para asignar valores a tus variables.

> [!WARNING]
> Este archivo contiene información específica de tu entorno. Asegúrate de que esté en tu `.gitignore` si decides hacerlo público (aunque en este caso solo son IDs).

```hcl
# infrastructure/terraform/terraform.tfvars

project_id      = "TU_ID_DE_PROYECTO_REAL"       # Reemplaza con tu ID de proyecto
gcs_bucket_name = "nyc-taxi-lakehouse-raw-tu-nombre" # Debe ser globalmente único
region          = "us-central1"
```

### 5. Despliegue

Finalmente, inicializa y aplica la configuración:

```bash
cd infrastructure/terraform

# 1. Descargar plugins necesarios
terraform init

# 2. Ver qué cambios se realizarán (Plan de ejecución)
terraform plan

# 3. Aplicar los cambios en la nube
terraform apply
# Escribe 'yes' cuando se te solicite confirmación.
```

¡Felicidades! 🎉 Has desplegado tu infraestructura base en Google Cloud.

### 6. Control de Versiones y Primer Commit

Como Git no rastrea directorios vacíos por defecto, necesitamos "anclar" las carpetas de nuestra futura estructura (como `dags` o `src`) para que se suban al repositorio. Usaremos la convención de archivos `.gitkeep`.

#### 1. Preservar estructura de directorios
Ejecuta los siguientes comandos en la terminal para crear archivos ocultos en las carpetas vacías:

```bash
# Volver a la raíz del proyecto (si estabas en infrastructure/terraform)
cd ../.. 

# Crear archivos .gitkeep
touch dags/.gitkeep
touch src/ingestion/.gitkeep
touch dbt_project/.gitkeep
touch tests/.gitkeep
```

### 1. Verificar qué archivos detecta Git
```bash
git status
```
### Deberías ver las nuevas carpetas y los archivos .tf

### 2. Agregar todo al área de preparación (Staging)
```bash
git add .
```

### 3. Crear el primer Commit
```bash
git commit -m "feat: init project structure, iaC setup and gitkeep for empty dirs"
```

### 4. Renombrar rama principal a 'main'
```bash
git branch -M main
```

### 5. Conectar con GitHub y subir (Solo la primera vez)
Reemplaza TU_USUARIO con tu usuario real de GitHub en el siguiente comando:

git remote add origin [https://github.com/TU_USUARIO/nyc-taxi-lakehouse.git](https://github.com/TU_USUARIO/nyc-taxi-lakehouse.git)

```bash
git push -u origin main
```