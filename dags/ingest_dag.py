from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
import os 

# --- CONFIGURACIÓN ---
PROJECT_PATH = "/home/branko007/projects/nyc-taxi-lakehouse" 

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
        command="--year 2024 --month 3",
        
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