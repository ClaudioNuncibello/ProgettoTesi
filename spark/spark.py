#!/usr/bin/env python3
import re

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, date_format, to_timestamp, udf
)
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, DoubleType, StringType
)
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Imputer, StringIndexer, OneHotEncoder, VectorAssembler
)
from pyspark.ml.classification import RandomForestClassifier

# ------------------ Spark Session ------------------
spark = SparkSession.builder \
    .appName("VolleyballSnapshotProcessor") \
    .config("spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
        "org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1") \
    .config("spark.sql.parquet.compression.codec", "uncompressed") \
    .getOrCreate()


#------------------- Modello di predizione --------------
# 2) UDF per parsare “148m 58s” → secondi
@udf("double")
def parse_duration(s: str) -> float:
    if s is None: return None
    m = re.search(r"(\d+)m", s)
    sec = re.search(r"(\d+)s", s)
    mins = float(m.group(1)) if m else 0.0
    secs = float(sec.group(1)) if sec else 0.0
    return mins * 60.0 + secs

# 3) BATCH TRAINING sul CSV (include target_win)
batch_schema = StructType([
    StructField("match_id", IntegerType(), False),
    StructField("timestamp", StringType(), False),
    StructField("home_team_id", IntegerType(), False),
    StructField("away_team_id", IntegerType(), False),
    StructField("home_score_total", IntegerType(), False),
    StructField("away_score_total", IntegerType(), False),
    StructField("home_sets_won", IntegerType(), False),
    StructField("away_sets_won", IntegerType(), False),
    StructField("score_diff", IntegerType(), False),
    StructField("set_diff", IntegerType(), False),
    StructField("home_current_score", IntegerType(), False),
    StructField("away_current_score", IntegerType(), False),
    StructField("set_info", StringType(), False),
    StructField("game_duration", StringType(), False),
    StructField("match_status", StringType(), False),
    StructField("home_win_rate_last5", DoubleType(), False),
    StructField("away_win_rate_last5", DoubleType(), False),
    StructField("head_to_head_win_rate_home", DoubleType(), False),
    StructField("target_win", IntegerType(), False)
])
batch_df = (spark.read
    .option("header","true")
    .schema(batch_schema)
    .csv("/data/trainer_model.csv")
    .withColumn("game_duration", parse_duration(col("game_duration")))
    .filter(col("target_win").isNotNull())
)

# Feature numeriche e categoriali
num_cols = [
    "home_score_total","away_score_total",
    "home_sets_won","away_sets_won",
    "score_diff","set_diff",
    "home_current_score","away_current_score",
    "game_duration",
    "home_win_rate_last5","away_win_rate_last5",
    "head_to_head_win_rate_home"
]
cat_cols = ["home_team_id","away_team_id"]

# 3.1) Stage di imputazione
imputer = Imputer(
    inputCols=num_cols,
    outputCols=[f"{c}_imp" for c in num_cols]
)

# 3.2) StringIndexer + OneHotEncoder
indexers = [
    StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep")
    for c in cat_cols
]
encoders = [
    OneHotEncoder(inputCol=f"{c}_idx", outputCol=f"{c}_ohe")
    for c in cat_cols
]

# 3.3) VectorAssembler + RandomForest
assembler = VectorAssembler(
    inputCols=[f"{c}_imp" for c in num_cols] + [f"{c}_ohe" for c in cat_cols],
    outputCol="features"
)
rf = RandomForestClassifier(
    featuresCol="features",
    labelCol="target_win",
    numTrees=100,
    maxDepth=8,
    seed=42
)

pipeline = Pipeline(stages=[imputer] + indexers + encoders + [assembler, rf])
model = pipeline.fit(batch_df)

# Calcola mediane per streaming fillna
medians = {
    c: float(batch_df.approxQuantile(c, [0.5], 0.001)[0])
    for c in num_cols
}

# (Opzionale) salva il modello su disco
model.write().overwrite().save("/data/models/volley/latest")



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

""""""""""
#---------------------- Apply Model -----------------------
# 5) Preprocess streaming: parse_duration + fillna
stream_prepped = (processed_df
    .withColumn("game_duration", parse_duration(col("game_duration")))
    .na.fill(medians)
)

# 6) Applica la pipeline già fit in memoria
scored = (model
    .transform(stream_prepped)
    .withColumn("predicted_win", col("probability")[1])
    .drop("rawPrediction", "probability", "features")
)
"""""""""""


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
