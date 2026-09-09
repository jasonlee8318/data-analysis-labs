# 10강 — 머신러닝 분석 모듈 개발 (Spark MLlib)

고객 이탈(churn) 예측을 소재로 LogisticRegression / DecisionTree /
RandomForest 세 모델을 학습·비교하고, CrossValidator로 하이퍼파라미터를
튜닝합니다.

## 사전 준비

```bash
docker compose pull
```

## 실행

```bash
docker compose up -d
```

http://localhost:8888/?token=mllib 접속 →
`work/mllib_classification.ipynb`를 열고 순서대로 실행합니다.

## 검증

이 노트북의 로직은 실제로 로컬에서 pyspark 4.2.0으로 미리 돌려
확인했습니다 — 세 모델의 AUC/Accuracy가 정상적으로 산출되고,
CrossValidator 튜닝 후 최적 파라미터(numTrees, maxDepth)가 실제로
조회되는 것까지 확인된 코드입니다.

## 다음 회차와의 연결

이 노트북에서 나온 `results`(모델별 AUC/Accuracy)와 `best_rf`(튜닝된
모델)는 11강(분석 결과 해석 및 시각화)에서 그대로 이어받아 성능
지표를 시각화하고 인사이트 리포트를 작성하는 데 씁니다.

## 자주 겪는 문제

- **8888/4040 포트 충돌** → compose에서 왼쪽 포트만 변경
- **CrossValidator가 느림** → `grid`의 조합 수(9개) × `numFolds`(3) = 27번
  학습이 반복됩니다. 로컬 환경에서 오래 걸리면 grid 값을 2종×2종으로 줄여도 됩니다
- **초기화** → `docker compose down` 후 `up -d`
