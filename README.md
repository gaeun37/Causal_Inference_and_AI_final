# 시위는 개선을 부르는가, 통제를 부르는가?
## 1912년 Lawrence Textile Strike 신문기사 기반 인과 프레이밍 분석

Causal Inference and AI 기말 프로젝트 · Track B: 인문 데이터의 관계 분석  
자료 출처: Library of Congress / Chronicling America

---

## 1. Project Overview

이 프로젝트는 1912년 Lawrence Textile Strike, 즉 “Bread and Roses” 파업을 둘러싼 신문 보도를 분석한다. 핵심 질문은 다음과 같다.

> 신문 지면은 Lawrence Strike를 개선의 원인으로 구성했는가, 아니면 혼란과 통제의 원인으로 구성했는가?

본 프로젝트의 목표는 단순한 신문 프레이밍 요약을 넘어서, 시위 압력 프레이밍이 개선 반응 또는 질서 통제 반응과 어떤 인과적 관계를 갖는지 분석하는 것이다. 다만 자료는 1912년 신문 OCR 8개 호, 90쪽으로 구성된 텍스트 corpus이므로, 파업 전후 임금 변화, 비파업 지역 비교, 노동법 변화, 공장별 자료 없이 실제 역사적 ATE를 확정하지 않는다.

따라서 이 repository는 신문 텍스트에서 관찰 가능한 인과 프레이밍을 추출하고, 이를 Knowledge Graph와 Causal DAG로 구조화한 뒤, demo-coded data를 통해 backdoor adjustment 절차를 시연한다. 핵심은 **correlation**, **asserted causation**, **identified causal effect**를 분리하는 것이다.

---

## 2. Research Scope

이 프로젝트가 하는 일은 다음과 같다.

- Chronicling America에서 1912년 1~3월 Lawrence Strike 관련 신문 OCR 자료를 수집한다.
- OCR 원문과 정제문을 분리하여 보존한다.
- 기사 단위에서 시위 압력, 요구 정당화, 혼란 프레이밍, 개선 반응, 질서 통제 반응을 코딩한다.
- Person, Organization, Place, Event entity layer를 추가하여 Step 3의 정보 추출 요구를 보완한다.
- 추출 결과를 Knowledge Graph로 구성하여 기사, 인용문, 변수 역할을 추적 가능하게 만든다.
- Causal DAG를 통해 개선 지향 경로와 질서 통제 경로를 모델링한다.
- 신문 맥락 Z를 고려한 backdoor adjustment 절차를 demo data로 시연한다.
- 실제 corpus의 rung-1 association을 별도로 계산하여 demo result와 구분한다.

이 프로젝트가 하지 않는 일은 다음과 같다.

- Lawrence Strike가 실제로 사회 발전을 일으켰다는 역사적 인과효과를 확정하지 않는다.
- 실제 임금 변화, 노동법 변화, 공장별 고용 자료를 사용한 사회경제적 효과 추정은 수행하지 않는다.
- demo effect 수치는 실제 역사적 ATE가 아니라, 신문 프레이밍 구조를 바탕으로 한 방법론적 시연 결과이다.

---

## 3. Causal Design

본 프로젝트의 주요 변수는 다음과 같다.

| Variable | Meaning |
|---|---|
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

M1과 M2는 X와 Y 사이의 causal path 위에 있는 mediator이므로 보정하지 않는다. Z는 신문 맥락이 X와 Y에 모두 영향을 줄 수 있는 common cause 역할을 하므로 backdoor adjustment의 보정 대상으로 둔다.

---

## 4. Main Findings

Lawrence Strike는 신문 속에서 단일한 “시위 → 개선” 이야기로만 보도되지 않았다. 신문 보도 안에서는 두 가지 경쟁적 인과 프레임이 나타났다.

1. **개선 지향 경로**: 파업이 임금 문제, 조사, 청문회, 합의, 임금 인상과 연결되는 경로이다.
2. **질서 통제 경로**: 파업이 폭동, 혼란, 경찰, 민병대, 체포와 연결되는 경로이다.

Demo-coded data를 이용한 backdoor adjustment 결과는 다음과 같다.

| Outcome | Naive Difference | Adjusted Demo Effect |
|---|---:|---:|
| Y1: 개선 반응 | +0.022 | +0.101 |
| Y2: 질서 통제 반응 | +0.195 | +0.121 |

이 결과는 단순 비교에서 거의 보이지 않던 개선 신호가 Z 보정 후 약하게 나타나고, 크게 보이던 통제 신호는 일부 줄어든다는 점을 보여준다. 다만 보정된 두 값은 모두 크지 않으며, 어느 한쪽이 다른 쪽을 압도한다고 말하기 어렵다.

> 주의: 위 수치는 합성 demo-coded data에서 계산한 framing effect 시연이며, 실제 역사적 ATE가 아니다.

### 실제 corpus 관찰: rung-1 association

합성 데이터에만 의존하지 않기 위해 실제 26개 추출 자체에서 관찰되는 연관도 별도로 계산하였다.

| Context Z | Y1 개선 단위 | Y2 통제 단위 | Lean |
|---|---:|---:|---|
| order_focused | 0 | 2 | 통제 |
| mixed | 7 | 3 | 개선 |
| institutional | 2 | 0 | 개선 |

실제 corpus의 서술적 연관은 “초기 order-focused 보도에서는 통제 프레임이 강하고, 후반 mixed/institutional 보도에서는 개선 프레임이 더 많이 나타나는” 2단계 흐름에 가깝다. 이 결과는 인과효과가 아니라 보정되지 않은 association이며, demo adjustment 결과와 구분해서 해석해야 한다.

따라서 본 프로젝트의 결론은 다음과 같다.

> 실제 역사적 효과는 이 자료만으로 확정할 수 없다. 그러나 신문 프레이밍 안에서 Lawrence Strike는 초기에는 혼란과 질서 통제의 대상으로 강하게 보도되었고, 이후 조사·청문회·임금 인상·합의 보도를 통해 개선의 계기로 재구성되었다. Demo-coded framing analysis 안에서는 개선 경로와 통제 경로 모두 양의 방향을 보였지만, 효과 크기는 작고 결정적이지 않았다.

---

## 5. Repository Structure

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
|---|---|
| `data/raw/` | 원본 OCR 텍스트와 source URL |
| `data/cleaned/` | 정제된 OCR 텍스트와 cleaning log |
| `data/curated/` | 기사 정보, 추출 결과, entity layer, demo data, 맥락 변수 |
| `graph/` | Knowledge Graph와 DAG의 nodes/edges CSV |
| `figures/` | 분석 파이프라인, KG, DAG, demo effect 그림 |
| `outputs/` | 인용 검증, 식별 진단, demo adjustment, real-corpus association, 민감도 분석 결과 |
| `report/` | 최종 보고서 |
| `scripts/` | OCR 정제, 맥락 계산, demo data 생성, corpus association, pipeline 실행 코드 |

---

## 6. Reproducibility

이 프로젝트는 외부 API, LLM, 난수 생성, 인터넷 연결 없이 재현 가능하도록 구성하였다.

주요 결과는 다음 명령으로 재현할 수 있다.

```bash
python scripts/clean_ocr.py
python scripts/issue_context.py
python scripts/make_demo_data.py
python scripts/corpus_cooccurrence.py
python scripts/build_pipeline.py
```

| Script | Role |
|---|---|
| `scripts/clean_ocr.py` | OCR 정제 및 cleaning log 생성 |
| `scripts/issue_context.py` | 신문 호 단위 맥락 Z를 보조적으로 계산 |
| `scripts/make_demo_data.py` | demo-coded data 생성 |
| `scripts/corpus_cooccurrence.py` | 실제 26개 추출의 rung-1 association 계산 |
| `scripts/build_pipeline.py` | 추출 결과, KG(+entity layer), DAG, demo adjustment, sensitivity, figures, outputs 생성 |

자세한 재현 방법은 [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)를 참고한다.

---

## 7. Evidence and Verification

본 프로젝트는 원문 증거와 분석 결과를 분리하여 저장하였다.

- 원문 OCR은 `data/raw/ocr/`에 보존하였다.
- 정제된 OCR은 `data/cleaned/`에 저장하였다.
- 인과 프레이밍 추출 결과는 `data/curated/real_extractions.csv`에 저장하였다.
- Entity/event layer는 `data/curated/entities.csv`에 저장하였다.
- 모든 인용문이 실제 OCR 원문에 존재하는지는 `outputs/quote_verification_report.csv`에서 확인할 수 있다.
- Knowledge Graph와 DAG는 `graph/` 폴더에서 확인할 수 있다.
- Demo adjustment와 sensitivity 결과는 `outputs/` 폴더에서 확인할 수 있다.
- 실제 corpus의 rung-1 association은 `outputs/real_corpus_cooccurrence.csv`에서 확인할 수 있다.

---

## 8. Limitations

본 프로젝트는 다음 한계를 명시한다.

- **실제 역사적 ATE 식별 불가**: corpus는 Lawrence Strike 관련 신문 보도 중심이므로 적절한 X=0 비교군과 외부 사회경제 자료가 부족하다.
- **Demo-coded data의 성격**: adjustment 수치(+0.101, +0.121)는 실제 역사 효과가 아니라 corpus 관찰을 바탕으로 구성한 방법론적 시연이다.
- **Z의 휴리스틱 성격**: `order_focused`, `mixed`, `institutional` 구분은 원문과 어휘 근거를 바탕으로 한 맥락 분류이며 정밀한 측정변수는 아니다. 이에 2단계 Z(`order_focused` vs `reform_leaning`) robustness도 함께 제시하였다.
- **신문 정체성과 시점의 교란**: `order_focused` 층위는 The Evening Standard 1912-01-15 단일 호이고, 후반 개선 프레임은 주로 Daily Kennebec Journal과 Washington Times에서 나온다. 따라서 시간 효과와 신문 정체성 효과를 완전히 분리할 수 없다.
- **Context-only issue**: iss003은 명확한 프레이밍 추출이 없어 추출 0건이지만 전체 corpus의 일부이므로 KG에 context-only issue node로 유지하였다.

---

## 9. Requirements

이 프로젝트는 Python 표준 라이브러리만 사용한다.

```text
No external Python packages are required.
Tested with Python 3.10+
```

---

## 10. Final Report

최종 보고서는 `report/` 폴더에 포함한다. LMS에는 PDF 또는 DOCX 형식으로 별도 제출할 수 있다.
