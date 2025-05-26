#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, date_format, to_timestamp

from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, DoubleType, StringType
)

# ------------------ Spark Session ------------------
spark = SparkSession.builder \
    .appName("VolleyballSnapshotProcessor") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
        "org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1"
    ) \
    .getOrCreate()

# ------------------ Schema Definition ------------------
snapshot_schema = StructType([
    StructField("match_id", IntegerType(), nullable=False),
    StructField("timestamp", StringType(), nullable=False),       # "yyyy-MM-dd HH:mm:ss.SSSSSS"
    StructField("home_team_id", IntegerType(), nullable=False),
    StructField("away_team_id", IntegerType(), nullable=False),
    StructField("home_score_total", IntegerType(), nullable=False),
    StructField("away_score_total", IntegerType(), nullable=False),
    StructField("home_sets_won", IntegerType(), nullable=False),
    StructField("away_sets_won", IntegerType(), nullable=False),
    StructField("score_diff", IntegerType(), nullable=False),
    StructField("set_diff", IntegerType(), nullable=False),
    StructField("home_current_score", StringType(), nullable=False),
    StructField("away_current_score", StringType(), nullable=False),
    StructField("set_info", StringType(), nullable=False),
    StructField("game_duration", StringType(), nullable=False),
    StructField("match_status", StringType(), nullable=False),
    StructField("home_win_rate_last5", DoubleType(), nullable=False),
    StructField("away_win_rate_last5", DoubleType(), nullable=False),
    StructField("head_to_head_win_rate_home", DoubleType(), nullable=False),
])

# ------------------ Read from Kafka ------------------
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-volley:9092") \
    .option("subscribe", "matchvolley") \
    .option("startingOffsets", "latest") \
    .load()

# ------------------ Parse JSON ------------------
parsed_df = kafka_df.select(
    from_json(col("value").cast("string"), snapshot_schema).alias("data")
).select("data.*")

# ------------------ Convert String → TimestampType on the same field ------------------
processed_df = parsed_df.withColumn(
    "timestamp",
    date_format(
        to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss.SSSSSS"),
        "yyyy-MM-dd HH:mm:ss.SSSSSS"
    )
)

# ------------------ Write to Elasticsearch ------------------
es_query = processed_df.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch-volley") \
    .option("es.port", "9200") \
    .option("es.resource", "volleyball_matches") \
    .option("es.write.operation", "index") \
    .option("checkpointLocation", "/tmp/spark-es-checkpoint") \
    .outputMode("append") \
    .start()

# ------------------ Await Termination ------------------
es_query.awaitTermination()
