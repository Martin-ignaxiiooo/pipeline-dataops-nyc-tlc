from pathlib import Path
import logging

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "raw" / "green_trips_raw.csv"
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "green_trips_clean.csv"
LOG_FILE = BASE_DIR / "logs" / "clean.log"


# El CSV puede venir con nombres originales del archivo TLC.
COLUMN_RENAMES = {
    "VendorID": "vendor_id",
    "lpep_pickup_datetime": "pickup_datetime",
    "lpep_dropoff_datetime": "dropoff_datetime",
    "PULocationID": "pickup_location_id",
    "DOLocationID": "dropoff_location_id",
}

CRITICAL_COLUMNS = [
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "pickup_location_id",
    "dropoff_location_id",
    "trip_distance",
    "fare_amount",
]

NUMERIC_COLUMNS = [
    "vendor_id",
    "pickup_location_id",
    "dropoff_location_id",
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "payment_type",
    "trip_type",
    "congestion_surcharge",
]


def setup_logger():
    """Deja listo el log de limpieza."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("clean")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    return logger


def clean_data():
    """Limpia el CSV raw y guarda el archivo procesado."""
    logger = setup_logger()

    if not RAW_FILE.exists():
        message = f"No se encontro el archivo de entrada: {RAW_FILE}"
        logger.error(message)
        raise FileNotFoundError(message)

    logger.info("Iniciando limpieza de datos")
    df = pd.read_csv(RAW_FILE)
    logger.info("Registros leidos: %s", len(df))

    df = df.rename(columns=COLUMN_RENAMES)

    missing_columns = [column for column in CRITICAL_COLUMNS if column not in df.columns]
    if missing_columns:
        message = f"Faltan columnas criticas en el CSV: {missing_columns}"
        logger.error(message)
        raise ValueError(message)

    # Fechas y numeros quedan en tipos que pandas pueda trabajar.
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    before_duplicates = len(df)
    df = df.drop_duplicates()
    logger.info("Duplicados eliminados: %s", before_duplicates - len(df))

    before_nulls = len(df)
    df = df.dropna(subset=CRITICAL_COLUMNS)
    logger.info("Registros con nulos criticos eliminados: %s", before_nulls - len(df))

    before_distance = len(df)
    df = df[df["trip_distance"] > 0]
    logger.info("Registros con trip_distance <= 0 eliminados: %s", before_distance - len(df))

    before_fare = len(df)
    df = df[df["fare_amount"] >= 2]
    logger.info("Registros con fare_amount < 2 eliminados: %s", before_fare - len(df))

    df["duracion_minutos"] = (
        df["dropoff_datetime"] - df["pickup_datetime"]
    ).dt.total_seconds() / 60

    before_duration = len(df)
    df = df[df["duracion_minutos"] > 0]
    logger.info("Registros con duracion invalida eliminados: %s", before_duration - len(df))

    df["velocidad_mph"] = df["trip_distance"] / (df["duracion_minutos"] / 60)

    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)

    logger.info("Registros finales limpios: %s", len(df))
    logger.info("Archivo procesado guardado en: %s", PROCESSED_FILE)

    return len(df)


if __name__ == "__main__":
    total_clean = clean_data()
    print(f"Limpieza finalizada. Registros limpios: {total_clean}")
