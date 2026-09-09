#!/usr/bin/env bash
# ============================================================
# 체크리스트 자동 점검 스크립트 (실습실 컨테이너 안에서 실행)
# 사용법: bash /root/work/verify.sh
# 각 항목을 스스로 점검한 뒤, 마지막에 이 스크립트로 교차 확인하세요.
# ============================================================

PASS=0; FAIL=0

check () {  # check "항목명" "명령"
  if eval "$2" > /dev/null 2>&1; then
    echo "  ✅ $1"
    PASS=$((PASS+1))
  else
    echo "  ❌ $1"
    FAIL=$((FAIL+1))
  fi
}

echo ""
echo "══ 분석 환경 구축 체크리스트 자동 점검 ══════════════════"
check "1. Anaconda/Miniconda 설치 (conda --version)"        "conda --version"
check "2. 가상환경 'bigdata' 존재 (conda env list)"          "conda env list | grep -q bigdata"
check "3. JupyterLab 설치 (jupyter lab --version)"           "conda run -n bigdata jupyter lab --version"
check "4. Java JDK 11/17 설치 (java -version)"               "java -version 2>&1 | grep -Eq 'version \"(11|17)'"
check "5. PySpark 설치 (import pyspark)"                     "conda run -n bigdata python -c 'import pyspark'"
check "6. SparkSession 생성 가능"                            "conda run -n bigdata python -c 'from pyspark.sql import SparkSession; s=SparkSession.builder.getOrCreate(); print(s.version); s.stop()'"
check "7. DataFrame 생성/조회 동작"                          "conda run -n bigdata python -c 'from pyspark.sql import SparkSession; s=SparkSession.builder.getOrCreate(); assert s.createDataFrame([(1,)],[\"a\"]).count()==1; s.stop()'"
check "8. MLlib LinearRegression 동작"                       "conda run -n bigdata python -c '
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
s = SparkSession.builder.getOrCreate()
df = s.createDataFrame([(1.0,2.0,5.0),(2.0,3.0,8.0),(3.0,4.0,11.0)],[\"x1\",\"x2\",\"y\"])
t = VectorAssembler(inputCols=[\"x1\",\"x2\"],outputCol=\"features\").transform(df)
LinearRegression(featuresCol=\"features\",labelCol=\"y\").fit(t)
s.stop()'"
check "9. requirements.txt 존재 (/root/work)"                "test -s /root/work/requirements.txt"
echo "  ⏸  10. Spark UI(localhost:4040)는 세션 실행 중에만 열립니다."
echo "         → spark_smoke_test.py 실행 중 브라우저로 직접 확인하세요."
echo "═════════════════════════════════════════════════════════"
echo ""
echo "  결과: 통과 $PASS / 실패 $FAIL  (10번은 수동 확인)"
if [ $FAIL -eq 0 ]; then
  echo "  🎉 자동 점검 항목 전부 통과!"
fi
echo ""
