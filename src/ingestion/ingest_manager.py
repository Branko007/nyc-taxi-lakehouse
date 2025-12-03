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
