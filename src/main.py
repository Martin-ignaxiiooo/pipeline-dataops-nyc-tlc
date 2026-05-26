try:
    from dotenv import load_dotenv
except ImportError:
    # El pipeline puede partir aunque dotenv no este instalado.
    def load_dotenv():
        return None

from clean import clean_data
from load import load_data
from validate import validate_data


def main():
    """Ejecuta limpieza, validacion y carga."""
    load_dotenv()

    print("Iniciando pipeline NYC TLC Green Taxi Trips")

    print("1. Ejecutando limpieza...")
    total_clean = clean_data()
    print(f"   Limpieza terminada. Registros limpios: {total_clean}")

    print("2. Ejecutando validacion...")
    total_valid, total_rejected = validate_data()
    print(f"   Validacion terminada. Validos: {total_valid} | Rechazados: {total_rejected}")

    print("3. Ejecutando carga a PostgreSQL...")
    total_inserted, total_db_rejected = load_data()
    print(
        "   Carga terminada. "
        f"Insertados: {total_inserted} | Rechazados DB: {total_db_rejected}"
    )

    print("Pipeline finalizado correctamente.")


if __name__ == "__main__":
    main()
