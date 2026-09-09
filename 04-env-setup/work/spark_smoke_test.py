# ============================================================
# 체크리스트 6~8번 검증 코드
# JupyterLab 노트북에 셀별로 붙여넣거나, 터미널에서
#   python spark_smoke_test.py
# 로 한 번에 실행해도 됩니다.
# ============================================================

# ── [6] SparkSession 생성 코드 정상 실행 ─────────────────────
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("env-check").getOrCreate()
print("[6] SparkSession OK — spark.version =", spark.version)

# ── [7] Spark DataFrame 생성/조회 정상 동작 ──────────────────
df = spark.createDataFrame(
    [(1.0, 2.0, 5.0), (2.0, 3.0, 8.0), (3.0, 4.0, 11.0)],
    ["x1", "x2", "y"],
)
df.show()
print("[7] DataFrame OK — 행 수 =", df.count())

# ── [8] Spark MLlib LinearRegression 실행 확인 ───────────────
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

assembler = VectorAssembler(inputCols=["x1", "x2"], outputCol="features")
train = assembler.transform(df)

lr = LinearRegression(featuresCol="features", labelCol="y")
model = lr.fit(train)

print("[8] MLlib OK — Coefficients:", model.coefficients)
print("            Intercept   :", model.intercept)

# Spark UI(체크리스트 10번) 확인을 위해 세션을 잠시 유지합니다.
input("\n브라우저에서 http://localhost:4040 (Spark UI) 접속을 확인한 뒤 Enter를 누르세요...")
spark.stop()
print("검증 완료! 세션을 종료했습니다.")
