ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8
ARG PYTHON_VERSION=3.9.8

FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT} AS py3
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}

COPY --from=py3 / /

ARG PYSPARK_VERSION=3.4.0
RUN pip --no-cache-dir install pyspark==${PYSPARK_VERSION} \
    && pip --no-cache-dir install elasticsearch

WORKDIR /home

COPY spark.py /home/spark.py


CMD spark-submit --master local[1] \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1 \
    /home/spark.py