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
python scripts/issue_context.py
python scripts/make_demo_data.py
python scripts/build_pipeline.py
```

각 스크립트의 역할은 다음과 같다.

| Script                    | Role                                                 |
| ------------------------- | ---------------------------------------------------- |
| scripts/issue_context.py  | 신문 호 단위 맥락 Z를 보조적으로 계산                               |
| scripts/make_demo_data.py | demo-coded data 생성                                   |
| scripts/build_pipeline.py | 추출 결과, KG, DAG, demo adjustment, figures, outputs 생성 |
| scripts/clean_ocr.py      | OCR 정제 및 cleaning log 생성                             |

---

## 7. Evidence and Verification

본 프로젝트는 원문 증거와 분석 결과를 분리하여 저장하였다.

* 원문 OCR은 `data/raw/ocr/`에 보존하였다.
* 정제된 OCR은 `data/cleaned/`에 저장하였다.
* 인과 프레이밍 추출 결과는 `data/curated/real_extractions.csv`에 저장하였다.
* 모든 인용문이 실제 OCR 원문에 존재하는지는 `outputs/quote_verification_report.csv`에서 확인할 수 있다.
* Knowledge Graph와 DAG는 `graph/` 폴더에서 확인할 수 있다.
* Demo adjustment와 sensitivity 결과는 `outputs/` 폴더에서 확인할 수 있다.

---

## 8. Requirements

이 프로젝트는 Python 표준 라이브러리만 사용한다.

```text
No external Python packages are required.
Tested with Python 3.10+
```

---

## 9. Final Report

최종 보고서는 LMS에 별도 제출한다.
이 repository는 재현 가능한 코드, 정제 데이터, Knowledge Graph/DAG export, 그림, 결과표를 포함한다.
