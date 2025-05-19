from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import (
    StructType, StructField, IntegerType, DoubleType,
    StringType, TimestampType
)

# Configurazione Spark
spark = SparkSession.builder \
    .appName("VolleyballSnapshotProcessor") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
            "org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1") \
    .getOrCreate()

# Schema per i record snapshot inviati dal producer
snapshot_schema = StructType([
    StructField("match_id", IntegerType()),
    StructField("timestamp", StringType()),    # JSON serializza datetime come stringa
    StructField("home_team_id", IntegerType()),
    StructField("away_team_id", IntegerType()),
    StructField("home_score_total", IntegerType()),
    StructField("away_score_total", IntegerType()),
    StructField("home_sets_won", IntegerType()),
    StructField("away_sets_won", IntegerType()),
    StructField("score_diff", IntegerType()),
    StructField("set_diff", IntegerType()),
    StructField("home_current_score", StringType()),   
    StructField("away_current_score", StringType()),
    StructField("set_info", StringType()),
    StructField("game_duration", StringType()),
    StructField("match_status", StringType()),
    StructField("home_win_rate_last5", DoubleType()),
    StructField("away_win_rate_last5", DoubleType()),
    StructField("head_to_head_win_rate_home", DoubleType())
])

# Leggi stream da Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-volley:9092") \
    .option("subscribe", "matchvolley") \
    .option("startingOffsets", "latest") \
    .load()

# Parsing JSON e applicazione dello schema snapshot
parsed_df = kafka_df.select(
    from_json(col("value").cast("string"), snapshot_schema).alias("data")
).select("data.*")

# Converto la stringa timestamp in vero tipo Timestamp, e rinomino per chiarezza
processed_df = parsed_df \
    .withColumn("event_timestamp", to_timestamp(col("timestamp"))) \
    .drop("timestamp")

# Scrivi su Elasticsearch, usando match_id come document ID
es_query = processed_df.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch-volley") \
    .option("es.port", "9200") \
    .option("es.resource", "volleyball_matches") \
    .option("es.write.operation", "index") \
    .option("checkpointLocation", "/tmp/spark-es-checkpoint") \
    .outputMode("append") \
    .start()


es_query.awaitTermination()
