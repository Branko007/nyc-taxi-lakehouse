from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
import os 

# --- CONFIGURACIÓN ---
# ⚠️ IMPORTANTE (DooD): En Docker-out-of-Docker, el 'source' de un Mount debe ser la ruta EN EL HOST.
# Si Airflow corre en Docker, os.path no nos sirve porque daría la ruta interna (/opt/airflow).
# Por eso, usamos una variable de entorno que definiremos en el docker-compose o .env
PROJECT_PATH = os.getenv("AIRFLOW_PROJ_DIR", "/home/TU_USUARIO/projects/nyc-taxi-lakehouse")

# 👇 LEEMOS LA CONFIGURACIÓN DEL ENTORNO
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "MISSING_BUCKET")

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
    description='Ingestión y transformación mensual de datos de NYC Taxi',
    schedule_interval='@monthly',
    start_date=datetime(2024, 1, 1), # Cambiamos a 2024 para evitar errores de datos futuros por defecto
    catchup=False,
    tags=['ingestion', 'docker', 'dbt', 'nyc-lakehouse'],
) as dag:

    # Tarea 1: Ingestión Dinámica (Bronze)
    ingest_task = DockerOperator(
        task_id='ingest_data',
        image='nyc-taxi-ingestor:v1',
        api_version='auto',
        auto_remove=True,
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

    # Tarea 2: Transformación con dbt (Silver & Gold)
    transform_task = DockerOperator(
        task_id='dbt_run',
        image='nyc-taxi-dbt:v1',
        api_version='auto',
        auto_remove=True,
        command="run --profiles-dir .",
        network_mode="host",
        mounts=[
            Mount(source=f"{PROJECT_PATH}/dbt_project", target="/usr/app/dbt_project", type="bind"),
            Mount(source=f"{PROJECT_PATH}/gcp_credentials", target="/usr/app/gcp_credentials", type="bind")
        ],
        docker_url="unix://var/run/docker.sock",
    )

    # Tarea 3: Pruebas de Calidad con dbt
    test_task = DockerOperator(
        task_id='dbt_test',
        image='nyc-taxi-dbt:v1',
        api_version='auto',
        auto_remove=True,
        command="test --profiles-dir .",
        network_mode="host",
        mounts=[
            Mount(source=f"{PROJECT_PATH}/dbt_project", target="/usr/app/dbt_project", type="bind"),
            Mount(source=f"{PROJECT_PATH}/gcp_credentials", target="/usr/app/gcp_credentials", type="bind")
        ],
        docker_url="unix://var/run/docker.sock",
    )

    # Definimos el flujo: Ingesta -> Transformación -> Pruebas
    ingest_task >> transform_task >> test_task