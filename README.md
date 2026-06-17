# 시위는 개선을 부르는가, 통제를 부르는가?

## 1912년 Lawrence Textile Strike 신문기사 기반 인과 프레이밍 분석

Causal Inference and AI 기말 프로젝트
Track B: 인문 데이터의 관계 분석
자료 출처: Library of Congress / Chronicling America

---

## 1. Project Overview

이 프로젝트는 1912년 Lawrence Textile Strike, 즉 “Bread and Roses” 파업을 둘러싼 신문 보도를 분석한다.
핵심 질문은 다음과 같다.

> 신문 지면은 Lawrence 파업을 개선의 계기로 보도했는가, 아니면 혼란과 통제의 대상으로 보도했는가?

본 프로젝트는 실제 역사에서 파업이 사회 발전을 직접 일으켰는지를 확정적으로 증명하지 않는다.
그 대신, 당시 신문 OCR 자료에서 관찰 가능한 인과 프레이밍을 추출하고, 이를 Knowledge Graph와 Causal DAG로 구조화한 뒤, demo-coded data를 통해 backdoor adjustment 절차를 시연한다.

---

## 2. Research Scope

이 프로젝트가 하는 일은 다음과 같다.

* Chronicling America에서 1912년 1~3월 Lawrence Strike 관련 신문 OCR 자료를 수집한다.
* OCR 원문과 정제문을 분리하여 보존한다.
* 기사 단위에서 시위 압력, 요구 정당화, 혼란 프레이밍, 개선 반응, 질서 통제 반응을 코딩한다.
* 추출 결과를 Knowledge Graph로 구성하여 기사, 인용문, 변수 역할을 추적 가능하게 만든다.
* Causal DAG를 통해 개선 지향 경로와 질서 통제 경로를 모델링한다.
* 신문 맥락 Z를 고려한 backdoor adjustment 절차를 demo data로 시연한다.

이 프로젝트가 하지 않는 일은 다음과 같다.

* Lawrence Strike가 실제로 사회 발전을 일으켰다는 역사적 인과효과를 확정하지 않는다.
* 실제 임금 변화, 노동법 변화, 공장별 고용 자료를 사용한 사회경제적 효과 추정은 수행하지 않는다.
* 모든 효과 수치는 실제 역사적 ATE가 아니라, 신문 프레이밍 구조를 바탕으로 한 방법론적 시연 결과이다.

---

## 3. Causal Design

본 프로젝트의 주요 변수는 다음과 같다.

| Variable | Meaning     |
| -------- | ----------- |
| X        | 시위 압력 프레이밍  |
| M1       | 요구 정당화 프레이밍 |
| Y1       | 발전 지향 개선 반응 |
| M2       | 혼란·충돌 프레이밍  |
| Y2       | 질서 통제 반응    |
| Z        | 신문 맥락 혼란변수  |

Causal DAG는 두 개의 주요 경로를 가진다.

```text
X → M1 → Y1
X → M2 → Y2
Z → X, M1, M2, Y1, Y2
```

M1과 M2는 매개변수이므로 보정하지 않는다.
Z는 X와 Y에 모두 영향을 줄 수 있는 맥락적 혼란변수이므로 backdoor adjustment의 보정 대상으로 둔다.

---

## 4. Main Findings

분석 결과, Lawrence Strike는 신문 속에서 단일한 “시위 → 개선” 이야기로만 보도되지 않았다.

신문 보도 안에서는 두 가지 경쟁적 인과 프레임이 나타났다.

1. **개선 지향 경로**
   파업이 임금 문제, 조사, 청문회, 합의, 임금 인상과 연결되는 경로이다.

2. **질서 통제 경로**
   파업이 폭동, 혼란, 경찰, 민병대, 체포와 연결되는 경로이다.

Demo-coded data를 이용한 backdoor adjustment 결과는 다음과 같다.

| Outcome      | Naive Difference | Adjusted Demo Effect |
| ------------ | ---------------: | -------------------: |
| Y1: 개선 반응    |           +0.022 |               +0.101 |
| Y2: 질서 통제 반응 |           +0.195 |               +0.121 |

이 결과는 신문 프레이밍 안에서 질서 통제 경로가 더 즉각적이고 표면적으로 강하게 나타났음을 보여준다.
개선 경로는 단순 비교에서는 거의 보이지 않지만, 신문 맥락 Z를 보정한 뒤 약하게 나타난다.

> **주의:** 위 수치는 합성(demo) 데이터에서 계산된 *방법 시연*이며 역사적 효과가 아니다.

### 실제 corpus 관찰 (rung 1, 합성 아님)

합성 데이터에만 의존하지 않도록, 실제 26개 추출 자체에서 관찰되는 연관도 별도로 기록하였다
(`outputs/real_corpus_cooccurrence.csv`, `scripts/corpus_cooccurrence.py`).

| Context Z (실제 추출) | Y1(개선) 단위 | Y2(통제) 단위 | lean |
| ------------------- | ---------: | ---------: | ---- |
| order_focused       |          0 |          2 | 통제 |
| mixed               |          7 |          3 | 개선 |
| institutional       |          2 |          0 | 개선 |

실제 corpus에서는 후반 보도일수록 개선 프레임(Y1)이 오히려 더 많이 나타난다.
즉 "통제가 더 강하다"는 인상은 (a) 합성 데이터 설계와 (b) 단일 order_focused 신문 호에서 주로 기인한다.
이 대비 자체가 *correlation*과 *demo-adjusted 시연*을 구분해 보여 주는 장치이다.

따라서 본 프로젝트의 결론은 다음과 같다.

> 실제 역사적 효과는 이 자료만으로 확정할 수 없다.
> 그러나 신문 프레이밍 안에서 Lawrence Strike는 먼저 혼란과 질서 통제의 대상으로 강하게 보도되었고, 이후 조사·청문회·임금 인상·합의 보도를 통해 제한적으로 개선의 계기로 재구성되었다.

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
└── scripts/
```

각 폴더의 역할은 다음과 같다.

| Folder        | Description                                  |
| ------------- | -------------------------------------------- |
| data/raw/     | 원본 OCR 텍스트와 source URL                       |
| data/cleaned/ | 정제된 OCR 텍스트와 cleaning log                    |
| data/curated/ | 기사 정보, 추출 결과, demo data, 맥락 변수               |
| graph/        | Knowledge Graph와 Causal DAG의 nodes/edges CSV |
| figures/      | 분석 파이프라인, KG, DAG, demo effect 그림            |
| outputs/      | 인용 검증, 식별 진단, demo adjustment, 민감도 분석 결과     |
| scripts/      | OCR 정제, 맥락 계산, demo data 생성, pipeline 실행 코드  |

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

각 스크립트의 역할은 다음과 같다.

| Script                        | Role                                                 |
| ----------------------------- | ---------------------------------------------------- |
| scripts/clean_ocr.py          | OCR 정제 및 cleaning log 생성                             |
| scripts/issue_context.py      | 신문 호 단위 맥락 Z를 보조적으로 계산 (3단계 vs 2단계 진단 포함)            |
| scripts/make_demo_data.py     | demo-coded data 생성                                   |
| scripts/corpus_cooccurrence.py | 실제 26개 추출의 rung-1 연관 (합성 아님) 계산                       |
| scripts/build_pipeline.py     | 추출 결과, KG(+entity layer), DAG, demo adjustment, 민감도, figures, outputs 생성 |

---

## 7. Evidence and Verification

본 프로젝트는 원문 증거와 분석 결과를 분리하여 저장하였다.

* 원문 OCR은 `data/raw/ocr/`에 보존하였다.
* 정제된 OCR은 `data/cleaned/`에 저장하였다.
* 인과 프레이밍 추출 결과는 `data/curated/real_extractions.csv`에 저장하였다.
* 모든 인용문이 실제 OCR 원문에 존재하는지는 `outputs/quote_verification_report.csv`에서 확인할 수 있다.
* Knowledge Graph와 DAG는 `graph/` 폴더에서 확인할 수 있다.
* Demo adjustment와 sensitivity 결과는 `outputs/` 폴더에서 확인할 수 있다.
* 실제 corpus의 rung-1 연관은 `outputs/real_corpus_cooccurrence.csv`에서 확인할 수 있다.
* Entity/event layer(Person·Organization·Place·Event)는 `data/curated/entities.csv`로 코딩하여 KG에 포함하였다.

---

## 7-1. Limitations

본 프로젝트는 다음 한계를 명시한다.

* **합성 데이터의 성격.** demo adjustment 수치(+0.101, +0.121)는 연구자가 corpus 인상에 맞추어 설계한 160개 합성 단위에서 나온 *방법 시연*이며, 실제 역사적 ATE가 아니다. 합성에만 의존하지 않도록 실제 추출 기반 rung-1 연관(`real_corpus_cooccurrence.csv`)을 함께 제시한다.
* **혼란변수 Z의 두께.** `issue_context.py`의 strike-proximal 측정에서 데이터가 실제로 지지하는 분할은 `order_focused`(1개 호) vs `reform_leaning`(나머지)의 2단계이며, `mixed`/`institutional` 구분은 상당 부분 수작업 판단이다. 이에 2단계 Z로 collapse한 robustness(`sensitivity_Z_collapse.csv`)를 추가하였고, 효과의 부호는 유지된다(Y1 +0.08, Y2 +0.138).
* **신문 정체성·시점과의 교란.** `order_focused` 층위는 전적으로 The Evening Standard 1912-01-15 단일 호이고, 후반의 개선 프레임은 주로 Daily Kennebec Journal에서 나온다. 따라서 "초기 통제 → 후기 개선"이라는 시간적 서사는 신문 정체성·시점과 분리되지 않는다.
* **코딩되지 않은 호.** iss003(1912-02-09)은 corpus·정제 단계에는 포함되지만 명확한 프레이밍 단위를 추출하지 못해 추출 0건이다(Z 맥락 참고용으로만 유지).

---

## 8. Requirements

이 프로젝트는 Python 표준 라이브러리만 사용한다.

```text
No external Python packages are required.
Tested with Python 3.10+
```

---


