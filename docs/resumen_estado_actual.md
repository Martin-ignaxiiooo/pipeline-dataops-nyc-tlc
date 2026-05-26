# Resumen del estado actual

## Implementado

- Pipeline en Python para limpieza, validacion y carga.
- Separacion de datos en `raw`, `processed`, `validated` y `reports`.
- Logs para limpieza, validacion y carga.
- Script SQL para crear la tabla `green_trips`.
- Carga a PostgreSQL con `src/load.py`.
- Soporte Docker con `Dockerfile` y `docker-compose.yml`.
- Documentacion del proyecto y preguntas de defensa.

## Archivos principales

```text
src/clean.py
src/validate.py
src/load.py
src/main.py
sql/create_table.sql
README.md
requirements.txt
.env.example
Dockerfile
docker-compose.yml
```

## Archivos que genera el pipeline

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

## Evidencia para la evaluacion

- `data/raw/green_trips_raw.csv`: datos originales.
- `data/processed/green_trips_clean.csv`: datos despues de limpieza.
- `data/validated/green_trips_validated.csv`: registros validos.
- `data/validated/green_trips_rejected.csv`: registros rechazados por reglas.
- `data/validated/green_trips_inserted.csv`: registros insertados en PostgreSQL.
- `data/validated/green_trips_db_rejected.csv`: errores de insercion en base de datos.
- `data/reports/validation_report.txt`: resumen de la validacion.
- `logs/clean.log`, `logs/validate.log`, `logs/load.log`: evidencia de ejecucion.
- Revision en pgAdmin con `SELECT COUNT(*) FROM green_trips;`.
- Prueba con Docker Compose en el equipo de Martin.

## Resultados finales

```text
Registros leidos: 1000
Registros limpios: 985
Registros validos: 973
Registros rechazados en validacion: 12
Registros insertados en PostgreSQL: 973
Rechazados por base de datos: 0
```

Detalle de limpieza:

```text
Duplicados eliminados: 0
Nulos criticos eliminados: 0
trip_distance <= 0 eliminados: 0
fare_amount < 2 eliminados: 14
Duraciones invalidas eliminadas: 1
```

El motivo principal de rechazo en validacion fue velocidad fuera del rango permitido entre 1 y 80 mph.

## PostgreSQL

La carga fue probada localmente en Windows con PostgreSQL instalado.

En pgAdmin:

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

Los datos se cargaron correctamente.

## Docker

Docker Compose fue probado en el equipo de Martin.

Resultados:

```text
Docker Compose levanto PostgreSQL 16.
El servicio pipeline ejecuto limpieza, validacion y carga.
Registros leidos: 1000
Registros limpios: 985
Registros validos: 973
Registros rechazados en validacion: 12
Registros insertados en PostgreSQL: 973
Registros rechazados por base de datos: 0
El contenedor pipeline termino con codigo de salida 0.
SELECT COUNT(*) FROM green_trips; = 973
```

La ejecucion local y la ejecucion con Docker Compose dieron los mismos resultados.

## Pendiente posible

- Subir el proyecto a GitHub.
- Agregar pruebas automatizadas si la pauta lo pide.
- Mejorar reportes si se quiere mostrar mas detalle.
