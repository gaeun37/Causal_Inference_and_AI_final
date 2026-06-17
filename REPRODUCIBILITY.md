# 재현 안내 (Reproducibility)

## 원자료
LOC / Chronicling America의 ALTO XML 90쪽(8개 호, 1912년 1~3월). `scripts/parse_alto.py`로 평문 OCR 추출. 출처(LCCN·판·지면·URL·맥락 Z)는 `data/raw/source_urls.csv`. 원문 OCR은 `data/raw/ocr/`에 무수정 보존.

## 전체 재현
```bash
python scripts/parse_alto.py          # (원본 ALTO XML에서 재추출할 때만)
python scripts/clean_ocr.py           # 정제 + 로그
python scripts/issue_context.py       # 호 전체 OCR로 맥락 Z 정량화
python scripts/make_demo_data.py      # demo 데이터 생성
python scripts/build_pipeline.py       # KG·DAG·추론·민감도·그림 (render_figures 자동 호출)
```
LLM·난수·인터넷 없음. 산출물은 정확히 동일하게 재현됨.

## 기대 결과 (demo 방법 시연 전용)
- Y1 개선: naive +0.022 → 보정 +0.101 (within-Z: order_focused −0.033, mixed +0.146, institutional +0.146)
- Y2 질서통제: naive +0.195 → 보정 +0.121
- 민감도(P(Z) 가중치): Y1 +0.101(balanced)/+0.124(observed), Y2 +0.121/+0.116
- backdoor 공식: P(Y=1 | do(X=x)) = Σ_z P(Y=1 | X=x, Z=z) · P(Z=z)

## 인용·맥락 검증
- `outputs/quote_verification_report.csv`: 전 추출 인용이 `data/raw/ocr/` 원문에 존재함을 재확인(텍스트 인용 25건 전부 확인; 26번째는 인용 없는 연구자-추가 Z).
- `data/curated/issue_context_features.csv`: Z 배정의 어휘 근거(호 전체 vs 파업 주변). 호 전체 카운트는 신문을 잘 못 가르고, 파업 주변 어휘에서만 order_focused가 강하게 검증됨(한계 명시).

## 환경
핵심 파이프라인은 Python 3 표준 라이브러리만 사용. `cairosvg`는 SVG 미리보기 변환에만 쓰는 선택 사항.
