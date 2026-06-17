# Reproducibility

이 문서는 본 프로젝트의 자료 구성, 실행 순서, 주요 산출물, 검증 방법을 설명한다. 프로젝트의 핵심 파이프라인은 Python 표준 라이브러리만으로 실행되며, LLM API, 난수 생성, 인터넷 연결을 사용하지 않는다.

---

## 1. Source Data

본 프로젝트의 원자료는 Library of Congress / Chronicling America에서 수집한 1912년 1~3월 Lawrence Textile Strike 관련 신문 자료이다. 총 8개 신문 호, 90개 지면의 OCR 자료를 사용하였다.

출처 정보는 다음 파일에 정리되어 있다.

```text
data/raw/source_urls.csv
```

원문 OCR 텍스트는 다음 폴더에 무수정 보존하였다.

```text
data/raw/ocr/
```

정제된 OCR 텍스트는 원문과 분리하여 다음 폴더에 저장하였다.

```text
data/cleaned/
```

---

## 2. How to Reproduce

주요 결과는 다음 순서로 재현할 수 있다.

```bash
python scripts/clean_ocr.py
python scripts/issue_context.py
python scripts/make_demo_data.py
python scripts/corpus_cooccurrence.py
python scripts/build_pipeline.py
```

| Script | Description |
|---|---|
| `scripts/clean_ocr.py` | 원문 OCR을 정제하고 cleaning log를 생성한다. |
| `scripts/issue_context.py` | 신문 호 단위 맥락 변수 Z를 보조적으로 계산한다. |
| `scripts/make_demo_data.py` | corpus 관찰에 근거한 demo-coded data를 생성한다. |
| `scripts/corpus_cooccurrence.py` | 실제 26개 추출의 rung-1 association을 계산한다. |
| `scripts/build_pipeline.py` | 추출 결과, Knowledge Graph(+entity layer), Causal DAG, demo adjustment, sensitivity, figure 파일을 생성한다. |

원본 ALTO XML에서 OCR 텍스트를 다시 추출해야 하는 경우에만 다음 스크립트를 사용할 수 있다.

```bash
python scripts/parse_alto.py
```

일반적인 재현 과정에서는 이미 추출된 OCR 텍스트가 `data/raw/ocr/`에 포함되어 있으므로 `parse_alto.py`를 다시 실행할 필요는 없다.

---

## 3. Expected Outputs

파이프라인을 실행하면 주요 결과 파일이 `outputs/`, `graph/`, `figures/` 폴더에 생성된다.

### 3.1 Demo backdoor adjustment

핵심 demo adjustment 결과는 다음과 같다.

| Outcome | Naive Difference | Adjusted Demo Effect |
|---|---:|---:|
| Y1: 개선 반응 | +0.022 | +0.101 |
| Y2: 질서 통제 반응 | +0.195 | +0.121 |

Backdoor adjustment 계산에는 다음 공식을 사용하였다.

```text
P(Y=1 | do(X=x)) = Σ_z P(Y=1 | X=x, Z=z) · P(Z=z)
```

이 수치들은 실제 역사적 ATE가 아니라, 신문 프레이밍 구조를 바탕으로 backdoor adjustment 절차를 시연하기 위한 demo result이다.

### 3.2 Sensitivity analysis

Z 가중치를 바꾸어도 결과의 부호는 유지된다.

| Outcome | Balanced P(Z) | Observed-issue P(Z) |
|---|---:|---:|
| Y1: 개선 반응 | +0.101 | +0.124 |
| Y2: 질서 통제 반응 | +0.121 | +0.116 |

데이터가 더 직접적으로 지지하는 2단계 Z(`order_focused` vs `reform_leaning`)로 collapse한 결과는 다음과 같다.

| Outcome | Collapsed-Z effect |
|---|---:|
| Y1: 개선 반응 | +0.080 |
| Y2: 질서 통제 반응 | +0.138 |

### 3.3 Real-corpus rung-1 association

합성 데이터에만 의존하지 않기 위해 실제 26개 추출의 보정되지 않은 association을 별도로 계산하였다.

| Context Z | Y1 개선 단위 | Y2 통제 단위 | Lean |
|---|---:|---:|---|
| order_focused | 0 | 2 | 통제 |
| mixed | 7 | 3 | 개선 |
| institutional | 2 | 0 | 개선 |

이 결과는 인과효과가 아니라 실제 corpus에서 관찰되는 descriptive association이다.

---

## 4. Evidence and Quote Verification

본 프로젝트는 텍스트 근거와 분석 결과를 분리하여 저장하였다.

인과 프레이밍 추출 결과는 다음 파일에 저장되어 있다.

```text
data/curated/real_extractions.csv
```

각 추출 항목은 원문 OCR 인용과 연결되어 있으며, 인용 검증 결과는 다음 파일에서 확인할 수 있다.

```text
outputs/quote_verification_report.csv
```

이 파일은 텍스트 기반 추출 인용이 `data/raw/ocr/`의 원문 OCR 안에 존재하는지 확인한다. 26개 추출 중 25개는 실제 인용문을 포함하며, 1개는 인용문이 없는 연구자 추가 맥락 변수 Z이다.

Entity/event layer는 다음 파일에 저장되어 있다.

```text
data/curated/entities.csv
```

---

## 5. Knowledge Graph and Causal Diagram

Knowledge Graph와 DAG export는 다음 폴더에 저장되어 있다.

```text
graph/nodes.csv
graph/edges.csv
```

KG에는 다음 유형의 node가 포함된다.

- Issue
- Article
- Extraction
- FramingClaim
- AssertedCausalClaim
- AnalystAssumption
- SupportingQuote
- Person
- Organization
- Place
- Event

전체 corpus는 8개 issue로 구성된다. iss003은 명확한 프레이밍 추출이 없어 extraction은 0건이지만, 전체 corpus의 일부이므로 context-only issue node로 유지하였다. 따라서 KG summary의 issue count는 corpus와 동일하게 8개이다.

Causal diagram과 관련 figure는 다음 폴더에 저장되어 있다.

```text
figures/
```

---

## 6. Context Variable Z

신문 맥락 변수 Z는 `order_focused`, `mixed`, `institutional`의 세 범주로 구성하였다. Z 배정의 보조 근거는 다음 파일에 저장되어 있다.

```text
data/curated/issue_context_features.csv
```

이 파일은 두 가지 방식의 어휘 정보를 포함한다.

1. 신문 호 전체 OCR에서의 개혁/제도 어휘와 혼란/통제 어휘
2. Lawrence Strike 언급 주변에서의 개혁/제도 어휘와 혼란/통제 어휘

신문 호 전체의 단순 키워드 카운트는 신문 간 차이를 충분히 구분하지 못했다. 반면 Lawrence Strike 언급 주변 어휘에서는 `order_focused` 맥락이 더 분명하게 확인되었다. 따라서 Z는 정밀한 측정변수라기보다, 원문 기사와 어휘 근거를 바탕으로 한 투명한 휴리스틱 변수로 해석해야 한다.

Z를 2단계로 collapse한 robustness result는 다음 파일에 저장되어 있다.

```text
outputs/sensitivity_Z_collapse.csv
```

---

## 7. Environment

핵심 파이프라인은 Python 3 표준 라이브러리만 사용한다.

```text
No external Python packages are required.
Tested with Python 3.10+
```

선택적으로 SVG 미리보기나 PDF 변환을 수행할 경우 `cairosvg` 같은 외부 패키지가 필요할 수 있다. 그러나 프로젝트의 핵심 분석 결과를 재현하는 데에는 필요하지 않다.
