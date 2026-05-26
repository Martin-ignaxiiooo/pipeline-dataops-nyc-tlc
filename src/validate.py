from pathlib import Path
import logging

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "green_trips_clean.csv"
VALIDATED_FILE = BASE_DIR / "data" / "validated" / "green_trips_validated.csv"
REJECTED_FILE = BASE_DIR / "data" / "validated" / "green_trips_rejected.csv"
REPORT_FILE = BASE_DIR / "data" / "reports" / "validation_report.txt"
LOG_FILE = BASE_DIR / "logs" / "validate.log"


def setup_logger():
    """Deja listo el log de validacion."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("validate")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    return logger


def validate_data():
    """Aplica reglas y separa validos de rechazados."""
    logger = setup_logger()

    if not PROCESSED_FILE.exists():
        message = f"No se encontro el archivo procesado: {PROCESSED_FILE}"
        logger.error(message)
        raise FileNotFoundError(message)

    logger.info("Iniciando validacion de datos")
    df = pd.read_csv(PROCESSED_FILE)
    logger.info("Registros leidos para validar: %s", len(df))

    # Al leer desde CSV, algunas columnas vuelven como texto.
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"], errors="coerce")

    numeric_columns = [
        "vendor_id",
        "pickup_location_id",
        "dropoff_location_id",
        "trip_distance",
        "fare_amount",
        "duracion_minutos",
        "velocidad_mph",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    rules = {
        "dropoff_datetime > pickup_datetime": df["dropoff_datetime"] > df["pickup_datetime"],
        "trip_distance > 0": df["trip_distance"] > 0,
        "fare_amount >= 2": df["fare_amount"] >= 2,
        "duracion_minutos > 0": df["duracion_minutos"] > 0,
        "velocidad_mph entre 1 y 80": df["velocidad_mph"].between(1, 80),
        "vendor_id en [1, 2]": df["vendor_id"].isin([1, 2]),
        "pickup_location_id > 0": df["pickup_location_id"] > 0,
        "dropoff_location_id > 0": df["dropoff_location_id"] > 0,
    }

    valid_mask = pd.Series(True, index=df.index)
    for rule_mask in rules.values():
        valid_mask = valid_mask & rule_mask.fillna(False)

    valid_rows = df[valid_mask].copy()
    rejected_rows = df[~valid_mask].copy()

    VALIDATED_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    valid_rows.to_csv(VALIDATED_FILE, index=False)
    rejected_rows.to_csv(REJECTED_FILE, index=False)

    report_lines = [
        "Reporte de validacion - NYC TLC Green Taxi Trips",
        "",
        f"Archivo validado: {PROCESSED_FILE}",
        f"Total de registros evaluados: {len(df)}",
        f"Registros validos: {len(valid_rows)}",
        f"Registros rechazados: {len(rejected_rows)}",
        "",
        "Reglas aplicadas:",
    ]

    for rule_name, rule_mask in rules.items():
        rejected_by_rule = int((~rule_mask.fillna(False)).sum())
        report_lines.append(f"- {rule_name}: {rejected_by_rule} registros rechazados")

    report_lines.append("")
    report_lines.append("Nota: un mismo registro puede fallar mas de una regla.")

    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")

    logger.info("Registros validos: %s", len(valid_rows))
    logger.info("Registros rechazados: %s", len(rejected_rows))
    logger.info("Archivo validado guardado en: %s", VALIDATED_FILE)
    logger.info("Archivo de rechazados guardado en: %s", REJECTED_FILE)
    logger.info("Reporte guardado en: %s", REPORT_FILE)

    return len(valid_rows), len(rejected_rows)


if __name__ == "__main__":
    total_valid, total_rejected = validate_data()
    print(f"Validacion finalizada. Validos: {total_valid} | Rechazados: {total_rejected}")
