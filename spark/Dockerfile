# 1. Definizione delle immagini base: Python 3.9 slim e OpenJDK 8 slim
ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8
ARG PYTHON_VERSION=3.9.8

# Prima stadi: importiamo l’ambiente Python
FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT} AS py3
# Secondo stadio: ambiente Java
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}

# 2. Installazione delle librerie native Snappy
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      libsnappy1v5 libsnappy-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 3. Copia dell’ambiente Python dall’immagine py3
COPY --from=py3 / /

# 4. Installazione via pip di PySpark, Elasticsearch e NumPy
ARG PYSPARK_VERSION=3.4.0
RUN pip install --no-cache-dir \
      pyspark==${PYSPARK_VERSION} \
      elasticsearch \
      numpy

# 5) Imposti la working dir
WORKDIR /home

# 6) Copi il tuo script spark.py
COPY spark.py /home/spark.py

# 7) Comando di default: Spark in shell-form, con line-continuation per comodità
CMD spark-submit --master local[1] \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1 \
    /home/spark.py
