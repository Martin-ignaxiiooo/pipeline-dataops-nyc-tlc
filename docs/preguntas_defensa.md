# Preguntas de defensa

## Que es DataOps?

DataOps es una forma de trabajar los datos con orden. En este proyecto se ve en la separacion de etapas: datos originales, limpieza, validacion, carga y logs.

## Por que se separan datos raw, processed y validated?

Porque cada carpeta representa una etapa distinta. `raw` mantiene el archivo original, `processed` guarda los datos limpios y `validated` deja los registros que ya pasaron las reglas.

## Que hace la etapa de limpieza?

La limpieza prepara el CSV para poder usarlo mejor. Convierte fechas y numeros, elimina duplicados, elimina nulos importantes, descarta tarifas o distancias invalidas y calcula duracion y velocidad.

## Que hace la validacion semantica?

Revisa que los datos tengan sentido. Por ejemplo, que el viaje termine despues de empezar, que la distancia sea mayor a cero y que la velocidad no sea demasiado baja o demasiado alta.

## Por que se generan logs?

Porque sirven como evidencia de lo que paso al ejecutar el pipeline. Tambien ayudan a revisar errores sin tener que volver a leer todo el codigo.

## Que significan registros validos y rechazados?

Los validos cumplen todas las reglas. Los rechazados fallan una o mas reglas, por eso se separan para no cargarlos como datos confiables.

## Que falta para completar la carga a PostgreSQL?

La carga ya esta completa. Se creo la tabla `green_trips`, se uso `src/load.py`, se insertaron 973 registros y no hubo rechazados por base de datos.

## Que aporta Docker Compose?

Docker Compose permite levantar PostgreSQL y ejecutar el pipeline sin depender de una instalacion local. En el equipo de Martin se probo correctamente y dio los mismos resultados que la ejecucion local.
