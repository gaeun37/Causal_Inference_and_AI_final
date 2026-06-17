# 시위는 개선을 부르는가?
### 1912년 Lawrence 섬유 파업 신문 데이터를 이용한 인과추론 파이프라인 (추정·시연)

*Causal Inference and AI* 기말 프로젝트(Track B, 모듈: 인문 데이터의 관계 분석). 실제 Library of Congress / Chronicling America 신문 OCR(1912년 1~3월, ALTO XML 90쪽)을 원문 보존부터 지식 그래프·인과 DAG·backdoor 보정 시연까지 이어 붙인다.

## 연구 질문
신문 지면은 Lawrence 파업을 **발전 지향 개선 반응**의 원인으로 구성했는가, 아니면 **혼란·통제 반응**의 원인으로 구성했는가?

## 무엇을 하고, 무엇을 하지 않는가 (중요)
- **하는 것:** 실제 신문에서 인과 구조(변수·경로·맥락별 비율)를 학습하고, 그 구조에 맞춘 demo 데이터로 "시위 프레이밍 → 개선 반응 프레이밍" 효과를 **추정하는 절차를 시연**한다.
- **하지 않는 것:** "파업이 실제로 사회 발전을 일으켰다"는 **증명이 아니다.** 그것은 비파업 지역 비교·파업 전후 임금/노동법 데이터·반사실 비교군이 필요한데, 신문 텍스트만으로는 불가능하다. 모든 효과 수치는 **방법 시연이며 역사적 효과가 아니다.**

## 인과 설계
- **X** 시위 압력 프레이밍(처치) · **M1** 요구 정당화 · **M2** 혼란 프레이밍(매개)
- **Y1** 개선 반응 · **Y2** 질서 통제 반응(결과) · **Z** 맥락 혼란변수(연구자 추가)
- 경로: **X→M1→Y1**(진보), **X→M2→Y2**(혼란)

## 파이프라인 순서
```
신문 OCR → OCR 정제 → 파업 기사 분리 → X/M1/M2/Y1/Y2/Z 코딩(+인용 검증)
→ 지식 그래프 → 인과 DAG → demo backdoor 보정(+민감도) → 보고서
```
원문 증거(`data/raw/`)와 분석 구조(`data/curated/`, `graph/`)를 엄격히 분리해, 모든 인과 주장이 실제 신문 문장에서 나왔는지 확인 가능하게 했다.

## 실행 (결정적·재현 가능; LLM·난수·인터넷 없음)
```bash
python scripts/issue_context.py       # 호 전체 OCR로 맥락 Z 정량화
python scripts/make_demo_data.py      # 코퍼스 근거 demo 데이터 생성(demo_cell_design.csv 참조)
python scripts/build_pipeline.py      # 추출 → KG → DAG → 추론+민감도 → 그림 4개
```

## 핵심 결과 (정직)
| 결과 | naive | 보정 do(X) |
|---|--:|--:|
| Y1 개선 | +0.022 | +0.101 |
| Y2 질서통제 | +0.195 | +0.121 |

원자료의 시위↔개선 연관은 거의 0이며, 맥락 보정 후에야 약한 연관이 나타난다(혼란 위주 신문 맥락에서는 **음수**). 단순한 "시위 → 진보" 서사를 복잡하게 만드는 정직한 결과로, 그대로 보고한다.

## 검증
26개 추출 모두 실제 OCR에서 코딩했고, `outputs/quote_verification_report.csv`가 전 인용이 원문(`data/raw/ocr/`)에 존재함을 재확인한다. Z는 `data/curated/issue_context_features.csv`(호 전체 vs 파업 주변 어휘)로 정당화하며, 결과는 `outputs/sensitivity_weighting.csv`에서 두 가지 P(Z) 가중치로 검증한다.

## 보고서
`report/final_report_ko.md` (한국어, 제출용) · `report/final_report.md` (영어).

## 구성
`data/raw/`(OCR+출처) · `data/cleaned/`(정제+로그) · `data/curated/`(issues, articles[시위+맥락], real_extractions, issue_context_features, demo_cell_design, demo_effect_data) · `graph/`(KG+DAG) · `figures/`(SVG 4) · `outputs/`(요약·진단·결과·민감도·검증) · `report/` · `scripts/`.
