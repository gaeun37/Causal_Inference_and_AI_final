# 시위는 개선을 부르는가, 통제를 부르는가?
## 1912년 Lawrence Textile Strike 신문기사 기반 인과 프레이밍 분석

Causal Inference and AI 기말 프로젝트 · Track B: 인문 데이터의 관계 분석  
자료 출처: Library of Congress / Chronicling America

---

## 1. Project Overview

이 repository는 1912년 Lawrence Textile Strike, 즉 “Bread and Roses” 파업을 둘러싼 신문 보도를 인과 프레이밍 관점에서 분석한 기말 프로젝트 제출물이다. 핵심 질문은 다음과 같다.

> 신문 지면은 Lawrence Strike를 개선의 원인으로 구성했는가, 아니면 혼란과 통제의 원인으로 구성했는가?

분석의 목적은 단순한 신문 기사 요약이 아니라, 신문 텍스트 안에서 시위 압력 프레이밍이 개선 반응 또는 질서 통제 반응과 어떤 인과적 관계를 갖는지 모델링하는 것이다. 이를 위해 OCR 자료를 정제하고, 인과 프레이밍을 추출한 뒤, Knowledge Graph와 Causal DAG로 구조화하였다. 이후 신문 맥락 Z를 혼란변수로 두고 demo-coded data를 이용한 backdoor adjustment를 수행하였다.

이 repository는 코드, 정제 데이터, Knowledge Graph/DAG export, figure, output table, 최종 보고서를 함께 포함한다.

---

## 2. Corpus and Scope

분석 자료는 Library of Congress / Chronicling America에서 수집한 1912년 1월부터 3월까지의 Lawrence Strike 관련 신문 8개 호, 총 90쪽 OCR이다. 분석 대상 신문은 The Evening Standard, Daily Kennebec Journal, The Washington Times를 포함한다.

분석은 두 층위로 진행하였다.

- `issue-level`: 신문 호 전체의 분위기와 맥락 변수 Z를 파악하는 단위
- `article-level`: Lawrence Strike 관련 기사에서 실제 프레이밍과 근거 인용을 추출하는 단위

결과변수인 개선 반응(Y1)과 질서 통제 반응(Y2)은 파업 관련 기사에서만 코딩하였다. 반면 신문 전체의 어휘 환경은 맥락 변수 Z를 구성하는 보조 근거로 사용하였다.

---

## 3. Variables and Causal Design

| Variable | Meaning |
| -------- | ------- |
| X | 시위 압력 프레이밍 |
| M1 | 요구 정당화 프레이밍 |
| Y1 | 발전 지향 개선 반응 |
| M2 | 혼란·충돌 프레이밍 |
| Y2 | 질서 통제 반응 |
| Z | 신문 맥락 혼란변수 |

Causal DAG는 두 개의 주요 경로를 가진다.

```text
X → M1 → Y1
X → M2 → Y2
Z → X, M1, M2, Y1, Y2
```

M1과 M2는 X와 Y 사이의 causal path 위에 있는 mediator이므로 보정하지 않았다. Z는 X와 Y에 모두 영향을 줄 수 있는 맥락적 confounder로 설정하였다.

---

## 4. Main Results

Demo-coded data를 이용한 backdoor adjustment 결과는 다음과 같다.

| Outcome | Naive Difference | Adjusted Demo Effect |
| ------- | ---------------: | -------------------: |
| Y1: 개선 반응 | +0.022 | +0.101 |
| Y2: 질서 통제 반응 | +0.195 | +0.121 |

이 결과는 신문 맥락 Z를 보정하면 단순 비교에서 거의 보이지 않던 개선 경로가 약하게 나타나고, 크게 보이던 통제 경로는 일부 줄어든다는 점을 보여준다. 다만 이 수치는 실제 역사적 ATE가 아니라, 신문 프레이밍 구조를 바탕으로 구성한 demo-coded framing analysis의 결과이다.

합성 데이터에만 의존하지 않도록 실제 26개 추출에서 관찰되는 rung-1 association도 별도로 계산하였다.

| Context Z | Y1(개선) units | Y2(통제) units | Lean |
| --------- | -------------: | -------------: | ---- |
| order_focused | 0 | 2 | 통제 |
| mixed | 7 | 3 | 개선 |
| institutional | 2 | 0 | 개선 |

실제 corpus의 서술적 연관은 “초기 order_focused 보도에서는 통제 프레임이 강하고, 후반 mixed/institutional 보도에서는 개선 프레임이 더 자주 나타나는” 2단계 흐름에 가깝다.

---

## 5. Interpretation

본 프로젝트는 세 층위를 구분한다.

1. **Correlation**: 실제 추출에서 관찰되는 보정되지 않은 서술적 연관
2. **Asserted causation**: 신문이 직접 주장한 인과 관계
3. **Identified causal effect**: DAG와 식별 조건을 통해 추정 가능한 인과효과

이 corpus만으로 Lawrence Strike의 실제 역사적 causal effect를 식별할 수는 없다. 적절한 X=0 비교군, 파업 전후 임금 변화, 비파업 지역 비교, 노동법 변화 자료가 부족하기 때문이다. 따라서 본 프로젝트의 effect estimate는 실제 역사적 ATE가 아니라 demo-coded framing effect로 제한하여 해석한다.

---

## 6. Repository Structure

```text
.
├── README.md
├── REPRODUCIBILITY.md
├── requirements.txt
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── curated/
├── figures/
├── graph/
├── outputs/
├── report/
└── scripts/
```

| Folder | Description |
| ------ | ----------- |
| `data/raw/` | 원본 OCR 텍스트와 source URL |
| `data/cleaned/` | 정제된 OCR 텍스트와 cleaning log |
| `data/curated/` | 기사 정보, 추출 결과, demo data, 맥락 변수, entity layer |
| `graph/` | Knowledge Graph와 Causal DAG의 nodes/edges CSV |
| `figures/` | 분석 파이프라인, Knowledge Graph, Causal DAG, demo effect figure |
| `outputs/` | 인용 검증, 식별 진단, demo adjustment, sensitivity, real-corpus association 결과 |
| `report/` | 최종 보고서 |
| `scripts/` | OCR 정제, 맥락 계산, demo data 생성, corpus association, pipeline 실행 코드 |

---

## 7. Reproducibility

핵심 결과는 Python 표준 라이브러리만으로 재현할 수 있다. 외부 LLM API, 난수 생성, 인터넷 연결은 사용하지 않는다.

```bash
python scripts/clean_ocr.py
python scripts/issue_context.py
python scripts/make_demo_data.py
python scripts/corpus_cooccurrence.py
python scripts/build_pipeline.py
```

각 스크립트의 역할은 다음과 같다.

| Script | Role |
| ------ | ---- |
| `scripts/clean_ocr.py` | OCR 정제 및 cleaning log 생성 |
| `scripts/issue_context.py` | 신문 호 단위 맥락 Z 계산 및 2단계 Z 진단 |
| `scripts/make_demo_data.py` | demo-coded data 생성 |
| `scripts/corpus_cooccurrence.py` | 실제 26개 추출의 rung-1 association 계산 |
| `scripts/build_pipeline.py` | KG, DAG, demo adjustment, sensitivity, figures, outputs 생성 |

자세한 재현 절차는 `REPRODUCIBILITY.md`에 정리되어 있다.

---

## 8. Key Outputs

| Output | Description |
| ------ | ----------- |
| `graph/nodes.csv` | Knowledge Graph node export |
| `graph/edges.csv` | Knowledge Graph edge export |
| `figures/causal_dag.png` | Causal diagram |
| `outputs/demo_backdoor_adjustment_results.csv` | Naive vs adjusted demo effect |
| `outputs/sensitivity_weighting.csv` | Z weighting sensitivity |
| `outputs/sensitivity_Z_collapse.csv` | 2-level Z robustness check |
| `outputs/real_corpus_cooccurrence.csv` | 실제 추출 기반 rung-1 association |
| `outputs/quote_verification_report.csv` | OCR quote verification |
| `report/final_report_ko_6step_causal_effect_6pages.docx` | 최종 보고서 |

---

## 9. Requirements

```text
No external Python packages are required.
Tested with Python 3.10+
```
