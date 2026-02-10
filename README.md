# Handover Package Generator

해양조사 프로젝트 납품 폴더를 클라이언트별 스펙에 맞춰 **검증**하는 CLI 도구입니다.
파일을 이동, 복사, 수정하지 않으며 현재 상태를 읽고 보고서만 생성합니다.

## 설치

```bash
pip install click PyYAML pandas openpyxl
# SEG-Y 헤더 검증이 필요한 경우
pip install segyio
```

## 사용법

### 프로젝트 프로파일로 검증

```bash
python -m handover_check.cli validate \
  --path /d/Projects/JAKO_2025/Delivery/ \
  --profile ./profiles/generated/JAKO_2025_Route.yaml \
  --linelist ./JAKO_2025_linelist.csv \
  --var project_code=JAKO2025 \
  --var area_code=RS \
  --output JAKO2025_handover_report.xlsx
```

### 콘솔 요약만 출력

```bash
python -m handover_check.cli validate \
  --path ./Delivery/ \
  --profile JAKO_2025_Route.yaml \
  --summary-only
```

### 특정 폴더만 검증

```bash
python -m handover_check.cli validate \
  --path ./Delivery/ \
  --profile JAKO_2025_Route.yaml \
  --folder "02_Processed_Data/01_SBP"
```

### 기본 검증 (base_geoview만)

```bash
python -m handover_check.cli validate \
  --path ./Delivery/ \
  --basic
```

### 병합된 프로파일 확인

```bash
python -m handover_check.cli show-profile \
  --profile ./profiles/generated/JAKO_2025_Route.yaml \
  --var project_code=JAKO2025
```

## CLI 옵션

| 옵션 | 필수 | 설명 |
|------|------|------|
| `--path` | O | 납품 폴더 경로 |
| `--profile` | - | 프로젝트 프로파일 YAML 경로 |
| `--linelist` | - | 라인 리스트 CSV 경로 (프로파일 설정 오버라이드) |
| `--var KEY=VALUE` | - | 변수 주입 (여러 번 사용 가능) |
| `--output` | - | Excel 보고서 출력 경로 |
| `--summary-only` | - | 콘솔 요약만, Excel 생략 |
| `--folder` | - | 특정 하위 폴더만 검증 |
| `--basic` | - | base_geoview.yaml만 사용 |

## 종료 코드

| 코드 | 의미 |
|------|------|
| `0` | 전체 PASS (INFO/WARNING 포함 가능) |
| `1` | FAIL 1개 이상 |
| `2` | 설정 오류 (프로파일 오류, 파일 미존재 등) |

## 프로파일 시스템

### 구조

```
profiles/
├── base_geoview.yaml           # GeoView 기본 표준 (항상 적용)
└── generated/                  # 프로젝트별 프로파일
    └── JAKO_2025_Route.yaml    # base를 상속하고 오버라이드
```

### 병합 규칙

| 필드 | 규칙 |
|------|------|
| `folders` | 프로젝트 정의 시 base 완전 대체 |
| `global_rules` | base 유지 + 프로젝트 `global_rules_extra` 추가 |
| `variables` | 병합, 프로젝트가 우선 |
| 메타데이터 | 프로젝트가 base 오버라이드 |

### 변수 우선순위

`--var` (CLI) > 프로젝트 프로파일 > base 프로파일

## 검증 규칙

| 규칙 | 결과 | 설명 |
|------|------|------|
| `file_pattern` | PASS/FAIL | glob 패턴 파일 존재 + 선택적 naming_regex |
| `naming_regex` | PASS/WARNING | 전체 파일 정규식 검증 |
| `count_match` | PASS/FAIL | 라인 리스트 대비 파일 수 비교 |
| `required_files` | PASS/FAIL | 필수 파일 존재 확인 |
| `min_file_size` | PASS/WARNING | 최소 파일 크기 |
| `no_empty_folders` | PASS/WARNING | 빈 폴더 감지 |
| `no_zero_byte_files` | PASS/FAIL | 0바이트 파일 감지 |
| `no_temp_files` | PASS/FAIL | 임시 파일 감지 |
| `no_duplicate_files` | PASS/WARNING | 중복 파일명 감지 |
| `segy_header_check` | PASS/FAIL/SKIP | SEG-Y 헤더 검증 (segyio 필요) |
| `total_size_report` | INFO | 폴더별 파일 수/용량 보고 |
| `checksum_file` | PASS/FAIL | 체크섬 파일 검증 |

## Excel 보고서 (5개 탭)

1. **Summary** — 폴더별 PASS/FAIL 요약
2. **Issues** — 전체 문제 상세 목록
3. **Line Coverage** — 라인별 파일 존재 매트릭스 (✓/✗)
4. **File Inventory** — 전체 파일 목록 (크기, 날짜, 네이밍 검증)
5. **Naming Violations** — 네이밍 규칙 위반 파일 목록

## 프로파일 생성 워크플로우

프로젝트별 프로파일은 **별도 Claude 채팅**에서 생성합니다.

1. `prompts/system_prompt_profile_generator.md` 내용을 새 Claude 채팅에 붙여넣기
2. 고객사 SoW PDF를 업로드하거나 인테이크 폼 작성
3. Claude가 YAML 프로파일을 생성
4. 검토 후 `profiles/generated/`에 저장
5. `handover-check validate`로 사용

자세한 내용은 `prompts/` 디렉토리를 참조하세요.

## 테스트

```bash
PYTHONPATH=. python -m pytest tests/ -v
```

## 프로젝트 구조

```
handover_check/
├── cli.py              # Click CLI
├── config.py           # 프로파일 로더, 변수 치환, 병합
├── engine.py           # 검증 오케스트레이터
├── line_matcher.py     # 라인 리스트 매칭
├── models.py           # 데이터 클래스
├── validators/         # 12개 검증기
└── reporters/          # console + excel 리포터
profiles/
├── base_geoview.yaml   # GeoView 기본 표준
└── generated/          # 프로젝트별 프로파일
prompts/
├── system_prompt_profile_generator.md  # 프로파일 생성 프롬프트
└── intake_form_ko.md                   # 수동 입력 양식
tests/                  # 63개 테스트
```
