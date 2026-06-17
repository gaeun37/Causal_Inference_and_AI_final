# Reproducibility

이 문서는 본 프로젝트의 자료 구성, 실행 순서, 주요 산출물, 검증 방법을 설명한다. 핵심 파이프라인은 Python 표준 라이브러리만으로 실행되며, 외부 LLM API, 난수 생성, 인터넷 연결을 사용하지 않는다.

---

## 1. Source Data

원자료는 Library of Congress / Chronicling America에서 수집한 1912년 1~3월 Lawrence Textile Strike 관련 신문 8개 호, 90개 지면의 OCR 자료이다.

출처 정보는 다음 파일에 정리되어 있다.

```text
data/raw/source_urls.csv
```

원문 OCR 텍스트는 다음 폴더에 보존하였다.

```text
data/raw/ocr/
```

정제된 OCR 텍스트와 cleaning log는 다음 폴더에 저장된다.

```text
data/cleaned/
```

---

## 2. Run Order

주요 결과는 다음 순서로 재현할 수 있다.

```bash
python scripts/clean_ocr.py
python scripts/issue_context.py
python scripts/make_demo_data.py
python scripts/corpus_cooccurrence.py
python scripts/build_pipeline.py
```

각 스크립트의 역할은 다음과 같다.

| Script | Description |
| ------ | ----------- |
| `scripts/clean_ocr.py` | 원문 OCR을 정제하고 cleaning log를 생성한다. |
| `scripts/issue_context.py` | 신문 호 단위 맥락 변수 Z를 계산하고, 3단계 Z와 2단계 Z 진단을 생성한다. |
| `scripts/make_demo_data.py` | corpus 관찰을 바탕으로 demo-coded data를 생성한다. |
| `scripts/corpus_cooccurrence.py` | 실제 26개 추출에서 관찰되는 rung-1 association을 계산한다. |
| `scripts/build_pipeline.py` | Knowledge Graph, Causal DAG, demo adjustment, sensitivity analysis, figure, output table을 생성한다. |

원본 ALTO XML에서 OCR 텍스트를 다시 추출해야 하는 경우에만 다음 스크립트를 사용할 수 있다.

```bash
python scripts/parse_alto.py
```

일반적인 재현 과정에서는 이미 추출된 OCR 텍스트가 `data/raw/ocr/`에 포함되어 있으므로 `parse_alto.py`를 다시 실행할 필요는 없다.

---

## 3. Expected Outputs

파이프라인 실행 후 주요 산출물은 `outputs/`, `graph/`, `figures/`에 생성된다.

| File | Description |
| ---- | ----------- |
| `outputs/extraction_summary.csv` | 프레이밍 추출 요약 |
| `outputs/quote_verification_report.csv` | OCR 원문 인용 검증 결과 |
| `outputs/identification_diagnostic_table.csv` | 식별 가능성 진단 |
| `outputs/demo_backdoor_adjustment_results.csv` | naive comparison과 adjusted demo effect |
| `outputs/sensitivity_weighting.csv` | Z 가중치 민감도 분석 |
| `outputs/sensitivity_Z_collapse.csv` | 2단계 Z robustness check |
| `outputs/real_corpus_cooccurrence.csv` | 실제 추출 기반 rung-1 association |
| `graph/nodes.csv` | Knowledge Graph node export |
| `graph/edges.csv` | Knowledge Graph edge export |
| `figures/causal_dag.png` | Causal DAG figure |

---

## 4. Core Results

Demo-coded data를 이용한 backdoor adjustment 결과는 다음과 같다.

| Outcome | Naive Difference | Adjusted Demo Effect |
| ------- | ---------------: | -------------------: |
| Y1: 개선 반응 | +0.022 | +0.101 |
| Y2: 질서 통제 반응 | +0.195 | +0.121 |

Backdoor adjustment 계산에는 다음 공식을 사용하였다.

```text
P(Y=1 | do(X=x)) = Σ_z P(Y=1 | X=x, Z=z) · P(Z=z)
```

Z 가중치를 바꾸어도 결과의 방향은 유지된다.

| Outcome | Balanced P(Z) | Observed-issue P(Z) |
| ------- | ------------: | ------------------: |
| Y1: 개선 반응 | +0.101 | +0.124 |
| Y2: 질서 통제 반응 | +0.121 | +0.116 |

2단계 Z(`order_focused` vs `reform_leaning`)로 collapse한 robustness check에서도 방향은 유지된다.

| Outcome | 2-level Z adjusted effect |
| ------- | ------------------------: |
| Y1: 개선 반응 | +0.080 |
| Y2: 질서 통제 반응 | +0.138 |

위 수치들은 실제 역사적 ATE가 아니라, 신문 프레이밍 구조를 바탕으로 backdoor adjustment 절차를 시연하기 위한 demo-coded framing effect이다.

---

## 5. Evidence and Verification

인과 프레이밍 추출 결과는 다음 파일에 저장되어 있다.

```text
data/curated/real_extractions.csv
```

각 추출 항목은 원문 OCR 인용과 연결된다. 인용 검증 결과는 다음 파일에서 확인할 수 있다.

```text
outputs/quote_verification_report.csv
```

Entity/event layer는 다음 파일에 저장되어 있으며, Knowledge Graph에 `MENTIONS` 관계로 연결된다.

```text
data/curated/entities.csv
```

Knowledge Graph export는 다음 두 파일로 제공된다.

```text
graph/nodes.csv
graph/edges.csv
```

Corpus는 총 8개 issue로 구성되며, iss003은 명확한 프레이밍 추출이 없어 context-only issue node로 유지하였다.

---

## 6. Context Variable Z

신문 맥락 변수 Z는 `order_focused`, `mixed`, `institutional`의 세 범주로 구성하였다. Z 배정의 보조 근거는 다음 파일에 저장되어 있다.

```text
data/curated/issue_context_features.csv
```

strike-proximal 측정에서 데이터가 직접적으로 지지하는 분할은 `order_focused`와 `reform_leaning`의 2단계 구분이다. 따라서 `outputs/sensitivity_Z_collapse.csv`를 추가하여 2단계 Z에서도 결과 방향이 유지되는지 확인하였다.

실제 26개 추출에서 관찰되는 rung-1 association은 다음 파일에서 확인할 수 있다.

```text
outputs/real_corpus_cooccurrence.csv
```

이 값은 보정되지 않은 서술적 연관이며, 인과효과나 역사적 효과로 해석하지 않는다.

---

## 7. Environment

```text
No external Python packages are required.
Tested with Python 3.10+
```

선택적으로 figure 미리보기나 문서 변환을 수행할 때 외부 도구가 필요할 수 있으나, 핵심 분석 결과 재현에는 필요하지 않다.
