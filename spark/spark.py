from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, from_unixtime
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# 1. Definizione dello schema per i dati in ingresso
match_schema = StructType([
    StructField("match_id", IntegerType(), False),
    StructField("team_a", StringType(), False),
    StructField("team_b", StringType(), False),
    StructField("score_a", IntegerType(), False),
    StructField("score_b", IntegerType(), False),
    StructField("timestamp", IntegerType(), False)
])

# 2. Inizializzazione della SparkSession
spark = SparkSession.builder \
    .appName("VolleyballMatchesProcessor") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1") \
    .config("spark.es.nodes.wan.only", "true") \
    .getOrCreate()

# 3. Lettura dei dati da Kafka
kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-volley:9092") \
    .option("subscribe", "matchvolley") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Trasformazione dei dati
processed_data = kafka_stream \
    .select(from_json(col("value").cast("string"), match_schema).alias("data")) \
    .select("data.*") \
    .withColumn("event_time", from_unixtime(col("timestamp")).cast(TimestampType()))

# 5. Scrittura su Elasticsearch
query = processed_data.writeStream \
    .outputMode("append") \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch-volley") \
    .option("es.port", "9200") \
    .option("es.resource", "volleyball_matches") \
    .option("es.mapping.id", "match_id") \
    .option("es.nodes.wan.only", "true") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start()

# 6. Gestione dell'esecuzione
try:
    query.awaitTermination()
except Exception as e:
    print(f"Errore durante l'esecuzione: {str(e)}")
    query.stop()