#!/usr/bin/env python3
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, lit, log, pow, udf,
    to_timestamp, countDistinct, expr
)
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, DoubleType, StringType
)
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Imputer, StringIndexer, OneHotEncoder,
    VectorAssembler, StandardScaler
)
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator
)
from pyspark.ml.functions import vector_to_array

def main():
    # 1. Inizializza SparkSession
    spark = SparkSession.builder \
        .appName("ValutazioneModelloTemporaleFix") \
        .getOrCreate()

    # 2. Definizione UDF
    @udf(returnType=DoubleType())
    def parse_duration(s: str) -> float:
        if s is None: return None
        m = re.search(r"(\d+)m", s)
        sec = re.search(r"(\d+)s", s)
        mins = float(m.group(1)) if m else 0.0
        secs = float(sec.group(1)) if sec else 0.0
        return mins * 60.0 + secs

    @udf(returnType=IntegerType())
    def compute_current_set_number(status: str) -> int:
        if status is None: return 1
        s = status.lower().strip()
        if s.startswith("1"): return 1
        if s.startswith("2"): return 2
        if s.startswith("3"): return 3
        if "1st" in s: return 1
        if "2nd" in s: return 2
        if "3rd" in s: return 3
        return 1

    @udf(returnType=DoubleType())
    def extract_current_set_diff(set_info: str, overall_diff: float) -> float:
        if set_info is None: return overall_diff
        parts = set_info.split("|")
        last = parts[-1].strip()
        if ":" not in last: return overall_diff
        try:
            score = last.split(":")[1].strip()
            a, b = score.split("-")
            return float(a) - float(b)
        except:
            return overall_diff

    @udf(returnType=DoubleType())
    def compute_set_importance(hsw, asw, csn) -> float:
        hs = hsw or 0.0
        aw = asw or 0.0
        cs = csn or 1
        if cs == 3 and hs == 1.0 and aw == 1.0: return 1.0
        if cs == 2 and ((hs == 1.0 and aw == 0.0) or (aw == 1.0 and hs == 0.0)): return 1.0
        return 0.5

    @udf(returnType=DoubleType())
    def compute_home_win_rate_adj(hw5, hcs, acs, sd, sdc, csn, si):
        # se mancano parametri, ritorna un valore di fallback
        if hw5 is None or hcs is None or acs is None or sd is None or sdc is None or csn is None or si is None:
            return float(hw5 or 0.0) * float(si or 1.0)
        # altrimenti procedi
        base = hw5
        if csn == 3 and sdc <= -3.0:
            adj = base * 0.05
        elif ((hcs >= 20.0) or (acs >= 20.0)) and (sd <= -2.0):
            adj = base * 0.25
        else:
            adj = base
        return adj * si

    @udf(returnType=DoubleType())
    def compute_away_win_rate_adj(aw5, hcs, acs, sd, sdc, csn, si):
        # se mancano parametri, ritorna un valore di fallback
        if aw5 is None or hcs is None or acs is None or sd is None or sdc is None or csn is None or si is None:
            return float(aw5 or 0.0) * float(si or 1.0)
        # altrimenti procedi
        base = aw5
        if csn == 3 and sdc >= 3.0:
            adj = base * 0.05
        elif ((hcs >= 20.0) or (acs >= 20.0)) and (sd >= 2.0):
            adj = base * 0.25
        else:
            adj = base
        return adj * si


    # 3. Schema e caricamento dati
    schema = StructType([
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
        StructField("target_win", IntegerType(), False),
    ])

    df = (spark.read
          .option("header", "true")
          .schema(schema)
          .csv("spark/data/trainer_model.csv")
          .withColumn("game_duration", parse_duration(col("game_duration")))
          .filter(col("target_win").isNotNull())
          .withColumn("ts", to_timestamp("timestamp", "yyyy-MM-dd HH:mm:ss.SSSSSS"))
    )

    # 4. Distribuzione delle classi
    print("=== Distribuzione classe target ===")
    df.groupBy("target_win").count().show()

    # 5. Split per match_id (train su 80% dei match, test sui restanti 20%)
    all_ids = df.select("match_id").distinct().rdd.map(lambda r: r[0]).collect()
    import random
    random.seed(42)
    random.shuffle(all_ids)
    cutoff_idx = int(len(all_ids) * 0.8)
    train_ids = set(all_ids[:cutoff_idx])
    test_ids  = set(all_ids[cutoff_idx:])

    train_df = df.filter(col("match_id").isin(train_ids))
    test_df  = df.filter(col("match_id").isin(test_ids))

    print("=== Match count train/test per match_id split ===")
    print(f"Train match_id: {len(train_ids)}, Test match_id: {len(test_ids)}")
    train_df.groupBy("target_win").count().show()
    test_df.groupBy("target_win").count().show()



    print("=== Distribuzione in train/test ===")
    train_df.groupBy("target_win").count().show()
    test_df.groupBy("target_win").count().show()

    # 6. Verifica leakage su match_id
    n_train = train_df.select(countDistinct("match_id")).first()[0]
    n_test  = test_df.select(countDistinct("match_id")).first()[0]
    n_common= train_df.select("match_id").intersect(test_df.select("match_id")).count()
    print(f"Match unici train: {n_train}, test: {n_test}, comuni: {n_common}")

    # 7. Feature engineering
    def fe(df_in):
        return (df_in
            .withColumn("set_diff_current", extract_current_set_diff(col("set_info"), col("score_diff")))
            .withColumn("current_set_number", compute_current_set_number(col("match_status")))
            .withColumn("set_importance", compute_set_importance(col("home_sets_won"), col("away_sets_won"), col("current_set_number")))
            .withColumn("home_win_rate_adj", compute_home_win_rate_adj(
                col("home_win_rate_last5"), col("home_current_score"), col("away_current_score"),
                col("score_diff"), col("set_diff_current"), col("current_set_number"), col("set_importance")
            ))
            .withColumn("away_win_rate_adj", compute_away_win_rate_adj(
                col("away_win_rate_last5"), col("home_current_score"), col("away_current_score"),
                col("score_diff"), col("set_diff_current"), col("current_set_number"), col("set_importance")
            ))
            .withColumn("win_rate_diff", col("home_win_rate_adj") - col("away_win_rate_adj"))
            .withColumn("set_diff_current", col("set_diff_current") * lit(2.0))
            .withColumn("home_win_rate_last5", col("home_win_rate_last5") * lit(0.5))
            .withColumn("away_win_rate_last5", col("away_win_rate_last5") * lit(0.5))
            .withColumn("head_to_head_win_rate_home", col("head_to_head_win_rate_home") * lit(0.5))
        )

    train_feat = fe(train_df)
    test_feat  = fe(test_df)

    # 8. Definizione pipeline
    num_orig = [
        "home_score_total","away_score_total","home_sets_won","away_sets_won",
        "score_diff","set_diff","home_current_score","away_current_score",
        "game_duration","home_win_rate_last5","away_win_rate_last5","head_to_head_win_rate_home"
    ]
    num_all = num_orig + [
        "set_diff_current","current_set_number","set_importance",
        "home_win_rate_adj","away_win_rate_adj","win_rate_diff"
    ]
    cat_cols = ["home_team_id","away_team_id"]

    imputer  = Imputer(inputCols=num_all, outputCols=[f"{c}_imp" for c in num_all])
    indexers = [StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep") for c in cat_cols]
    encoders = [OneHotEncoder(inputCol=f"{c}_idx", outputCol=f"{c}_ohe") for c in cat_cols]
    assembler = VectorAssembler(inputCols=[f"{c}_imp" for c in num_all] + [f"{c}_ohe" for c in cat_cols],
                                outputCol="assembled_features")
    scaler    = StandardScaler(inputCol="assembled_features", outputCol="features", withMean=True, withStd=True)
    lr = LogisticRegression(featuresCol="features", labelCol="target_win", maxIter=100,
                            regParam=1.0, elasticNetParam=0.0)

    pipeline = Pipeline(stages=[imputer] + indexers + encoders + [assembler, scaler, lr])

    # 9. Addestramento e predizioni
    model = pipeline.fit(train_feat)
    preds = model.transform(test_feat).withColumn("prob", vector_to_array(col("probability"))[1])

    # 10. Clipping delle probabilità
    preds = preds.withColumn("p_clipped",
        expr("CASE WHEN prob < 1e-15 THEN 1e-15 WHEN prob > 1-1e-15 THEN 1-1e-15 ELSE prob END")
    )

    # 11. Calcolo metriche
    acc     = MulticlassClassificationEvaluator(labelCol="target_win",
                                                 predictionCol="prediction",
                                                 metricName="accuracy").evaluate(preds)
    auc     = BinaryClassificationEvaluator(labelCol="target_win",
                                             rawPredictionCol="rawPrediction",
                                             metricName="areaUnderROC").evaluate(preds)
    logloss = preds.withColumn("logloss", -(
                 col("target_win") * log(col("p_clipped")) +
                 (1 - col("target_win")) * log(1 - col("p_clipped"))
               )).selectExpr("avg(logloss)").first()[0]
    brier   = preds.withColumn("brier", pow(col("p_clipped") - col("target_win"), 2))\
                   .selectExpr("avg(brier)").first()[0]

    print("=== Metriche su test set (time split) ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"AUC-ROC:  {auc:.4f}")
    print(f"Log Loss: {logloss:.4f}")
    print(f"Brier:    {brier:.4f}")

    # 12. Confusion matrix e falsi negativi
    print("=== Confusion Matrix ===")
    preds.groupBy("target_win", "prediction").count().show()
    print("=== False Negatives ===")
    preds.filter((col("target_win") == 1) & (col("prediction") == 0))\
         .show(10, truncate=False)

    spark.stop()

if __name__ == "__main__":
    main()
