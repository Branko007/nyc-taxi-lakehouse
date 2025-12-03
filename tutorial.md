# 📘 Guía Maestra: Construyendo un Data Lakehouse con GCP & Python

¡Bienvenido/a! Estás a punto de construir una plataforma de datos profesional. Esta guía no es solo un recetario de comandos; es un recorrido diseñado para que **entiendas** cada decisión arquitectónica.

Utilizaremos un stack moderno y demandado en la industria: **Google Cloud Platform (GCP)**, **Terraform** (Infraestructura como Código) y **Python** con **Polars**.

---

## 🎯 Objetivo del Proyecto

Simularemos un entorno de producción real para una empresa de taxis (NYC Taxi).
**Tu misión:** Crear un sistema automatizado que ingeste, procese y almacene datos masivos de viajes, permitiendo análisis rápidos y eficientes.

**Lo que aprenderás:**
*   🏗️ **IaC**: Cómo levantar infraestructura sin hacer clics manuales.
*   🛡️ **Seguridad**: Manejo de credenciales y roles.
*   🐍 **Python Moderno**: Uso de tipos estáticos, POO y librerías de alto rendimiento (Polars).
*   ☁️ **Cloud Engineering**: Conceptos de Data Lake vs Data Warehouse.

---

## 📋 Prerrequisitos

Antes de empezar, necesitamos preparar tu "caja de herramientas". Asegúrate de tener esto instalado en tu entorno (WSL2, Linux o macOS):

*   **Git**: Para guardar tu progreso y versionar el código.
*   **Google Cloud CLI (`gcloud`)**: El "control remoto" de GCP desde tu terminal.
*   **Terraform**: El albañil que construirá tu infraestructura.
*   **Python 3.9+**: El cerebro de nuestra lógica.
*   **uv**: Un gestor de paquetes ultra-rápido (lo instalaremos juntos si no lo tienes).

---

## 🏗️ Fase 1: Cimientos y Entorno Local

Al igual que un edificio necesita cimientos sólidos, un proyecto de software necesita una estructura ordenada y segura.

### 1. El "Scaffolding" (Andamiaje)

Vamos a crear una estructura de carpetas profesional. Separaremos la **infraestructura** (el "hardware" virtual) del **código** (la lógica de negocio).

Ejecuta esto en tu terminal:

```bash
# 1. Crear la carpeta raíz del proyecto
mkdir nyc-taxi-lakehouse
cd nyc-taxi-lakehouse

# 2. Inicializar Git (Tu bitácora de cambios)
git init
git branch -M main

# 3. Crear la estructura de directorios
mkdir -p infrastructure/terraform   # Aquí vivirá la definición de la nube
mkdir -p gcp_credentials            # 🔒 Aquí guardaremos las llaves (¡SECRETO!)
mkdir -p src/ingestion              # Código Python para descargar datos
mkdir -p dags                       # Orquestación (Airflow)
mkdir -p dbt_project                # Transformación de datos (SQL)
mkdir -p .github/workflows          # Automatización CI/CD
mkdir -p tests                      # Pruebas de calidad
```

### 2. Seguridad Primero (`.gitignore`)

> [!IMPORTANT]
> **Regla de Oro**: Las credenciales (claves, contraseñas) **NUNCA** se suben a Git.

Creamos un archivo `.gitignore` para decirle a Git qué archivos ignorar:

```text
# --- Python (Archivos temporales y entornos) ---
.venv/
venv/
__pycache__/
*.pyc

# --- Configuración Local ---
.env        # Variables de entorno (claves)
.DS_Store   # Basura de macOS

# --- Google Cloud (¡CRÍTICO!) ---
gcp_credentials/
*.json

# --- Terraform (Estado de la infraestructura) ---
.terraform/
.terraform.lock.hcl
*.tfstate
*.tfstate.backup
```

### 3. Gestión de Dependencias con `uv`

Usaremos `uv` en lugar de `pip`. Imagina que `pip` es un instalador manual y `uv` es un equipo de instalación automatizado de alta velocidad.

```bash
# 1. Inicializar el gestor de paquetes
uv init

# 2. Crear un entorno virtual aislado (.venv)
# Esto evita que las librerías de este proyecto choquen con otros.
uv venv

# 3. Activar el entorno
# En Linux/macOS/WSL:
source .venv/bin/activate
# En Windows (PowerShell):
# .venv\Scripts\activate

# 4. Instalar librerías iniciales
uv pip install polars pyarrow google-cloud-storage python-dotenv
```

---

## ☁️ Fase 2: Configuración de Google Cloud (El "Bootstrap")

Aunque usaremos Terraform para casi todo, necesitamos un punto de partida manual en la nube (el problema del "huevo y la gallina").

1.  **Crear Proyecto**: Ve a la [Consola de GCP](https://console.cloud.google.com/) y crea un proyecto nuevo (ej. `nyc-lakehouse-prod`).
2.  **Facturación**: Asegúrate de que tenga una cuenta de facturación activa (GCP te da crédito gratis inicial).
3.  **Habilitar APIs**: Las APIs son los enchufes que permiten controlar los servicios. Busca y habilita:
    *   *Compute Engine API*
    *   *Google Cloud Storage JSON API*
    *   *BigQuery API*
4.  **El Robot Constructor (Service Account)**:
    *   Ve a **IAM y administración** > **Cuentas de servicio**.
    *   Crea una cuenta llamada `terraform-runner`.
    *   **Rol**: Dale rol de **Propietario (Owner)** (Para este tutorial simplifica las cosas; en producción seríamos más estrictos).
    *   **Clave**: Crea una clave **JSON**, descárgala y guárdala en tu carpeta `nyc-taxi-lakehouse/gcp_credentials/` con el nombre `terraform-key.json`.

---

## 🛠️ Fase 3: Infraestructura como Código (Terraform)

En lugar de hacer clics en la consola para crear servidores, escribiremos "recetas" de código que describen lo que queremos. Terraform leerá la receta y construirá todo.

**Ve a la carpeta:** `cd infrastructure/terraform/`

### 1. El Proveedor (`provider.tf`)

Define quién es el proveedor de nube (Google) y cómo autenticarse.

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  credentials = file("../../gcp_credentials/terraform-key.json")
  project     = var.project_id
  region      = var.region
}
```

### 2. Las Variables (`variables.tf`)

Hacemos el código reutilizable. En lugar de escribir "mi-proyecto" en todos lados, usamos variables.

```hcl
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

```

### 3. Los Recursos (`main.tf`)

Aquí definimos qué queremos construir: un **Bucket** (disco duro ilimitado en la nube) y un **Dataset** (base de datos analítica Big Query).

```hcl
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

```

### 4. Tus Valores (`terraform.tfvars`)

Aquí pones tus datos reales.
**¡OJO!** Si este archivo tuviera contraseñas, debería ir al `.gitignore`.

```hcl
project_id      = "TU_ID_DE_PROYECTO_REAL"       # <--- CAMBIA ESTO
gcs_bucket_name = "nyc-taxi-lakehouse-raw-tunombre" # <--- CAMBIA ESTO (Debe ser único en todo Google)
region          = "us-central1"
```

### 5. ¡A Desplegar!

```bash
# 1. Inicializar (descargar plugins)
terraform init

# 2. Planificar (ver qué va a pasar)
terraform plan

# 3. Aplicar (construir la infraestructura)
terraform apply
# Escribe 'yes' para confirmar.
```

#### ¡Felicidades! 🎉 Has desplegado tu infraestructura base en Google Cloud.
---

## 💾 Intermedio: Guardando el Progreso (Git)

Git no guarda carpetas vacías. Para mantener nuestra estructura organizada en el repositorio, usaremos un truco: poner un archivo vacío llamado `.gitkeep` en cada carpeta.

```bash
cd ../..  # Volver a la raíz del proyecto

# Crear archivos ancla
touch dags/.gitkeep src/ingestion/.gitkeep dbt_project/.gitkeep tests/.gitkeep

# Guardar todo en Git
git add .
git commit -m "feat: init project structure and infrastructure"

# Subir a GitHub (Configura tu repo remoto primero)
# git remote add origin <TU_URL_DE_GITHUB>
# git push -u origin main
```

---

## 🐍 Fase 4: El Motor de Ingestión (Python + POO)

Ahora que tenemos infraestructura, necesitamos datos. Crearemos un programa en Python que:
1.  **Descargue** datos oficiales de los taxis de NYC.
2.  **Valide** y transforme ligeramente los datos.
3.  **Suba** los archivos a nuestro Data Lake en la nube.

### ¿Por qué Python y POO?
Usaremos **Programación Orientada a Objetos (Clases)**. Esto hace que el código sea modular (piezas de Lego) y fácil de probar, a diferencia de un script "espagueti" que hace todo de arriba a abajo.

### Preparación de Librerías

Usaremos `uv add` para instalar y registrar las dependencias en `pyproject.toml` (como el `package.json` de Node.js).

```bash
uv add requests polars google-cloud-storage python-dotenv pyarrow
```

### Configuración (`.env`)

Crea un archivo `.env` en la raíz. Esto permite cambiar la configuración sin tocar el código.

```ini
GOOGLE_APPLICATION_CREDENTIALS="gcp_credentials/terraform-key.json"
GCP_PROJECT_ID="tu-project-id-real"
GCS_BUCKET_NAME="nyc-taxi-lakehouse-raw-tunombre" # El mismo que pusiste en Terraform
```

### El Código (`src/ingestion/ingest_manager.py`)

Crea este archivo. Lee los comentarios en el código, explican el "por qué" de cada bloque.

```python
import os
import logging
import requests
import polars as pl
from google.cloud import storage
from datetime import datetime
from dotenv import load_dotenv
import sys

# Configuración básica de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class TaxiIngestor:
    """
    Clase responsable de descargar, transformar mínimamente y cargar 
    datos de NYC Taxis al Data Lake (GCS).
    """

    def __init__(self, bucket_name: str):
        """
        Inicializa el cliente de GCS y configura el bucket de destino.
        """
        self.bucket_name = bucket_name  
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        logging.info(f"🔧 Ingestor inicializado para bucket: {bucket_name}")

    def download_data(self, year: int, month: int, service_type: str = "yellow") -> str:
        """
        Descarga el archivo Parquet desde la web de NYC TLC a un temporal local.
        Retorna la ruta del archivo local.
        """
        # Formato de URL oficial de NYC TLC: 
        # https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
        month_str = f"{month:02d}"
        file_name = f"{service_type}_tripdata_{year}-{month_str}.parquet"
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file_name}"
        local_path = f"/tmp/{file_name}"

        logging.info(f"⬇️ Iniciando descarga desde: {url}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status() # Lanza error si 404/500

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logging.info(f"✅ Archivo descargado en: {local_path}")
            return local_path
            
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Error descargando archivo: {e}")
            raise

    def validate_and_transform(self, file_path: str) -> str:
        """
        Lee el archivo con Polars para validar esquema y añade metadatos de ingestión.
        Retorna la ruta del archivo procesado listo para subir.
        """
        logging.info("🔄 Validando y procesando con Polars...")
        
        try:
            # Lazy Loading para eficiencia de memoria
            df = pl.scan_parquet(file_path)
            
            # Agregamos una columna de metadatos: fecha de ingestión
            # Esto es vital para auditoría en un Data Lake.
            df_processed = df.with_columns(
                pl.lit(datetime.now()).alias("ingestion_timestamp")
            )

            # Materializamos (collect) y guardamos de nuevo optimizado
            output_path = file_path.replace(".parquet", "_processed.parquet")
            df_processed.collect().write_parquet(output_path)
            
            logging.info(f"✨ Transformación completada. Filas procesadas.")
            return output_path

        except Exception as e:
            logging.error(f"❌ Error procesando con Polars: {e}")
            raise

    def upload_to_gcs(self, local_path: str, destination_blob_name: str):
        """
        Sube el archivo procesado al Data Lake (GCS).
        """
        logging.info(f"☁️ Subiendo {local_path} a gs://{self.bucket_name}/{destination_blob_name}")
        
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(local_path)
            logging.info("🚀 Carga a GCS exitosa.")
        except Exception as e:
            logging.error(f"❌ Error subiendo a GCS: {e}")
            raise

    def clean_local(self, *files):
        """Borra archivos temporales para mantener el contenedor/entorno limpio."""
        for f in files:
            if os.path.exists(f):
                os.remove(f)
        logging.info("🧹 Limpieza de archivos temporales completada.")

if __name__ == "__main__":
    # Cargar variables de entorno
    load_dotenv()
    
    BUCKET = os.getenv("GCS_BUCKET_NAME")
    if not BUCKET:
        raise ValueError("La variable GCS_BUCKET_NAME no está definida en .env")

    # Ejecución de prueba
    ingestor = TaxiIngestor(bucket_name=BUCKET)
    
    # Probamos con Enero 2024 (Yellow Taxis)
    YEAR = 2024
    MONTH = 1
    
    try:
        raw_file = ingestor.download_data(YEAR, MONTH)
        processed_file = ingestor.validate_and_transform(raw_file)
        
        # Estructura de carpeta tipo Hive: year=YYYY/month=MM/file.parquet
        gcs_path = f"raw/yellow_tripdata/{YEAR}/{MONTH:02d}/data.parquet"
        
        ingestor.upload_to_gcs(processed_file, gcs_path)
        
        # Limpieza
        ingestor.clean_local(raw_file, processed_file)
        
    except Exception as main_error:
        logging.critical(f"💀 El proceso falló: {main_error}")
        exit(1)

```

### 🧠 Conceptos Clave de este Código

1.  **Atomicidad**: Dividimos el problema en funciones pequeñas (`download`, `transform`, `upload`). Si algo falla, sabemos exactamente dónde.
2.  **Metadatos**: Agregamos `ingestion_timestamp`. En el futuro, si encuentras un error en los datos, podrás saber exactamente cuándo entraron al sistema.
3.  **Particionamiento**: No tiramos los archivos en una pila gigante. Los organizamos en carpetas `año/mes/`. Esto hará que las consultas en BigQuery sean **mucho más baratas y rápidas**.

### 🧪 Prueba de Fuego

Vamos a ejecutarlo. Asegúrate de estar en tu entorno virtual (`source .venv/bin/activate`).

```bash
python src/ingestion/ingest_manager.py
```

Si todo sale bien, verás los logs verdes y, si vas a tu consola de Google Cloud Storage, ¡verás tu archivo Parquet esperándote en la nube!

### 📝 Guardar Cambios (Git)

No olvides guardar tu trabajo duro.

```bash
git add src/ingestion/ingest_manager.py pyproject.toml uv.lock .env.example
# Nota: No agregues el .env real, crea un .env.example sin claves si quieres compartir la estructura.

git commit -m "feat: implement robust ingestion script with polars and gcs upload"
git push
```

¡Excelente trabajo! Has construido la primera tubería de datos de tu Lakehouse. 🚀