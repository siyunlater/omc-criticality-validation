"""케이스별 벤치마크 keff ± σ.

규칙
- 키는 ICSBEP 벤치마크 ID (results.csv의 case 열과 같은 이름)
- 값은 출처를 확인한 것만 넣는다. 없으면 항목을 만들지 않는다
  → save_result가 빈 칸으로 저장하고, compare가 "원문 확인 대기"로 표시한다
- 원문의 치수·표는 여기 쓰지 않는다 (ID와 최종 keff ± σ만)

출처 (2026-10-26 확인)
- mit-crpg/benchmarks, icsbep/icsbep/uncertainties.csv (`model_keff`, MIT 라이선스)
  아래 6개가 이 파일의 값과 일치함. ICSBEP 원문 자체는 아님(2차 출처)
- 입력(반지름)도 같은 저장소 모델과 일치함
"""

BENCHMARKS = {
    # ID: (keff, σ)
    "PU-MET-FAST-001": (1.0000, 0.0020),
    "HEU-MET-FAST-001": (1.0000, 0.0010),
    "U233-MET-FAST-001": (1.0000, 0.0010),
    "MIX-MET-FAST-001": (1.0000, 0.0016),
    "PU-MET-FAST-006": (1.0000, 0.0030),
    "HEU-SOL-THERM-032": (1.0015, 0.0026),
}
