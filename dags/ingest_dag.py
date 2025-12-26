from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
import os 

# --- CONFIGURACIÓN ---
# Obtenemos la ruta base del proyecto de forma dinámica
DAG_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.abspath(os.path.join(DAG_PATH, ".."))

# 👇 LEEMOS LA CONFIGURACIÓN DEL ENTORNO
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

    # Tarea 1: Ingestión Dinámica
    ingest_task = DockerOperator(
        task_id='ingest_data',
        image='nyc-taxi-ingestor:v1',
        api_version='auto',
        auto_remove=True,
        # Usamos macros de Airflow para que sea dinámico basado en la fecha de ejecución
        command="--year {{ execution_date.year }} --month {{ execution_date.month }}",
        network_mode="host", 
        mounts=[
            Mount(
                source=f"{PROJECT_PATH}/gcp_credentials", 
                target="/app/gcp_credentials", 
                type="bind"
            )
        ],
        environment={
            'GOOGLE_APPLICATION_CREDENTIALS': '/app/gcp_credentials/terraform-key.json',
            'GCS_BUCKET_NAME': BUCKET_NAME 
        },
        docker_url="unix://var/run/docker.sock",
    )

    # Tarea 2: Transformación con dbt (Capa Silver)
    transform_task = DockerOperator(
        task_id='dbt_transform',
        image='nyc-taxi-dbt:v1',
        api_version='auto',
        auto_remove=True,
        # Ejecutamos dbt run usando el perfil local
        command="run --profiles-dir .",
        network_mode="host",
        mounts=[
            # Montamos el proyecto dbt
            Mount(
                source=f"{PROJECT_PATH}/dbt_project",
                target="/usr/app/dbt_project",
                type="bind"
            ),
            # Montamos las credenciales en la ruta que espera profiles.yml (../gcp_credentials)
            Mount(
                source=f"{PROJECT_PATH}/gcp_credentials",
                target="/usr/app/gcp_credentials",
                type="bind"
            )
        ],
        docker_url="unix://var/run/docker.sock",
    )

    # Definimos la dependencia: Primero ingesta, luego transformación
    ingest_task >> transform_task