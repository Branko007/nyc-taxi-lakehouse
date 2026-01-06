# 📘 Guía Maestra: Construyendo un Data Lakehouse con GCP & Python

¡Bienvenido/a! Estás a punto de construir una plataforma de datos profesional. Esta guía no es solo un recetario de comandos; es un recorrido diseñado para que **entiendas** cada decisión arquitectónica.

En este proyecto, trabajaremos con el dataset público de **NYC Taxi & Limousine Commission (TLC)**. Estos datos contienen millones de registros sobre viajes en taxi en la ciudad de Nueva York, incluyendo horarios, ubicaciones de inicio/fin, distancias y tarifas, lo que nos proporciona el escenario perfecto para simular un flujo de Big Data real.

Utilizaremos un stack moderno y robusto, integrando las herramientas líderes del mercado para cubrir cada etapa del ciclo de vida del dato:

*   ☁️ **Google Cloud Platform (GCP)**: Nuestro ecosistema en la nube donde residirá toda la solución.
*   🏗️ **Terraform**: Para implementar **Infraestructura como Código (IaC)**, permitiéndonos crear y destruir recursos (servidores, bases de datos) de forma automática y profesional.
*   🪣 **Cloud Storage (Buckets)**: Funcionará como nuestro **Data Lake**, el lugar donde almacenaremos los datos crudos (Raw) de forma económica y masiva.
*   🐍 **Python & Polars**: El motor de procesamiento. Usaremos Polars por su velocidad extrema para transformar datos antes de moverlos.
*   🐳 **Docker**: Para "contenerizar" nuestro código, asegurando que lo que funciona en tu computadora funcione exactamente igual en la nube, sin conflictos de dependencias.
*   ⚙️ **Apache Airflow**: El director de orquesta que programará y vigilará que cada paso de nuestra tubería de datos (pipeline) se ejecute en el orden correcto.
*   🔍 **BigQuery**: Nuestro **Data Warehouse** de alto rendimiento, donde realizaremos análisis complejos a gran escala usando SQL.
*   🛠️ **dbt (data build tool)**: Para transformar los datos dentro de BigQuery, aplicando ingeniería de software (tests, documentación y control de versiones) a nuestras consultas SQL.
*  📦 **GIT**: Para controlar versiones y colaborar con otros desarrolladores.
---

## 🎯 Objetivo del Proyecto

Simularemos un entorno de producción real para una empresa de taxis (NYC Taxi).
**Tu misión:** Crear un sistema automatizado que ingeste, procese y almacene datos masivos de viajes, permitiendo análisis rápidos y eficientes.

### 🧠 ¿Qué habilidades dominarás?

Al finalizar este proyecto, no solo habrás configurado herramientas; habrás desarrollado una mentalidad de **Data Engineer** sólida basada en principios de ingeniería de software:

*   **Pensamiento de Infraestructura (IaC)**: Dejarás de configurar recursos manualmente para definir tu arquitectura mediante código, permitiendo que sea reproducible, versionable y libre de errores humanos.
*   **Diseño de Arquitecturas Híbridas**: Entenderás la sinergia entre un **Data Lake** (almacenamiento masivo y económico) y un **Data Warehouse** (análisis de alto rendimiento), aprendiendo a mover datos entre ellos de forma eficiente.
*   **Ingeniería de Datos de Alto Rendimiento**: Dominarás el procesamiento de datos moderno con **Polars**, aprendiendo a manipular millones de filas en segundos optimizando el uso de memoria y CPU.
*   **Calidad y Gobernanza de Datos**: Aplicarás estándares de desarrollo (tests, documentación y linaje) a tus modelos de SQL mediante **dbt**, transformando consultas simples en activos de datos confiables para el negocio.
*   **Resiliencia y Orquestación**: Aprenderás a encapsular lógica en **Docker** para eliminar el "en mi máquina funciona" y a delegar la ejecución en **Airflow**, garantizando que tus procesos se recuperen automáticamente ante fallos.

* **Idempotencia**: Aprenderás a hacer que tus procesos sean idempotentes, es decir, que puedan ser ejecutados múltiples veces sin causar efectos secundarios.

---

## 📋 Prerrequisitos

Antes de empezar, necesitamos preparar tu "caja de herramientas". Asegúrate de tener esto instalado en tu entorno (WSL2, Linux o macOS):

*   **Git**: Para guardar tu progreso y versionar el código.
*   **Google Cloud CLI (`gcloud`)**: El "control remoto" de GCP desde tu terminal.
*   **Terraform**: El albañil que construirá tu infraestructura.
*   **Python 3.10**: El cerebro de nuestra lógica.
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
# 1. Inicializar el gestor de paquetes desde la raíz del proyecto
uv init

# 2. Crear un entorno virtual aislado (.venv)
# Esto evita que las librerías de este proyecto choquen con otros.
uv venv

# 3. Activar el entorno
# En Linux/macOS/WSL:
source .venv/bin/activate
# En Windows (PowerShell):
# .venv\Scripts\activate

# 4. Agregar las librerías al proyecto
# Esto las instala y las registra en pyproject.toml automáticamente
uv add "requests>=2.32.5" "polars>=1.35.2" "google-cloud-storage>=3.6.0" "python-dotenv>=1.2.1" "pyarrow>=22.0.0"
```

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
      source  = "hashicorp/google" # Origen del proveedor oficial de GCP
      version = "4.51.0" # Se fija la versión para garantizar estabilidad y evitar cambios inesperados
    }
  }
}

provider "google" {
  credentials = file("../../gcp_credentials/terraform-key.json") # Ruta a tu key
  project     = var.project_id # ID del proyecto de GCP
  region      = var.region # Región de GCP
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
  default     = "nyc_taxi_bronze"
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

### 🏁 Parada Técnica: ¿Qué acabas de lograr?

Acabas de cruzar la frontera de "usuario de consola" a "ingeniero de nube". 

*   **¿Qué?**: Levantaste un **Data Lake** (GCS) para guardar archivos y un **Data Warehouse** (BigQuery) para analítica.
*   **¿Cómo?**: Usando **Infraestructura como Código (IaC)**. Terraform leyó tus archivos `.tf` y se encargó de hablar con la API de Google por ti.
*   **¿Por qué?**: Porque en el mundo real no configuramos nubes a mano. Queremos código que sea **reproducible**, **auditable** y fácil de recrear sin errores humanos.

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

### Preparación del Entorno

Como ya agregamos las librerías necesarias en la **Fase 1**, nuestro entorno ya está listo para importar `polars`, `requests` y el resto de herramientas. No es necesario volver a instalarlas.

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

### 🏁 Parada Técnica: ¿Qué acabas de lograr?

En esta etapa, hemos pasado de un script básico a una **tubería de datos de grado productivo**. Aquí está el desglose de nuestra arquitectura:

*   **¿Qué hicimos?**: Creamos un orquestador de ingesta que automatiza el ciclo de vida del dato: descarga -> limpieza/tipado -> almacenamiento en la nube -> limpieza local.
*   **¿Cómo lo hicimos?**:
    *   **Polars**: Para procesar datos en memoria de forma ultra rápida y exportar a **Parquet** (el estándar de oro en Big Data).
    *   **Google Cloud Storage (GCS)**: Como nuestra capa de *Landing Zone* o *Bronze*, donde los datos viven de forma duradera.
    *   **Logging & Error Handling**: Implementamos un sistema de rastreo para que, si algo falla a las 3 AM, sepamos exactamente por qué sin adivinar.
*   **¿Por qué así?**: Porque la escalabilidad no se trata solo de manejar más datos, sino de manejar la **complejidad**. Al separar las responsabilidades y usar formatos columnares (Parquet), estamos preparando el terreno para que BigQuery analice terabytes en segundos.

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
Esto debería descargar Febrero 2024 y subirlo al bucket `nyc-taxi-lakehouse-raw-tunombre/raw/yellow_tripdata/2024/02/data.parquet` .

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

- `-e GCS_BUCKET_NAME=...`: (Environment) Inyecta las variables de entorno necesarias (como el nombre del bucket) para que el script las reconozca dentro del contenedor.

```bash
docker run --rm \
  --network host \
  -v $(pwd)/gcp_credentials:/app/gcp_credentials \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/gcp_credentials/terraform-key.json \
  -e GCS_BUCKET_NAME="nyc-taxi-lakehouse-raw-tunombre" \
  nyc-taxi-ingestor:v1 \
  --year 2023 --month 5
```

Nota: Reemplaza `nyc-taxi-lakehouse-raw-tunombre` con el nombre real de tu bucket si es diferente.

¿Qué debería pasar?

1. Docker arranca.
2. Python dentro de Docker ve el archivo JSON montado en `/app/gcp_credentials`.

3. Descarga Mayo 2023 `(2023-05)`.

4. Procesa y sube a GCS.

5. El contenedor se autodestruye (`--rm`) al terminar.


Resultado: Si ves los logs de descarga y subida exitosa, ¡felicidades! Tienes una aplicación de datos blindada, portable y lista para ser orquestada por Airflow.
### 🏁 Parada Técnica: De Script a Producto (Dockerización)

En esta etapa, hemos transformado un script de automatización en una **aplicación profesional lista para la nube**. Analicemos los pilares de este cambio:

*   **¿Qué logramos?**: Pasamos de un código estático a una **herramienta CLI (Command Line Interface)**. Ahora el script no está "atado" a una configuración fija; es dinámico y puede procesar cualquier mes o año mediante parámetros.
*   **¿Cómo lo hicimos?**:
    *   **Argparse**: Implementamos una interfaz que permite al script recibir instrucciones externas, facilitando su integración con otros sistemas.
    *   **Dockerfile**: Creamos una "receta" que garantiza que el código tenga exactamente las mismas librerías y versión de Python, sin importar si corre en Windows, Mac o Linux.
    *   **Volúmenes y Variables**: Aprendimos a inyectar secretos (credenciales) y configuraciones sin dejar rastro dentro de la imagen, siguiendo las mejores prácticas de seguridad.
*   **¿Por qué es vital?**: Porque en el mundo real, los datos no se procesan en tu laptop. Al dockerizar, tu tubería es **portátil y escalable**. Está lista para ser lanzada en un servidor remoto, en Kubernetes o, como veremos a continuación, ser controlada por un orquestador.

**En resumen:** Has blindado tu código. Ya no es solo un script; es un componente de software robusto y aislado. 

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
    AIRFLOW__WEBSERVER__SECRET_KEY: 'this_is_a_very_secret_key_for_dev_only'
    # Esta variable instala el proveedor de Docker al arrancar (Truco para Dev)
    _PIP_ADDITIONAL_REQUIREMENTS: apache-airflow-providers-docker
    # Pasamos la ruta del host para que el DockerOperator sepa dónde están los archivos
    AIRFLOW_PROJ_DIR: ${AIRFLOW_PROJ_DIR}
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./gcp_credentials:/opt/airflow/gcp_credentials
    # Mapeamos el socket de Docker
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
# ⚠️ RUTA ABSOLUTA de tu proyecto en el HOST (ej: /home/branko/nyc-taxi-lakehouse)
# Esto es vital para que los mounts de Docker funcionen correctamente.
AIRFLOW_PROJ_DIR=/home/TU_USUARIO/projects/nyc-taxi-lakehouse
```

> [!IMPORTANT]
> **Nota: El misterio de las rutas en Docker-out-of-Docker (DooD)**
>
> ¿Por qué no podemos usar rutas relativas o `os.path.abspath`?
> 1. **Cajas dentro de cajas**: Airflow corre dentro de un contenedor. Si le pedimos a Python su ruta, dirá `/opt/airflow`.
> 2. **El Motor Real**: Airflow no lanza contenedores "dentro" de sí mismo, sino que le pide al Docker de tu máquina real (el Host) que los lance.
> 3. **El Mount**: Cuando montamos un volumen, el motor de Docker busca la ruta en **tu máquina real**. Si le pasamos `/opt/airflow`, Docker fallará porque esa carpeta no existe en tu Windows/WSL, solo existe dentro de Airflow.
>
> Al definir `AIRFLOW_PROJ_DIR`, le damos a Airflow la "dirección real" de tu casa para que pueda invitar a otros contenedores a pasar.

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
    'owner': 'airflow',
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

Si ves la tarea en **verde oscuro (Success)** en la interfaz de Airflow y confirmas que el archivo nuevo apareció en tu Google Cloud Storage, **¡has desbloqueado un nuevo logro!** 🏆

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


---

## 🏗️ Fase 8: El Puente al Lakehouse (BigQuery External Tables)

En esta fase, conectamos nuestro Data Lake (GCS) con nuestro Data Warehouse (BigQuery). Lo haremos sin mover los archivos, usando **Tablas Externas**. Esto es lo que define un **Data Lakehouse**: la potencia analítica de SQL sobre la flexibilidad de un almacenamiento de objetos.

### 1. Definir la Nomenclatura de los Datasets
Como Data Engineer, buscamos que los nombres sean intuitivos. Cambiaremos el dataset genérico por nombres que reflejen la **Arquitectura Medallion**:
- `nyc_taxi_bronze`: Donde viven los datos crudos.
- `nyc_taxi_silver`: Donde viven los datos limpios.

### 2. Actualizar la Infraestructura (`infrastructure/terraform/main.tf`)

Añadimos el dataset para la capa Silver y la tabla externa que servirá de puente:

```hcl
# Dataset para la Capa Silver (Datos Limpios)
resource "google_bigquery_dataset" "silver_dataset" {
  dataset_id                 = "nyc_taxi_silver"
  friendly_name              = "NYC Taxi DWH - Silver"
  description                = "Capa Silver: Datos limpios y deduplicados"
  location                   = var.region
  delete_contents_on_destroy = true
}

# Tabla Externa: El "espejo" de nuestros archivos Parquet
resource "google_bigquery_table" "external_yellow_taxi" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "external_yellow_taxi"
  description = "Tabla externa que apunta a los datos crudos en GCS"
  deletion_protection = false

  external_data_configuration {
    autodetect    = true
    source_format = "PARQUET"
    # El comodín * permite leer todos los archivos .parquet en la carpeta
    source_uris   = ["gs://${var.gcs_bucket_name}/raw/yellow_tripdata/*.parquet"]
  }
}
```

Luego ejecuta `terraform apply` para crear estos nuevos recursos.

---
### Zero-Copy Ingestion

Es probable que te preguntes: *¿En qué momento ejecutamos el comando para cargar los datos a BigQuery?* La respuesta es: **Nunca**.

Gracias a las **Tablas Externas**, hemos implementado **Zero-Copy Ingestion**. Esto cambia las reglas del juego:

*   **💰 Almacenamiento (Costo $0 en BigQuery):** Si revisas los detalles de la tabla `external_yellow_taxi` en la consola de Google Cloud, verás que su tamaño es `0 bytes`. Esto es porque los datos físicamente residen en el Bucket de GCS. BigQuery solo actúa como una "capa de lectura" inteligente. Estás pagando el precio de almacenamiento de GCS (mucho más barato) pero con la potencia de BigQuery.
*   **⚡ Publicación Instantánea:** En cuanto tu script de Python termina de subir un archivo `.parquet` al bucket, los datos están disponibles para ser consultados por SQL. No hay procesos de carga (*Load Jobs*) que esperar ni fallos de ingesta por falta de espacio.
*   **🚀 Rendimiento:** Aunque las tablas externas son ligeramente más lentas que las tablas nativas de BigQuery, al usar el formato **Parquet** (que es columnar), BigQuery solo lee las columnas necesarias de los archivos en GCS. Esto optimiza drásticamente el rendimiento y reduce los costos de consulta.
*   **🏗️ Arquitectura Desacoplada:** Esta es la esencia de un **Data Lakehouse**. Puedes tener a tus ingenieros de datos subiendo archivos a GCS y, al mismo tiempo, a tus analistas consultando esos mismos archivos vía SQL en BigQuery, sin que un proceso bloquee al otro.

**En resumen:** La capa **Bronze** no es una base de datos física, es un "espejo" de tu Data Lake.

## 🛠️ Fase 9: Transformación Profesional con dbt

dbt (Data Build Tool) es el estándar de la industria para transformar datos. No solo escribe SQL, sino que añade **ingeniería** al proceso: control de versiones, pruebas y documentación.

### 1. Configuración del Proyecto (`dbt_project.yml` & `profiles.yml`)
Para que dbt funcione, necesita saber dos cosas: qué modelos ejecutar y cómo conectarse a la base de datos.

**`dbt_project.yml`**: Es el cerebro del proyecto. Aquí definimos dónde están los modelos y en qué datasets (schemas) deben guardarse.
```yaml
name: 'nyc_taxi_transform'
version: '1.0.0'
config-version: 2
profile: 'nyc_taxi_profile'

models:
  nyc_taxi_transform:
    staging:
      +schema: nyc_taxi_bronze
      +materialized: view
    silver:
      +schema: nyc_taxi_silver
      +materialized: incremental
```
**¿Qué significan estas líneas clave?**

*   **name**: El identificador único de tu proyecto dbt.
*   **profile**: Vincula este proyecto con el perfil de conexión que definiremos en `profiles.yml`.
*   **models**: Define la jerarquía de transformación y su **materialización**:
    *   **`view` (Vista)**: Es una tabla virtual que no almacena datos físicamente. Cada vez que la consultas, BigQuery ejecuta el SQL subyacente. Es ideal para la capa **Staging** porque garantiza que siempre veas los datos más frescos sin incurrir en costos de almacenamiento adicionales.
    *   **`incremental`**: Es una tabla física que solo procesa e inserta los registros nuevos desde la última ejecución. En lugar de reconstruir millones de filas cada vez (lo cual sería lento y costoso), dbt solo añade el "delta" de datos. Es la estrategia recomendada para la capa **Silver** para optimizar el rendimiento y el presupuesto de la nube.
---

**`profiles.yml`**: Contiene las credenciales técnicas. **Nota:** Usamos una ruta relativa para el `keyfile` para que funcione tanto en local como en Docker.

```yaml
nyc_taxi_profile:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: TU_PROJECT_ID_REAL
      dataset: nyc_taxi_bronze
      threads: 4
      keyfile: ../gcp_credentials/terraform-key.json
      location: us-central1
```

**Desglose de la configuración:**

*   **`type: bigquery`**: Especifica que el motor de base de datos es Google BigQuery.
*   **`method: service-account`**: Define el uso de una cuenta de servicio para la autenticación.
*   **`project`**: El ID de tu proyecto en Google Cloud Platform.
*   **`dataset`**: El dataset base para las operaciones de dbt.
*   **`threads`**: Número de hilos para ejecutar modelos en paralelo.
*   **`keyfile`**: Ruta relativa al archivo JSON de credenciales.
*   **`location`**: Región de GCP donde se procesarán los datos.

### 2. Limpieza de Nombres (Macros)
Por defecto, dbt añade prefijos a los nombres de los datasets. Para evitar esto y tener nombres limpios, creamos una macro en `dbt_project/macros/generate_schema_name.sql`:

```sql
-- Esta macro sobreescribe el comportamiento por defecto de dbt
-- para que use exactamente el nombre de esquema que definamos.
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

### 3. Capa de Staging (Bronze) con Tipado Explícito
En `models/staging/stg_yellow_tripdata.sql`, normalizamos los nombres a `snake_case` y forzamos los tipos de datos. **Nunca confíes en la autodetección para producción.**

```sql
{{ config(materialized='view') }}

SELECT
    -- Identificadores (Normalizados a snake_case)
    CAST(VendorID AS INT64) as vendor_id,
    CAST(RatecodeID AS INT64) as rate_code_id,
    CAST(PULocationID AS INT64) as pu_location_id,
    CAST(DOLocationID AS INT64) as do_location_id,

    -- Fechas (Convertidas de nanosegundos a Timestamp)
    TIMESTAMP_MICROS(CAST(tpep_pickup_datetime / 1000 AS INT64)) as pickup_datetime,
    TIMESTAMP_MICROS(CAST(tpep_dropoff_datetime / 1000 AS INT64)) as dropoff_datetime,

    -- Detalles del viaje
    CAST(passenger_count AS INT64) as passenger_count,
    CAST(trip_distance AS FLOAT64) as trip_distance,
    CAST(store_and_fwd_flag AS STRING) as store_and_fwd_flag,

    -- Pagos y montos (Explícitamente FLOAT64 para evitar errores de precisión)
    CAST(payment_type AS INT64) as payment_type,
    CAST(fare_amount AS FLOAT64) as fare_amount,
    CAST(extra AS FLOAT64) as extra,
    CAST(mta_tax AS FLOAT64) as mta_tax,
    CAST(tip_amount AS FLOAT64) as tip_amount,
    CAST(tolls_amount AS FLOAT64) as tolls_amount,
    CAST(improvement_surcharge AS FLOAT64) as improvement_surcharge,
    CAST(total_amount AS FLOAT64) as total_amount,
    CAST(congestion_surcharge AS FLOAT64) as congestion_surcharge,
    CAST(Airport_fee AS FLOAT64) as airport_fee,

    -- Auditoría
    CAST(ingestion_timestamp AS TIMESTAMP) as ingestion_timestamp
FROM {{ source('raw_data', 'external_yellow_taxi') }}
```

### 4. Capa Silver: Deduplicación Incremental
En `models/silver/silver_yellow_tripdata.sql`, aplicamos la lógica de negocio. Usamos `incremental` para no procesar toda la tabla cada vez, ahorrando costos.

```sql
{{ config(
    materialized='incremental',
    unique_key=['vendor_id', 'pickup_datetime', 'dropoff_datetime', 'pu_location_id', 'do_location_id'],
    incremental_strategy='merge'
) }}

WITH deduplicated AS (
    SELECT
        *,
        -- Nos quedamos con el registro más reciente si hay duplicados
        ROW_NUMBER() OVER (
            PARTITION BY vendor_id, pickup_datetime, dropoff_datetime, pu_location_id, do_location_id
            ORDER BY ingestion_timestamp DESC
        ) as row_num
    FROM {{ ref('stg_yellow_tripdata') }}
    WHERE trip_distance > 0 
      AND fare_amount > 0
      AND pickup_datetime < CURRENT_TIMESTAMP()
)

SELECT
    * EXCEPT(row_num)
FROM deduplicated
WHERE row_num = 1
```

---

## 🤖 Fase 10: Automatización y Calidad

Un pipeline que requiere ejecución manual no es un pipeline. Vamos a cerrar el círculo automatizando dbt dentro de Airflow.

### 1. Dockerfile para dbt (`Dockerfile.dbt`)
Creamos una imagen ligera que solo contiene dbt, pero usando `uv` para mantener la consistencia y velocidad:

```dockerfile
FROM python:3.10-slim
# Instalamos uv desde su imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Configuramos uv para que instale en el Python del sistema del contenedor
ENV UV_SYSTEM_PYTHON=1

RUN apt-get update && apt-get install -y --no-install-recommends git
RUN uv pip install dbt-bigquery

WORKDIR /usr/app/dbt_project
ENTRYPOINT ["dbt"]
```

> **💡 Nota: ¿Por qué usar `uv` dentro de Docker?**
> Aunque podríamos usar `pip`, usamos `uv` por tres razones:
> 1. **Consistencia**: Todo el proyecto usa `uv`, el Dockerfile no debe ser la excepción.
> 2. **Velocidad**: `uv` reduce el tiempo de construcción de la imagen significativamente.
> 3. **Determinismo**: Nos asegura que las dependencias se resuelvan de la misma forma que en tu máquina local.

### 2. El DAG Final (`dags/ingest_dag.py`)
Ahora conectamos las piezas. La tarea de transformación depende de que la ingesta termine con éxito.

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
import os 

# --- CONFIGURACIÓN ---
# ⚠️ IMPORTANTE (DooD): En Docker-out-of-Docker, el 'source' de un Mount debe ser la ruta EN EL HOST.
PROJECT_PATH = os.getenv("AIRFLOW_PROJ_DIR", "/home/TU_USUARIO/projects/nyc-taxi-lakehouse")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'nyc_taxi_ingestion_v1',
    default_args=default_args,
    start_date=datetime(2024, 1, 1), # Evitamos el mes actual para no tener errores de datos no publicados
    schedule_interval='@monthly',
    catchup=False,
) as dag:

    ingest_task = DockerOperator(
        task_id='ingest_data',
        image='nyc-taxi-ingestor:v1',
        command="--year {{ execution_date.year }} --month {{ execution_date.month }}",
        network_mode="host", 
        mounts=[
            Mount(source=f"{PROJECT_PATH}/gcp_credentials", target="/app/gcp_credentials", type="bind")
        ],
        environment={
            'GOOGLE_APPLICATION_CREDENTIALS': '/app/gcp_credentials/terraform-key.json',
            'GCS_BUCKET_NAME': BUCKET_NAME 
        },
        docker_url="unix://var/run/docker.sock",
    )

    transform_task = DockerOperator(
        task_id='dbt_run',
        image='nyc-taxi-dbt:v1',
        command="run --profiles-dir .",
        network_mode="host",
        mounts=[
            Mount(source=f"{PROJECT_PATH}/dbt_project", target="/usr/app/dbt_project", type="bind"),
            Mount(source=f"{PROJECT_PATH}/gcp_credentials", target="/usr/app/gcp_credentials", type="bind")
        ],
        docker_url="unix://var/run/docker.sock",
    )

    test_task = DockerOperator(
        task_id='dbt_test',
        image='nyc-taxi-dbt:v1',
        command="test --profiles-dir .",
        network_mode="host",
        mounts=[
            Mount(source=f"{PROJECT_PATH}/dbt_project", target="/usr/app/dbt_project", type="bind"),
            Mount(source=f"{PROJECT_PATH}/gcp_credentials", target="/usr/app/gcp_credentials", type="bind")
        ],
        docker_url="unix://var/run/docker.sock",
    )

    ingest_task >> transform_task >> test_task
```

---

## ⚠️ Fase 14: El Problema del "Futuro" y Errores 403/404

Si ejecutas el DAG para el mes actual, es muy probable que veas un error **403 Forbidden** o **404 Not Found**.

### ¿Por qué sucede esto?
Los datos de NYC TLC (Taxi & Limousine Commission) no se publican en tiempo real. Suelen tener un retraso de **2 a 3 meses**. Por lo tanto, si hoy es Diciembre de 2025, el archivo `yellow_tripdata_2025-12.parquet` aún no existe en sus servidores.

### Cómo probar con datos reales
Para verificar que tu pipeline funciona de principio a fin, debes hacer un **Backfill** (ejecución hacia atrás) para un mes que sí tenga datos, como **Enero de 2024**.

#### Opción A: Desde la Terminal (Recomendado)
Ejecuta este comando para forzar la ejecución de un mes pasado:
```bash
docker compose exec airflow-scheduler airflow dags backfill \
    --start-date 2024-01-01 \
    --end-date 2024-01-01 \
    nyc_taxi_ingestion_v1
```

#### Opción B: Desde la Interfaz de Airflow
1. Activa el DAG (interruptor azul).
2. Haz clic en el nombre del DAG.
3. En la vista de **Grid**, busca una ejecución pasada o usa **"Trigger DAG w/ config"** y ajusta la fecha si tu versión lo permite.
4. Si una tarea falló por fecha, puedes darle a **"Clear"** en una ejecución de 2024 para que vuelva a intentarlo con esa fecha.

---

### 3. Limpieza de Deuda Técnica
Como Senior, no dejamos basura. Eliminamos archivos `.log` y tablas temporales de prueba (`check_types`). Un repositorio limpio es un repositorio confiable.

---

## 🔐 Fase 11: Infraestructura Profesional (Remote Backend)

Como Senior, no podemos permitir que la "memoria" de nuestra infraestructura viva solo en nuestra computadora. Vamos a configurar un **Remote Backend** en GCS para que el estado de Terraform sea seguro, compartido y persistente.

### 1. ¿Por qué un Backend Remoto?
- **Seguridad**: El archivo `.tfstate` puede contener secretos. En la nube está cifrado.
- **Persistencia**: Si borras tu carpeta local, no pierdes el control de tu infraestructura.
- **Colaboración**: Permite que varios ingenieros trabajen en el mismo proyecto sin pisarse.

### 2. Configuración en `provider.tf`
Añadimos el bloque `backend` dentro de `terraform {}`:

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
  # El estado ahora se guarda en la nube
  backend "gcs" {
    bucket  = "nyc-taxi-lakehouse-terraform-state-branko007"
    prefix  = "terraform/state"
  }
}
```

### 3. Migración del Estado
Para mover tu estado local a la nube, ejecuta:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=../../gcp_credentials/terraform-key.json
terraform init -migrate-state
```

Una vez completado, puedes borrar los archivos `terraform.tfstate` y `terraform.tfstate.backup` de tu carpeta local. ¡Tu infraestructura ahora es profesional!

---

---

## 🏆 Fase 12: La Capa Gold (Valor de Negocio)

La capa Gold es donde los datos se transforman en respuestas para el negocio. Aquí no guardamos datos crudos, sino **reportes agregados** listos para ser consumidos por herramientas de BI (como Looker o Tableau).

### 1. ¿Qué es una Materialización? (Concepto Senior)
Antes de crear los modelos, debes entender cómo dbt guarda los datos en BigQuery:

| Tipo | Qué hace | Cuándo usarlo |
| :--- | :--- | :--- |
| **View** | Es una consulta guardada (virtual). No ocupa espacio. | Datos pequeños o que cambian mucho. |
| **Table** | Crea una tabla física con los datos. | Reportes finales donde la velocidad es clave. |
| **Incremental** | Solo añade los datos nuevos a una tabla existente. | Tablas gigantes (como nuestra capa Silver). |

> [!TIP]
> En la capa Gold usaremos `materialized='table'` para que los analistas tengan respuestas instantáneas.

### 2. Configuración de la Capa Gold
Actualizamos nuestro `dbt_project.yml` para incluir la nueva capa:

```yaml
models:
  nyc_taxi_transform:
    # ... (staging y silver)
    gold:
      +schema: nyc_taxi_gold
      +materialized: table
```

### 3. Modelo: Ingresos Mensuales (`gold_monthly_revenue.sql`)
Este modelo agrupa millones de viajes en unas pocas filas de resumen mensual:

```sql
{{ config(materialized='table') }}

SELECT
    vendor_id,
    EXTRACT(YEAR FROM pickup_datetime) as year,
    EXTRACT(MONTH FROM pickup_datetime) as month,
    SUM(fare_amount) as total_fare,
    SUM(tip_amount) as total_tips,
    SUM(total_amount) as total_revenue,
    COUNT(*) as total_trips
FROM {{ ref('silver_yellow_tripdata') }}
GROUP BY 1, 2, 3
```

---

## 🧪 Fase 13: Calidad de Datos (dbt Tests)

Un Data Engineer Senior nunca entrega datos sin probarlos. dbt nos permite automatizar pruebas de calidad.

### 1. Pruebas Genéricas (`schema.yml`)
Creamos un archivo de configuración para definir qué esperamos de nuestros datos:

```yaml
version: 2
models:
  - name: gold_monthly_revenue
    columns:
      - name: vendor_id
        tests:
          - not_null  # El ID no puede estar vacío
      - name: total_revenue
        tests:
          - not_null
```

### 2. Ejecución de Pruebas
Para validar que todo es correcto, ejecutamos manualmente:

```bash
dbt test
```

**¡Automatización Senior!** 🚀
Como habrás notado en la Fase 10, hemos integrado `dbt test` directamente en nuestro DAG de Airflow. Esto significa que si los datos no pasan las pruebas de calidad, el pipeline se detendrá y no llegará a los reportes finales, evitando que el negocio tome decisiones basadas en datos erróneos.

---

## 🕵️ Fase 15: El Desafío de los "Datos Sucios" (Real World Data)

Si exploras tus tablas Gold, notarás algo extraño: aunque procesamos datos de 2024, aparecen registros de años como **2002, 2009 o incluso 2030**. 

### ¿Por qué sucede esto?
No es un error de tu código. Es la realidad de trabajar con datos masivos del mundo real:
1. **Taxímetros Desconfigurados**: Muchos taxis tienen relojes internos mal configurados. Si el reloj dice que es el año 2002, el viaje se registrará con esa fecha.
2. **Reseteos de Hardware**: Fallos de batería o GPS pueden resetear la fecha del sistema a valores por defecto.
3. **Ruido en la Fuente**: El dataset de NYC TLC es famoso por contener este tipo de "anomalías cronológicas".

### 💡 Tu Desafío (Opcional)
Un Data Engineer Senior no solo mueve datos, los limpia. En la **Arquitectura Medallion**, la capa **Silver** es el lugar ideal para filtrar este ruido.

**¿Te atreves a resolverlo?**
Intenta modificar tu modelo `silver_yellow_tripdata.sql` para añadir un filtro `WHERE` que solo permita viajes con fechas lógicas (ej: entre 2023 y 2025). ¡Esa es la diferencia entre un pipeline que funciona y uno que es confiable!

---

## 🧠 Conclusión Final
¡Felicidades! Has construido un **Data Lakehouse End-to-End** con estándares de la industria. 

**¿Qué has aprendido?**
1. **IaC**: Terraform para gestionar la nube.
2. **Orquestación**: Airflow con Docker (DooD).
3. **Almacenamiento**: GCS + BigQuery (Lakehouse).
4. **Transformación**: dbt con Arquitectura Medallion (Bronze, Silver, Gold).
5. **Calidad**: Tipado explícito, deduplicación y tests automatizados.
6. **Seniority**: Remote Backends y Micro-containerización.

**No te olvides de guardar tus avances:**

```bash
git add .
git commit -m "feat: complete medallion architecture with gold layer and tests"
git push origin main
```
