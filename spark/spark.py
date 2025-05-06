from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, MapType
from pyspark.sql.functions import current_timestamp

# Configurazione Spark
spark = SparkSession.builder \
    .appName("VolleyballStreamProcessor") \
    .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
            "org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1") \
    .getOrCreate()

# Schema per i dati in arrivo da Kafka
volleyball_schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType()),
    StructField("tournament_id", IntegerType()),
    StructField("home_team_id", IntegerType()),
    StructField("away_team_id", IntegerType()),
    StructField("home_team_name", StringType()),
    StructField("away_team_name", StringType()),
    StructField("home_team_score", MapType(StringType(), IntegerType())),
    StructField("away_team_score", MapType(StringType(), IntegerType())),
    StructField("status", MapType(StringType(), StringType())),
    StructField("arena_name", StringType()),
    StructField("start_time", StringType()),
    StructField("duration", IntegerType()),
    StructField("round", MapType(StringType(), StringType())),
    StructField("coaches", MapType(StringType(), StringType()))
])

# Leggi da Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-volley:9092") \
    .option("subscribe", "matchvolley") \
    .option("startingOffsets", "latest") \
    .load()

# Parsing dei dati JSON
parsed_df = kafka_df.select(
    from_json(col("value").cast("string"), volleyball_schema).alias("data")
).select("data.*")

# Aggiungi campo timestamp di elaborazione
processed_df = parsed_df.withColumn("processing_timestamp", current_timestamp())

# Scrivi su Elasticsearch
query = processed_df.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch-volley") \
    .option("es.port", "9200") \
    .option("es.resource", "volleyball_matches") \
    .option("es.mapping.id", "id") \
    .option("es.write.operation", "upsert") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .outputMode("append") \
    .start()

query.awaitTermination()