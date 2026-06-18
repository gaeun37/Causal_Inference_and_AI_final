# Reproducibility

이 문서는 본 프로젝트의 자료 구성, 실행 순서, 주요 산출물, 검증 방법을 설명한다. 프로젝트의 핵심 파이프라인은 Python 표준 라이브러리만으로 실행되며, LLM API, 난수 생성, 인터넷 연결을 사용하지 않는다.

---

## 1. Source Data

본 프로젝트의 원자료는 Library of Congress / Chronicling America에서 수집한 1912년 1~3월 Lawrence Textile Strike 관련 신문 자료이다. 총 8개 신문 호, 90개 지면의 ALTO XML/OCR 자료를 사용하였다.

출처 정보는 다음 파일에 정리되어 있다.

```text
data/raw/source_urls.csv
```

이 파일에는 각 신문 호의 날짜, 신문명, LCCN, 지면 수, URL, 맥락 변수 `Z`가 포함되어 있다.

원문 OCR 텍스트는 다음 폴더에 무수정 보존하였다.

```text
data/raw/ocr/
```

정제된 OCR 텍스트는 원문과 분리하여 다음 폴더에 저장하였다.

```text
data/cleaned/
```

---

## 2. Data Layers

본 프로젝트의 데이터는 원문 신문 OCR에서 출발하여 다음 네 층위로 구성된다.

| 데이터 종류 | 내용 | 역할 |
|---|---|---|
| 실제 신문 OCR corpus | Lawrence Strike 관련 신문 8개 호, 90쪽 OCR | 1차 역사 신문 자료 |
| 프레이밍 추출 데이터 | 실제 기사 문장과 source span을 기준으로 추출한 26개 인과 프레이밍 단위 | `X`, `M1`, `Y1`, `M2`, `Y2`, `Z` 코딩의 기준 |
| Knowledge Graph 데이터 | `Issue`, `Article`, `Extraction`, `SupportingQuote`, `AssertedCausalClaim`, `AnalystAssumption` 등 nodes/edges CSV | 프레이밍 해석과 원문 근거를 연결하는 출처 추적 구조 |
| demo-coded data | corpus 관찰 패턴을 바탕으로 구성한 160개 효과 추정 시연용 데이터 | 신문 맥락 `Z` 보정 전후 해석 비교 |

실제 corpus에서 직접 관찰한 결과는 26개 프레이밍 추출 단위의 분포이고, backdoor adjustment 결과는 실제 역사 전체의 ATE가 아니라 demo-coded data 안에서 계산한 제한적 framing effect이다.

---

## 3. How to Reproduce

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
|---|---|
| `scripts/clean_ocr.py` | 원문 OCR을 정제하고 cleaning log를 생성한다. |
| `scripts/issue_context.py` | 신문 호 단위 맥락 변수 `Z`를 보조적으로 계산한다. |
| `scripts/make_demo_data.py` | corpus 관찰에 근거한 demo-coded data를 생성한다. |
| `scripts/corpus_cooccurrence.py` | 실제 26개 추출의 rung-1 association을 계산한다. |
| `scripts/build_pipeline.py` | 추출 결과, Knowledge Graph, Causal DAG, demo adjustment, sensitivity, figure 파일을 생성한다. |

원본 ALTO XML에서 OCR 텍스트를 다시 추출해야 하는 경우에만 다음 스크립트를 사용할 수 있다.

```bash
python scripts/parse_alto.py
```

일반적인 재현 과정에서는 이미 추출된 OCR 텍스트가 `data/raw/ocr/`에 포함되어 있으므로 `parse_alto.py`를 다시 실행할 필요는 없다.

---

## 4. Demo-coded Data Cell Counts

Backdoor adjustment를 위해 사용한 demo-coded data는 다음 cell count에 기반한다. 이 데이터는 무작위 생성 데이터가 아니라, 실제 corpus에서 관찰한 신문 맥락별 프레이밍 경향을 바탕으로 구성한 시연용 데이터이다.

| 신문 맥락 `Z` | `X`: 시위 압력 프레이밍 | 단위 수 `n` | `Y1` 개선 반응 수 | `Y1` 비율 | `Y2` 질서 통제 반응 수 | `Y2` 비율 |
|---|---:|---:|---:|---:|---:|---:|
| order_focused | 1 | 30 | 8 | 0.267 | 24 | 0.800 |
| order_focused | 0 | 10 | 3 | 0.300 | 6 | 0.600 |
| mixed | 1 | 44 | 26 | 0.591 | 22 | 0.500 |
| mixed | 0 | 36 | 16 | 0.444 | 14 | 0.389 |
| institutional | 1 | 16 | 13 | 0.813 | 5 | 0.313 |
| institutional | 0 | 24 | 16 | 0.667 | 6 | 0.250 |

`X=1`은 시위 압력 프레이밍이 있는 경우, `X=0`은 같은 신문 맥락 안에서 비교를 위해 구성한 시위 압력 프레이밍이 없는 경우를 의미한다. 이 데이터로 계산한 값은 실제 역사 효과가 아니라, DAG 기반 보정 논리가 어떻게 작동하는지 보여주는 demo framing effect이다.

---

## 5. Expected Outputs

파이프라인을 실행하면 주요 결과 파일이 `outputs/`, `graph/`, `figures/` 폴더에 생성된다.

핵심 demo adjustment 결과는 다음과 같다.

| Outcome | Naive Difference | Adjusted Demo Effect |
|---|---:|---:|
| `Y1`: 개선 반응 | +0.022 | +0.101 |
| `Y2`: 질서 통제 반응 | +0.195 | +0.121 |

Y1 개선 반응의 within-context 결과는 다음과 같다.

| Context `Z` | Within-Z `X→Y1` |
|---|---:|
| order_focused | -0.033 |
| mixed | +0.146 |
| institutional | +0.146 |

민감도 분석 결과는 다음과 같다.

| Outcome | Balanced `P(Z)` | Observed-issue `P(Z)` | 2-level `Z` collapse |
|---|---:|---:|---:|
| `Y1`: 개선 반응 | +0.101 | +0.124 | +0.080 |
| `Y2`: 질서 통제 반응 | +0.121 | +0.116 | +0.138 |

Backdoor adjustment 계산에는 다음 공식을 사용하였다.

```text
P(Y=1 | do(X=x)) = Σ_z P(Y=1 | X=x, Z=z) · P(Z=z)
```

이 수치들은 실제 역사적 ATE가 아니라, 신문 프레이밍 구조를 바탕으로 backdoor adjustment 절차를 시연하기 위한 demo 결과이다.

---

## 6. Evidence and Quote Verification

본 프로젝트는 텍스트 근거와 분석 결과를 분리하여 저장하였다. 인과 프레이밍 추출 결과는 다음 파일에 저장되어 있다.

```text
data/curated/real_extractions.csv
```

각 추출 항목은 원문 OCR 인용과 연결되어 있으며, 인용 검증 결과는 다음 파일에서 확인할 수 있다.

```text
outputs/quote_verification_report.csv
```

이 파일은 텍스트 기반 추출 인용이 `data/raw/ocr/`의 원문 OCR 안에 존재하는지 확인한다. 26개 추출 중 25개는 실제 인용문을 포함하며, 1개는 인용문이 없는 연구자 추가 맥락 변수 `Z`이다.

---

## 7. Context Variable Z

신문 맥락 변수 `Z`는 `order_focused`, `mixed`, `institutional`의 세 범주로 구성하였다. Z 배정의 보조 근거는 다음 파일에 저장되어 있다.

```text
data/curated/issue_context_features.csv
```

이 파일은 두 가지 방식의 어휘 정보를 포함한다.

1. 신문 호 전체 OCR에서의 개혁/제도 어휘와 혼란/통제 어휘
2. Lawrence Strike 언급 주변에서의 개혁/제도 어휘와 혼란/통제 어휘

신문 호 전체의 단순 키워드 카운트는 신문 간 차이를 충분히 구분하지 못했다. 반면 Lawrence Strike 언급 주변 어휘에서는 `order_focused` 맥락이 더 분명하게 확인되었다. 따라서 `Z`는 완전히 정밀한 측정변수라기보다, 원문 기사와 어휘 근거를 바탕으로 한 투명한 휴리스틱 변수로 해석해야 한다.

Strike-proximal 측정에서 데이터가 실제로 지지하는 분할은 `order_focused` vs `reform_leaning`의 2단계이며, `mixed`/`institutional`의 세부 구분은 상당 부분 수작업 판단이다. 이에 `Z`를 2단계로 collapse한 robustness를 `outputs/sensitivity_Z_collapse.csv`에 추가하였으며, 효과의 부호는 유지된다.

추출이 없는 issue는 결과변수 계산에는 포함하지 않지만, corpus 맥락과 재현성을 위해 context-only issue node로 유지하였다.

---

## 8. Optional Visualization

추가 시각화는 다음 스크립트로 다시 만들 수 있다.

```bash
python scripts/visualize_project_results.py
```

생성되는 figure는 다음과 같다.

| Figure | Description |
|---|---|
| `figures/kg_evidence_structure.png` | KG evidence-tracing structure |
| `figures/demo_cell_counts.png` | demo-coded data cell counts |
| `figures/real_corpus_frame_distribution.png` | 실제 corpus 프레임 분포 |
| `figures/demo_effect_naive_vs_adjusted.png` | 보정 전후 demo effect 비교 |
| `figures/sensitivity_effects.png` | 민감도 분석 결과 |

---

## 9. Environment

핵심 파이프라인은 Python 3 표준 라이브러리만 사용한다.

```text
No external Python packages are required.
Tested with Python 3.10+
```

선택적으로 figure를 다시 생성하려면 `matplotlib`이 필요하다. 프로젝트의 핵심 분석 결과 재현에는 필요하지 않다.
