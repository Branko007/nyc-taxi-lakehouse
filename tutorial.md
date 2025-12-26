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
uv add "requests>=2.32.5" "polars>=1.35.2" "google-cloud-storage>=3.6.0" "python-dotenv>=1.2.1" "pyarrow>=22.0.0"
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

## 🐳 Fase 5: Dockerización y CLI (Hacia Producción)

Hasta ahora, hemos ejecutado el script manualmente cambiando las variables en el código. Pero en un entorno profesional (como Airflow), **nadie edita código para correr un proceso**. Los scripts deben ser flexibles y portátiles.

En esta fase haremos dos cosas cruciales:
1.  **Refactorizar a CLI:** Convertir el script en una herramienta de línea de comandos que acepte argumentos (ej: `--year 2024`).
2.  **Containerizar:** Empaquetar todo en **Docker** para que funcione idéntico en tu PC, en un servidor o en la nube.

### 1. Refactorización: De Script a CLI

Vamos a modificar **solamente el bloque final** de `src/ingestion/ingest_manager.py`. Usaremos la librería nativa `argparse` para que el script "escuche" parámetros externos.

Reemplaza el bloque `if __name__ == "__main__":` (al final del archivo) con este código:

```python
import argparse # Asegúrate de importar esto al inicio del archivo

# ... (El código de la clase TaxiIngestor NO CAMBIA) ...

if __name__ == "__main__":
    # 1. Configuración de Argumentos CLI (Interfaz de Línea de Comandos)
    # Esto permite ejecutar: python script.py --year 2024 --month 2
    parser = argparse.ArgumentParser(description="Ingestión de datos de NYC Taxi a GCS")
    parser.add_argument("--year", type=int, required=True, help="Año de los datos (ej. 2024)")
    parser.add_argument("--month", type=int, required=True, help="Mes de los datos (1-12)")
    
    args = parser.parse_args()

    # 2. Carga de entorno
    load_dotenv()
    BUCKET = os.getenv("GCS_BUCKET_NAME")
    if not BUCKET:
        raise ValueError("GCS_BUCKET_NAME no definido en .env")

    # 3. Ejecución Dinámica con los argumentos recibidos
    ingestor = TaxiIngestor(bucket_name=BUCKET)
    
    try:
        logging.info(f"📅 Iniciando proceso para {args.year}-{args.month:02d}")
        
        raw_file = ingestor.download_data(args.year, args.month)
        processed_file = ingestor.validate_and_transform(raw_file)
        
        # Particionamiento Hive
        gcs_path = f"raw/yellow_tripdata/{args.year}/{args.month:02d}/data.parquet"
        
        ingestor.upload_to_gcs(processed_file, gcs_path)
        ingestor.clean_local(raw_file, processed_file)
        
    except Exception as e:
        logging.critical(f"💀 Fallo el proceso: {e}")
        exit(1)
```
Prueba local: Ahora tu script exige parámetros.

```bash
uv run src/ingestion/ingest_manager.py --year 2024 --month 2
```
Esto debería descargar Febrero 2024 y subirlo al bucket `nyc-taxi-lakehouse-raw-branko/raw/yellow_tripdata/2024/02/data.parquet` .

### 2. Creando la Receta (Dockerfile)
Un contenedor Docker es como una "caja virtual" que contiene tu código y todas sus dependencias (Python, librerías, sistema operativo base). Esto elimina el famoso problema de "en mi máquina funcionaba".

Crea un archivo llamado Dockerfile (sin extensión) en la raíz del proyecto:

```docker
# 1. Imagen Base: Usamos Python 3.10 versión "slim" (ligera y segura)
FROM python:3.10-slim

# 2. Configuración de entorno para evitar archivos basura (.pyc) y logs retenidos
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# 3. Instalamos dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalamos uv copiándolo de su imagen oficial (Patrón Best Practice)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 5. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 6. Copiamos las definiciones de dependencias PRIMERO
# Esto permite a Docker usar la caché. Si no cambias dependencias, este paso no se repite.
COPY pyproject.toml uv.lock ./

# 7. Instalamos las librerías en el sistema del contenedor
RUN uv pip install --system -r pyproject.toml

# 8. Copiamos el código fuente de nuestra aplicación
COPY src/ ./src/

# 9. Definimos el comando por defecto al iniciar
ENTRYPOINT ["python", "src/ingestion/ingest_manager.py"]
```


### 3. Build & Run (Construir y Ejecutar)

#### Ahora vamos a convertir esa receta en una imagen real y a ejecutarla.

A. Build (Construir la imagen)
Este comando lee el Dockerfile y crea una imagen llamada `nyc-taxi-ingestor`. El punto final `.` le dice a Docker "busca los archivos aquí".

```bash
docker build -t nyc-taxi-ingestor:v1 .
```

B. Run (Correr el contenedor)

Aquí está el truco. El contenedor es aislado: no tiene acceso a tus archivos, ni a tus credenciales de Google, ni a tu archivo `.env`. Tenemos que "inyectárselos".

- `v $(pwd)/gcp_credentials:/app/gcp_credentials`: (Volumen) Conecta tu carpeta de credenciales local con una carpeta dentro del contenedor. Es como conectar un USB virtual.

- `e VARIABLE=...`: (Environment) Le pasa las variables de entorno necesarias manualmente.

```bash
docker run --rm \
  --network host \
  -v $(pwd)/gcp_credentials:/app/gcp_credentials \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/gcp_credentials/terraform-key.json \
  -e GCS_BUCKET_NAME="nyc-taxi-lakehouse-raw-TU-NOMBRE" \
  nyc-taxi-ingestor:v1 \
  --year 2023 --month 5
```

Nota: Reemplaza `nyc-taxi-lakehouse-raw-TU-NOMBRE` con el nombre real de tu bucket si es diferente.

¿Qué debería pasar?

1. Docker arranca.
2. Python dentro de Docker ve el archivo JSON montado en `/app/gcp_credentials`.

3. Descarga Mayo 2023 `(2023-05)`.

4. Procesa y sube a GCS.

5. El contenedor se autodestruye (`--rm`) al terminar.


Resultado: Si ves los logs de descarga y subida exitosa, ¡felicidades! Tienes una aplicación de datos blindada, portable y lista para ser orquestada por Airflow.

# 🌪️ Fase 6: Orquestación con Apache Airflow

¡Bienvenido al corazón del Data Engineering! Ya tienes tu "robot" (Docker) que descarga datos, pero... ¿quién lo despierta? ¿Quién vigila que no falle? ¿Quién programa las ejecuciones automáticas?

## 🎯 ¿Qué es Apache Airflow?

**Apache Airflow** es un orquestador de tareas que te permite:
- ✅ Ejecutar procesos de forma automática
- ✅ Programar tareas recurrentes (diarias, mensuales, etc.)
- ✅ Monitorear ejecuciones y gestionar errores
- ✅ Visualizar flujos de trabajo

---

## 🤔 ¿Por qué NO instalarlo directamente?

En lugar de hacer `pip install apache-airflow`, usaremos **Docker Compose**. Déjame explicarte por qué.

### 🥊 Instalación Local vs Docker Compose

Imagina que quieres montar un restaurante (tu proyecto de datos).

### ❌ Opción A: Instalación Local (`pip install`)

Es como montar el restaurante **en la cocina de tu casa**.

**Problemas:**

1. **Conflicto de dependencias** 🔥
   - Airflow necesita más de 100 librerías específicas
   - Si tienes un proyecto con `pandas v2.0` y Airflow necesita `pandas v1.5`, habrá conflicto
   - Al instalar Airflow, sobrescribirá tus librerías y romperá otros proyectos

2. **Infraestructura incompleta** 🧩
   - Airflow necesita varios componentes:
     - Webserver (interfaz visual)
     - Scheduler (ejecutor de tareas)
     - Base de datos (PostgreSQL)
   - Con `pip install` solo instalas el código Python
   - Debes instalar y configurar PostgreSQL manualmente

3. **"En mi máquina funcionaba"** 💻
   - Si cambias de PC o colaboras con alguien, deberán repetir toda la instalación
   - Diferencias entre sistemas operativos causarán problemas

### ✅ Opción B: Docker Compose (La Opción Profesional)

Es como alquilar un **Food Truck totalmente equipado**.

**Ventajas:**

1. **Aislamiento total** 🎯
   - Cada contenedor tiene sus propias dependencias
   - Airflow puede usar `pandas v1.5` mientras tu máquina usa `pandas v2.0`
   - No hay conflictos entre proyectos

2. **Infraestructura completa** 📦
   - Un solo comando levanta:
     - PostgreSQL
     - Airflow Webserver
     - Airflow Scheduler
   - Todo conectado y configurado automáticamente

3. **Portabilidad** 🌍
   - El archivo `docker-compose.yaml` funciona igual en cualquier máquina
   - Comparte el archivo y cualquiera puede replicar tu entorno

4. **Limpieza** 🧹
   - ¿Terminaste el proyecto? → `docker compose down`
   - Tu máquina queda como nueva, sin archivos residuales

---

## 🛠️ Paso 1: Crear el archivo docker-compose.yaml

En la raíz de tu proyecto `nyc-taxi-lakehouse`, crea un archivo llamado **docker-compose.yaml**.

```yaml
x-airflow-common:
  &airflow-common
  # Usamos la imagen oficial extendida (la crearemos en breve) o la estándar
  # Por ahora usaremos la estándar, pero inyectando la librería de Docker
  image: apache/airflow:2.7.3
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth'
    # Esta variable instala el proveedor de Docker al arrancar (Truco para Dev)
    _PIP_ADDITIONAL_REQUIREMENTS: apache-airflow-providers-docker
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./gcp_credentials:/opt/airflow/gcp_credentials
    # 🔥 TRUCO SENIOR: Mapeamos el socket de Docker
    # Esto permite que Airflow (dentro de un contenedor) pueda crear HERMANOS contenedores
    - /var/run/docker.sock:/var/run/docker.sock
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    - postgres

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5
    restart: always

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    restart: always

  airflow-init:
    <<: *airflow-common
    command: version
    environment:
      <<: *airflow-common-env
      _PIP_ADDITIONAL_REQUIREMENTS: ''
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-admin}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-admin}
    user: "0:0"
    volumes:
      - .:/sources

volumes:
  postgres-db-volume:
```

---

## 📖 Entendiendo el archivo docker-compose.yaml

### 1️⃣ Bloque `x-airflow-common` (Configuración Base)

Este bloque define configuraciones reutilizables para evitar repetir código.

**Elementos clave:**

- **`_PIP_ADDITIONAL_REQUIREMENTS`**: Instala librerías adicionales al iniciar el contenedor
- **Volúmenes**:
  - `./dags:/opt/airflow/dags` → Sincroniza tus DAGs locales con Airflow
  - `./gcp_credentials` → Inyecta credenciales de Google Cloud
  - **`/var/run/docker.sock`** 🔥 → **Truco avanzado**: Permite que Airflow controle Docker desde dentro del contenedor (Docker out of Docker)

### 2️⃣ Servicios

**`postgres`** (La Memoria)
- Base de datos que almacena el historial de ejecuciones de Airflow
- Guarda qué tareas se ejecutaron, cuáles fallaron, etc.

**`airflow-scheduler`** (El Corazón)
- Monitorea los DAGs y decide cuándo ejecutar tareas
- Si este servicio falla, nada se ejecuta

**`airflow-webserver`** (La Interfaz)
- Interfaz gráfica en el puerto 8080
- Te permite visualizar y controlar tus flujos de trabajo

**`airflow-init`** (El Configurador)
- Se ejecuta una sola vez al inicio
- Prepara la base de datos y crea el usuario admin

---

## 🚀 Paso 2: Preparar el entorno

Antes de iniciar Airflow, necesitas crear las carpetas necesarias y configurar permisos.

### Crear directorios

```bash
mkdir -p logs plugins
```

### Configurar ID de usuario

Agrega esta línea a tu archivo `.env`:

```
AIRFLOW_UID=1000
```

> **Nota:** Esto evita errores de permisos. Puedes verificar tu UID con el comando `id -u`.

---

## 🚦 Paso 3: Iniciar Airflow

### 1. Inicializar la base de datos

```bash
docker compose up airflow-init
```

Espera hasta ver el mensaje **"User admin created"** y que termine con código 0.

### 2. Levantar todos los servicios

```bash
docker compose up -d
```

El flag `-d` ejecuta los contenedores en segundo plano.

---

## 🎉 Paso 4: Acceder a Airflow

Abre tu navegador y ve a: **http://localhost:8080**

**Credenciales:**
- **Usuario:** `admin`
- **Contraseña:** `admin`

Si ves la interfaz de Airflow, ¡felicidades! 🎊 Ya tienes tu orquestador listo para crear DAGs.

¡No olvides realizar un commit del avance!

---

## 📝 Resumen

✅ Configuraste Apache Airflow usando Docker Compose  
✅ Levantaste una infraestructura profesional con PostgreSQL, Scheduler y Webserver  
✅ Evitaste conflictos de dependencias y problemas de configuración  
✅ Ahora puedes orquestar tus pipelines de datos de forma automatizada  

**Próximo paso:** Crear tu primer DAG para ejecutar el contenedor de ingestión automáticamente.


## 🌪️ Fase 7: Tu Primer DAG 

Ahora crearemos el DAG (Directed Acyclic Graph) que le dirá a Airflow cómo ejecutar nuestro contenedor de ingestión.

**Reto Técnico:** Airflow corre dentro de Docker. Para que pueda lanzar *otro* contenedor (nuestro script), necesitamos configurar **Docker out of Docker (DooD)** y gestionar correctamente los permisos y variables de entorno.

### 1. Configuración de Permisos (WSL/Linux)

Airflow necesita comunicarse con el "cerebro" de Docker (`docker.sock`) de tu máquina anfitriona. Por defecto, este archivo solo lo puede usar `root`. Necesitamos abrir los permisos para que el usuario `airflow` no sea rechazado.

Ejecuta este comando en tu terminal (WSL):

```bash
sudo chmod 666 /var/run/docker.sock
```

#### ⚠️ Nota: Este comando permite que cualquier usuario en tu máquina controle Docker. Es estándar para entornos de desarrollo local, pero requiere precaución en servidores productivos compartidos.
---

### 3. El Código del DAG (`dags/ingest_dag.py`)
Crea este archivo en la carpeta `dags/`. Este código:

1. Obtiene la ruta absoluta de tu proyecto (necesario para montar volúmenes).

2. Lee el nombre del Bucket desde el `.env`.

3. Usa `DockerOperator` para lanzar el contenedor de ingestión de forma efímera.

IMPORTANTE: Antes de guardar, ejecuta `pwd` en tu terminal y actualiza la variable `PROJECT_PATH` en el código

```python

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
import os 

# --- CONFIGURACIÓN ---
# Aqui deberías pegar el resultaltado obtenido luego de ejecutar pwd en la raiz de tu proyecto
PROJECT_PATH = "/home/TU_USUARIO/projects/nyc-taxi-lakehouse" 

# 👇 LEEMOS LA CONFIGURACIÓN DEL ENTORNO
# Si no encuentra la variable, lanzamos error para fallar rápido (Fail Fast)
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
if not BUCKET_NAME:
    raise ValueError("❌ Error Crítico: GCS_BUCKET_NAME no está definido en el entorno de Airflow.")

default_args = {
    'owner': 'branko',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'nyc_taxi_ingestion_v1',
    default_args=default_args,
    description='Ingestión mensual de datos de NYC Taxi usando Docker',
    schedule_interval='@monthly', # Ejecutar una vez al mes
    start_date=datetime(2023, 1, 1),
    catchup=False, # No intentar ejecutar meses pasados automáticamente al inicio
    tags=['ingestion', 'docker', 'nyc-lakehouse'],
) as dag:

    # Tarea: Ingestión de Junio 2024 (Hardcodeada por ahora para probar)
    ingest_task = DockerOperator(
        task_id='ingest_jun_2024',
        image='nyc-taxi-ingestor:v1', # La imagen que construiste
        api_version='auto',
        auto_remove=True, # Borrar contenedor al terminar
        
        # El comando que ejecutará dentro del contenedor
        # Airflow pasará esto al ENTRYPOINT
        command="--year 2024 --month 6",
        
        # Configuración de red para salir a internet
        network_mode="host", 
        
        # Montaje de volúmenes (Mapeo de Host -> Contenedor)
        mounts=[
            # Montamos las credenciales para que el script pueda leerlas
            Mount(
                source=f"{PROJECT_PATH}/gcp_credentials", 
                target="/app/gcp_credentials", 
                type="bind"
            )
        ],
        environment={
            # Ruta interna en el contenedor (Fija porque depende del mount target)
            'GOOGLE_APPLICATION_CREDENTIALS': '/app/gcp_credentials/terraform-key.json',
            'GCS_BUCKET_NAME': BUCKET_NAME 
        },
        docker_url="unix://var/run/docker.sock",
    )

    ingest_task
```

### 4. Ejecución y Verificación

1. Ve a http://localhost:8080.

2. Busca el DAG nyc_taxi_ingestion_v1.

3. Actívalo (Toggle ON) y haz clic en el botón Play (Trigger DAG).

4. Entra en la vista de Graph, haz clic en la tarea y selecciona Logs.

---

Si ves la tarea en **verde oscuro (Success)** en la interfaz de Airflow y confirmas que el archivo nuevo apareció en tu Google Cloud Storage, **¡has desbloqueado un logro nivel Senior!** 🏆

Acabas de implementar con éxito una de las arquitecturas más complejas de orquestación local: **Docker-out-of-Docker (DooD)**.

### 📝 Resumen de Hitos
✅ **Infraestructura Avanzada:** Configuraste permisos de socket para permitir que Airflow controle el motor Docker del host.

✅ **12-Factor App:** Desacoplaste la configuración (variables de entorno) del código, haciendo tu DAG portable y seguro.

✅ **Automatización Real:** Tienes un pipeline que descarga, procesa y sube datos a la nube sin intervención humana.

**Próximo paso:** Ahora que los datos están "crudos" en el Data Lake (GCS), necesitamos hacerlos consultables. En la siguiente fase, conectaremos **BigQuery** para leer estos archivos mediante Tablas Externas.

**No te olvides de guardar tus avances:**

```bash

git add .
git commit -m "feat: add airflow dag with docker operator"
git push origin main

```



