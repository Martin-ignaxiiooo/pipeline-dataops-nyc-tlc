from pathlib import Path
import logging
import os

import pandas as pd

try:
    from dotenv import load_dotenv
except ImportError:
    # Si falta dotenv, igual se revisan las variables mas abajo.
    def load_dotenv(*args, **kwargs):
        return None

try:
    import psycopg2
except ImportError:
    psycopg2 = None


BASE_DIR = Path(__file__).resolve().parents[1]
VALIDATED_FILE = BASE_DIR / "data" / "validated" / "green_trips_validated.csv"
INSERTED_FILE = BASE_DIR / "data" / "validated" / "green_trips_inserted.csv"
DB_REJECTED_FILE = BASE_DIR / "data" / "validated" / "green_trips_db_rejected.csv"
SQL_FILE = BASE_DIR / "sql" / "create_table.sql"
LOG_FILE = BASE_DIR / "logs" / "load.log"

INSERT_COLUMNS = [
    "pickup_datetime",
    "dropoff_datetime",
    "trip_distance",
    "fare_amount",
    "pickup_location_id",
    "dropoff_location_id",
    "vendor_id",
    "duracion_minutos",
    "velocidad_mph",
]


def setup_logger():
    """Deja listo el log de carga."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("load")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    return logger


def get_db_config():
    """Lee los datos de conexion desde .env."""
    load_dotenv(BASE_DIR / ".env")

    config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    missing = [key for key, value in config.items() if not value]
    if missing:
        missing_names = ", ".join(missing)
        raise ValueError(f"Faltan variables de conexion en .env: {missing_names}")

    return config


def prepare_dataframe(df):
    """Prepara tipos antes de insertar en PostgreSQL."""
    df = df.copy()

    df["pickup_datetime"] = pd.to_datetime(
        df["pickup_datetime"], errors="coerce", utc=True
    ).dt.tz_convert(None)
    df["dropoff_datetime"] = pd.to_datetime(
        df["dropoff_datetime"], errors="coerce", utc=True
    ).dt.tz_convert(None)

    numeric_columns = [
        "trip_distance",
        "fare_amount",
        "pickup_location_id",
        "dropoff_location_id",
        "vendor_id",
        "duracion_minutos",
        "velocidad_mph",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def clean_value(value):
    """Pasa valores vacios a None para PostgreSQL."""
    if pd.isna(value):
        return None
    return value


def load_data():
    """Carga los registros validados en PostgreSQL."""
    logger = setup_logger()

    if psycopg2 is None:
        message = "Falta instalar psycopg2-binary. Ejecuta: pip install -r requirements.txt"
        logger.error(message)
        raise ImportError(message)

    if not VALIDATED_FILE.exists():
        message = f"No se encontro el archivo validado: {VALIDATED_FILE}"
        logger.error(message)
        raise FileNotFoundError(message)

    if not SQL_FILE.exists():
        message = f"No se encontro el archivo SQL: {SQL_FILE}"
        logger.error(message)
        raise FileNotFoundError(message)

    logger.info("Iniciando carga a PostgreSQL")

    try:
        db_config = get_db_config()
    except ValueError as error:
        logger.error(error)
        raise
    df = pd.read_csv(VALIDATED_FILE)
    df = prepare_dataframe(df)

    missing_columns = [column for column in INSERT_COLUMNS if column not in df.columns]
    if missing_columns:
        message = f"Faltan columnas para cargar en PostgreSQL: {missing_columns}"
        logger.error(message)
        raise ValueError(message)

    create_table_sql = SQL_FILE.read_text(encoding="utf-8")

    inserted_rows = []
    rejected_rows = []

    insert_sql = """
        INSERT INTO green_trips (
            pickup_datetime,
            dropoff_datetime,
            trip_distance,
            fare_amount,
            pickup_location_id,
            dropoff_location_id,
            vendor_id,
            duracion_minutos,
            velocidad_mph
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    connection = psycopg2.connect(**db_config)
    connection.autocommit = True

    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_sql)
            cursor.execute("TRUNCATE TABLE green_trips RESTART IDENTITY;")

            for _, row in df.iterrows():
                row_data = row.to_dict()
                values = tuple(clean_value(row[column]) for column in INSERT_COLUMNS)

                try:
                    cursor.execute(insert_sql, values)
                    inserted_rows.append(row_data)
                except Exception as error:
                    row_data["db_error"] = str(error)
                    rejected_rows.append(row_data)
                    logger.error("Registro rechazado por PostgreSQL: %s", error)
    finally:
        connection.close()

    pd.DataFrame(inserted_rows, columns=df.columns).to_csv(INSERTED_FILE, index=False)

    rejected_columns = list(df.columns) + ["db_error"]
    pd.DataFrame(rejected_rows, columns=rejected_columns).to_csv(
        DB_REJECTED_FILE, index=False
    )

    logger.info("Registros leidos para cargar: %s", len(df))
    logger.info("Registros insertados: %s", len(inserted_rows))
    logger.info("Registros rechazados por base de datos: %s", len(rejected_rows))
    logger.info("Archivo de insertados guardado en: %s", INSERTED_FILE)
    logger.info("Archivo de rechazados DB guardado en: %s", DB_REJECTED_FILE)

    return len(inserted_rows), len(rejected_rows)


if __name__ == "__main__":
    total_inserted, total_rejected = load_data()
    print(
        "Carga finalizada. "
        f"Insertados: {total_inserted} | Rechazados DB: {total_rejected}"
    )
