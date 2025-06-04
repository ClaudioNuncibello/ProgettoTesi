#!/usr/bin/env python3
import re
import json

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, date_format, to_timestamp,
    udf
)
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, DoubleType, StringType
)
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Imputer, StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
)
from pyspark.ml.classification import LogisticRegression

# ------------------ Spark Session ------------------
spark = SparkSession.builder \
    .appName("VolleyballSnapshotProcessor") \
    .config("spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
        "org.elasticsearch:elasticsearch-spark-30_2.12:8.7.1") \
    .config("spark.sql.parquet.compression.codec", "uncompressed") \
    .getOrCreate()


# ------------------ UDFs per feature engineering ------------------

@udf("double")
def parse_duration(s: str) -> float:
    if s is None:
        return None
    m = re.search(r"(\d+)m", s)
    sec = re.search(r"(\d+)s", s)
    mins = float(m.group(1)) if m else 0.0
    secs = float(sec.group(1)) if sec else 0.0
    return mins * 60.0 + secs

@udf("integer")
def compute_current_set_number(match_status: str) -> int:
    if match_status is None:
        return 1
    s = match_status.lower().strip()
    if s.startswith("1"):
        return 1
    if s.startswith("2"):
        return 2
    if s.startswith("3"):
        return 3
    if "1st" in s:
        return 1
    if "2nd" in s:
        return 2
    if "3rd" in s:
        return 3
    return 1

@udf("double")
def extract_current_set_diff(set_info: str, overall_diff: float) -> float:
    if set_info is None:
        return overall_diff
    parts = set_info.split("|")
    last = parts[-1].strip()
    if ":" not in last:
        return overall_diff
    try:
        score_part = last.split(":")[1].strip()
        a, b = score_part.split("-")
        return float(a) - float(b)
    except:
        return overall_diff

@udf("double")
def compute_set_importance(home_sets_won: float, away_sets_won: float, current_set_number: int) -> float:
    hs = home_sets_won or 0.0
    aw = away_sets_won or 0.0
    cs = current_set_number or 1
    if cs == 3 and hs == 1.0 and aw == 1.0:
        return 1.0
    if cs == 2 and ((hs == 1.0 and aw == 0.0) or (aw == 1.0 and hs == 0.0)):
        return 1.0
    return 0.5

@udf("double")
def compute_home_win_rate_adj(home_win_rate_last5: float,
                              home_current_score: float,
                              away_current_score: float,
                              score_diff: float,
                              set_diff_current: float,
                              current_set_number: int,
                              set_importance: float) -> float:
    base = home_win_rate_last5 or 0.0
    sd = set_diff_current or 0.0
    cs = current_set_number or 1
    if cs == 3 and sd <= -3.0:
        adj = base * 0.05
    elif ((home_current_score >= 20.0) or (away_current_score >= 20.0)) and (score_diff <= -2.0):
        adj = base * 0.25
    else:
        adj = base
    return adj * set_importance

@udf("double")
def compute_away_win_rate_adj(away_win_rate_last5: float,
                              home_current_score: float,
                              away_current_score: float,
                              score_diff: float,
                              set_diff_current: float,
                              current_set_number: int,
                              set_importance: float) -> float:
    base = away_win_rate_last5 or 0.0
    sd = set_diff_current or 0.0
    cs = current_set_number or 1
    if cs == 3 and sd >= 3.0:
        adj = base * 0.05
    elif ((home_current_score >= 20.0) or (away_current_score >= 20.0)) and (score_diff >= 2.0):
        adj = base * 0.25
    else:
        adj = base
    return adj * set_importance

@udf("integer")
def compute_flag_3set_severo_home(current_set_number: int, set_diff_current: float) -> int:
    return 1 if (current_set_number == 3 and set_diff_current <= -3.0) else 0

@udf("integer")
def compute_flag_3set_severo_away(current_set_number: int, set_diff_current: float) -> int:
    return 1 if (current_set_number == 3 and set_diff_current >= 3.0) else 0

@udf("integer")
def compute_flag_critico_base_home(home_current_score: float, away_current_score: float, score_diff: float) -> int:
    return 1 if (((home_current_score >= 20.0) or (away_current_score >= 20.0)) and (score_diff <= -2.0)) else 0

@udf("integer")
def compute_flag_critico_base_away(home_current_score: float, away_current_score: float, score_diff: float) -> int:
    return 1 if (((home_current_score >= 20.0) or (away_current_score >= 20.0)) and (score_diff >= 2.0)) else 0

# ------------------ UDF per estrarre la probabilità “classe 1” dal Vector ------------------
@udf("double")
def extract_prob(v):
    return float(v[1])  # prende il secondo elemento di probability: prob(T=1)



# ------------------ BATCH TRAINING sul CSV (include target_win) ------------------
batch_schema = StructType([
    StructField("match_id", IntegerType(), False),
    StructField("timestamp", StringType(), False),
    StructField("home_team_id", IntegerType(), False),
    StructField("away_team_id", IntegerType(), False),
    StructField("home_score_total", DoubleType(), False),
    StructField("away_score_total", DoubleType(), False),
    StructField("home_sets_won", DoubleType(), False),
    StructField("away_sets_won", DoubleType(), False),
    StructField("score_diff", DoubleType(), False),
    StructField("set_diff", DoubleType(), False),
    StructField("home_current_score", DoubleType(), False),
    StructField("away_current_score", DoubleType(), False),
    StructField("set_info", StringType(), False),
    StructField("game_duration", StringType(), False),
    StructField("match_status", StringType(), False),
    StructField("home_win_rate_last5", DoubleType(), False),
    StructField("away_win_rate_last5", DoubleType(), False),
    StructField("head_to_head_win_rate_home", DoubleType(), False),
    StructField("target_win", IntegerType(), False)
])

batch_df = (spark.read
    .option("header", "true")
    .schema(batch_schema)
    .csv("/data/trainer_model.csv")
    .withColumn("game_duration", parse_duration(col("game_duration")))
    .filter(col("target_win").isNotNull())
)

# ------------------ Aggiungi feature avanzate al batch ------------------
batch_feat = (
    batch_df
    .withColumn("set_diff_current",
                extract_current_set_diff(col("set_info"), col("score_diff")))
    .withColumn("current_set_number", compute_current_set_number(col("match_status")))
    .withColumn("set_importance",
                compute_set_importance(col("home_sets_won"), col("away_sets_won"), col("current_set_number")))
    .withColumn("flag_3set_severo_home",
                compute_flag_3set_severo_home(col("current_set_number"), col("set_diff_current")))
    .withColumn("flag_3set_severo_away",
                compute_flag_3set_severo_away(col("current_set_number"), col("set_diff_current")))
    .withColumn("flag_critico_base_home",
                compute_flag_critico_base_home(col("home_current_score"), col("away_current_score"), col("score_diff")))
    .withColumn("flag_critico_base_away",
                compute_flag_critico_base_away(col("home_current_score"), col("away_current_score"), col("score_diff")))
    .withColumn("home_win_rate_adj",
                compute_home_win_rate_adj(
                    col("home_win_rate_last5"),
                    col("home_current_score"),
                    col("away_current_score"),
                    col("score_diff"),
                    col("set_diff_current"),
                    col("current_set_number"),
                    col("set_importance")
                ))
    .withColumn("away_win_rate_adj",
                compute_away_win_rate_adj(
                    col("away_win_rate_last5"),
                    col("home_current_score"),
                    col("away_current_score"),
                    col("score_diff"),
                    col("set_diff_current"),
                    col("current_set_number"),
                    col("set_importance")
                ))
    .withColumn("win_rate_diff", col("home_win_rate_adj") - col("away_win_rate_adj"))
)

# ------------------ Definizione colonne numeriche e categoriali ------------------
num_cols_original = [
    "home_score_total", "away_score_total",
    "home_sets_won", "away_sets_won",
    "score_diff", "set_diff",
    "home_current_score", "away_current_score",
    "game_duration",
    "home_win_rate_last5", "away_win_rate_last5",
    "head_to_head_win_rate_home"
]
# Le “nuove” feature non entrano in medians_original
num_cols_all = num_cols_original + [
    "set_diff_current", "current_set_number", "set_importance",
    "home_win_rate_adj", "away_win_rate_adj", "win_rate_diff"
]
cat_cols = ["home_team_id", "away_team_id"]


# ------------------ Calcolo mediane SOLO sulle colonne originali ------------------
medians_original = {
    c: float(batch_feat.approxQuantile(c, [0.5], 0.001)[0])
    for c in num_cols_original
}


# ------------------ Costruzione pipeline di feature + LogisticRegression ------------------

# 1) Imputer per tutte le numeriche (incluse quelle avanzate)
imputer = Imputer(
    inputCols=num_cols_all,
    outputCols=[f"{c}_imp" for c in num_cols_all]
)

# 2) StringIndexer + OneHotEncoder per categoriali
indexers = [
    StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep")
    for c in cat_cols
]
encoders = [
    OneHotEncoder(inputCol=f"{c}_idx", outputCol=f"{c}_ohe")
    for c in cat_cols
]

# 3) Assembler delle feature imp e OHE
assembler = VectorAssembler(
    inputCols=[f"{c}_imp" for c in num_cols_all] + [f"{c}_ohe" for c in cat_cols],
    outputCol="assembled_features"
)

# 4) StandardScaler per centrare e scalare
scaler = StandardScaler(
    inputCol="assembled_features",
    outputCol="features",
    withMean=True,
    withStd=True
)

# 5) LogisticRegression
lr = LogisticRegression(
    featuresCol="features",
    labelCol="target_win",
    maxIter=100,
    regParam=1.0,
    elasticNetParam=0.0,
    probabilityCol="probability"
)

pipeline = Pipeline(stages=[imputer] + indexers + encoders + [assembler, scaler, lr])
model = pipeline.fit(batch_feat)

# Salva il modello su disco
model.write().overwrite().save("/data/models/volley_logreg/latest")


# ------------------ Schema Definition per streaming ------------------
snapshot_schema = StructType([
    StructField("match_id", IntegerType(), nullable=False),
    StructField("timestamp", StringType(), nullable=False),
    StructField("home_team_id", IntegerType(), nullable=False),
    StructField("away_team_id", IntegerType(), nullable=False),
    StructField("home_score_total", DoubleType(), nullable=False),
    StructField("away_score_total", DoubleType(), nullable=False),
    StructField("home_sets_won", DoubleType(), nullable=False),
    StructField("away_sets_won", DoubleType(), nullable=False),
    StructField("score_diff", DoubleType(), nullable=False),
    StructField("set_diff", DoubleType(), nullable=False),
    StructField("home_current_score", DoubleType(), nullable=False),
    StructField("away_current_score", DoubleType(), nullable=False),
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

# ------------------ Convert String → TimestampType ------------------
processed_df = parsed_df.withColumn(
    "timestamp",
    date_format(
        to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss.SSSSSS"),
        "yyyy-MM-dd HH:mm:ss.SSSSSS"
    )
)

# ------------------ Preprocess streaming: parse_duration + fillna sulle colonne originali ------------------
stream_base = (
    processed_df
    .withColumn("game_duration", parse_duration(col("game_duration")))
    .na.fill(medians_original)
)

# ------------------ Aggiungi feature avanzate allo streaming ------------------
stream_feat = (
    stream_base
    .withColumn("set_diff_current",
                extract_current_set_diff(col("set_info"), col("score_diff")))
    .withColumn("current_set_number", compute_current_set_number(col("match_status")))
    .withColumn("set_importance",
                compute_set_importance(col("home_sets_won"), col("away_sets_won"), col("current_set_number")))
    .withColumn("flag_3set_severo_home",
                compute_flag_3set_severo_home(col("current_set_number"), col("set_diff_current")))
    .withColumn("flag_3set_severo_away",
                compute_flag_3set_severo_away(col("current_set_number"), col("set_diff_current")))
    .withColumn("flag_critico_base_home",
                compute_flag_critico_base_home(col("home_current_score"), col("away_current_score"), col("score_diff")))
    .withColumn("flag_critico_base_away",
                compute_flag_critico_base_away(col("home_current_score"), col("away_current_score"), col("score_diff")))
    .withColumn("home_win_rate_adj",
                compute_home_win_rate_adj(
                    col("home_win_rate_last5"),
                    col("home_current_score"),
                    col("away_current_score"),
                    col("score_diff"),
                    col("set_diff_current"),
                    col("current_set_number"),
                    col("set_importance")
                ))
    .withColumn("away_win_rate_adj",
                compute_away_win_rate_adj(
                    col("away_win_rate_last5"),
                    col("home_current_score"),
                    col("away_current_score"),
                    col("score_diff"),
                    col("set_diff_current"),
                    col("current_set_number"),
                    col("set_importance")
                ))
    .withColumn("win_rate_diff", col("home_win_rate_adj") - col("away_win_rate_adj"))
)

# ------------------ Applica il modello ------------------
scored = model.transform(stream_feat)

# ------------------ Seleziona solo le colonne richieste dal mapping Elasticsearch ------------------
final_cols = [
    "match_id",
    "timestamp",
    "home_team_id",
    "away_team_id",
    "home_score_total",
    "away_score_total",
    "home_sets_won",
    "away_sets_won",
    "score_diff",
    "set_diff",
    "home_current_score",
    "away_current_score",
    "set_info",
    "game_duration",
    "match_status",
    "home_win_rate_last5",
    "away_win_rate_last5",
    "head_to_head_win_rate_home",
    "predicted_win"
]

output_df = scored \
    .withColumn("predicted_win", extract_prob(col("probability"))) \
    .select(*final_cols)


# ------------------ Write to Elasticsearch ------------------
es_query = output_df.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch-volley") \
    .option("es.port", "9200") \
    .option("es.resource", "volleyball_matches") \
    .option("es.write.operation", "index") \
    .option("checkpointLocation", "/tmp/spark-es-logreg-checkpoint") \
    .outputMode("append") \
    .start()

# ------------------ Await Termination ------------------
es_query.awaitTermination()
