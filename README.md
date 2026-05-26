# Pipeline DataOps NYC TLC

Proyecto en Python para limpiar, validar y cargar datos de viajes de taxis verdes de Nueva York.

## Caso

- Caso usado: **NYC TLC Green Taxi Trips**
- Dataset base: `tlc_green_trips_2022`
- Archivo de entrada: `data/raw/green_trips_raw.csv`
- Tabla destino en PostgreSQL: `green_trips`

La idea del proyecto es dejar un flujo ordenado: datos originales, limpieza, validacion, carga a PostgreSQL y evidencias de ejecucion.

## Estructura

```text
pipeline-dataops-nyc-tlc/
|-- data/
|   |-- raw/
|   |-- processed/
|   |-- validated/
|   `-- reports/
|-- docs/
|   |-- resumen_estado_actual.md
|   `-- preguntas_defensa.md
|-- logs/
|-- sql/
|   `-- create_table.sql
|-- src/
|   |-- clean.py
|   |-- load.py
|   |-- validate.py
|   `-- main.py
|-- Dockerfile
|-- docker-compose.yml
|-- .dockerignore
|-- README.md
|-- requirements.txt
|-- .gitignore
`-- .env.example
```

## Limpieza

La limpieza esta en `src/clean.py`.

Hace lo siguiente:

- lee `data/raw/green_trips_raw.csv`
- convierte las fechas de pickup y dropoff
- elimina duplicados
- elimina nulos en columnas importantes
- convierte columnas numericas
- elimina viajes con `trip_distance <= 0`
- elimina viajes con `fare_amount < 2`
- calcula `duracion_minutos`
- calcula `velocidad_mph`
- elimina duraciones invalidas
- guarda `data/processed/green_trips_clean.csv`
- genera `logs/clean.log`

## Validacion

La validacion esta en `src/validate.py`.

Revisa estas reglas:

- `dropoff_datetime > pickup_datetime`
- `trip_distance > 0`
- `fare_amount >= 2`
- `duracion_minutos > 0`
- `velocidad_mph` entre 1 y 80
- `vendor_id` en `[1, 2]`
- `pickup_location_id > 0`
- `dropoff_location_id > 0`

Los registros que cumplen todo quedan en `green_trips_validated.csv`. Los que fallan alguna regla quedan en `green_trips_rejected.csv`.

## Carga a PostgreSQL

La carga esta en `src/load.py`.

El script:

- lee la conexion desde `.env`
- lee `data/validated/green_trips_validated.csv`
- crea la tabla `green_trips` usando `sql/create_table.sql`
- limpia la tabla antes de cargar con `TRUNCATE TABLE green_trips RESTART IDENTITY;`
- inserta los registros validos
- guarda los insertados en `data/validated/green_trips_inserted.csv`
- guarda errores de base de datos en `data/validated/green_trips_db_rejected.csv`
- genera `logs/load.log`

El archivo `.env` no se sube al repositorio. Para probar localmente se usa `.env.example` como base.

## Archivos generados

```text
data/processed/green_trips_clean.csv
data/validated/green_trips_validated.csv
data/validated/green_trips_rejected.csv
data/validated/green_trips_inserted.csv
data/validated/green_trips_db_rejected.csv
data/reports/validation_report.txt
logs/clean.log
logs/validate.log
logs/load.log
```

## Resultados finales

Con el CSV real de 1000 registros:

```text
Registros leidos: 1000
Registros limpios: 985
Registros validos: 973
Registros rechazados en validacion: 12
Registros insertados en PostgreSQL: 973
Rechazados por base de datos: 0
```

Detalle de limpieza y validacion:

```text
Duplicados eliminados: 0
Nulos criticos eliminados: 0
trip_distance <= 0 eliminados: 0
fare_amount < 2 eliminados: 14
Duraciones invalidas eliminadas: 1
Rechazados en validacion: 12
Motivo principal de rechazo: velocidad fuera del rango permitido entre 1 y 80 mph
```

En pgAdmin se comprobo:

```sql
SELECT COUNT(*) FROM green_trips;
```

Resultado:

```text
973
```

Tambien se reviso:

```sql
SELECT * FROM green_trips LIMIT 10;
```

La consulta mostro datos cargados correctamente.

## Ejecucion local

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear un archivo `.env` local:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nyc_tlc_trips
DB_USER=postgres
DB_PASSWORD=tu_contrasena_real
```

Ejecutar todo el pipeline:

```bash
python src/main.py
```

En Windows tambien se puede usar:

```bash
py src/main.py
```

Etapas por separado:

```bash
python src/clean.py
python src/validate.py
python src/load.py
```

La ejecucion local fue validada en Windows con PostgreSQL instalado y revisada desde pgAdmin.

## Ejecucion con Docker

Docker Compose tambien fue probado correctamente en el equipo de Martin.

Comando:

```bash
docker compose up --build
```

Resultado con Docker:

```text
Docker Compose levanto PostgreSQL 16.
El servicio pipeline ejecuto limpieza, validacion y carga.
El contenedor pipeline termino con codigo de salida 0.
SELECT COUNT(*) FROM green_trips; = 973
```

La ejecucion local y la ejecucion con Docker Compose dieron los mismos resultados.

El `docker-compose.yml` usa:

- servicio `db` con PostgreSQL 16
- base de datos `nyc_tlc_trips`
- usuario `postgres`
- password `postgres`
- puerto externo `5433:5432`
- servicio `pipeline` conectado a `db`
