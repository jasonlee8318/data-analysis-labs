# 11강 — 분석 결과 해석 및 시각화

10강에서 학습한 RandomForest 이탈 예측 모델의 성능을 시각화하고
(혼동행렬, ROC 곡선, Feature Importance), 인사이트 리포트를 작성합니다.

## 실행

```bash
docker compose pull
docker compose up -d
```

http://localhost:8888/?token=interpret 접속 →
`work/result_interpretation.ipynb` 실행.

## 검증

혼동행렬 집계, ROC AUC 계산(`BinaryClassificationMetrics`),
`featureImportances` 조회까지 로컬에서 실제로 pyspark 4.2.0으로
돌려 값이 정상적으로 나오는 것을 확인한 코드입니다.

## 이 회차의 핵심

숫자(AUC=0.95 등)를 계산하는 건 10강에서 이미 했습니다. 이 회차는
그 숫자를 **① 그림으로 바꾸고 ② 비즈니스 언어로 해석하는** 데
집중합니다. 노트북 마지막의 리포트 템플릿을 "숫자 나열"이 아니라
"그래서 무엇을 해야 하는가"로 끝나도록 채우는 게 핵심 과제입니다.

## 자주 겪는 문제

- **8888/4040 포트 충돌** → compose에서 왼쪽 포트만 변경
- **matplotlib 한글 깨짐** → 이 노트북은 한글을 축 이름이 아니라
  범례/제목에 최소한으로만 사용해 큰 문제는 없지만, 완전히 깨끗하게
  보이려면 나눔고딕 등 한글 폰트를 컨테이너에 추가해야 합니다
- **초기화** → `docker compose down` 후 `up -d`
