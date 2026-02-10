# Handover Package Validator

해양조사 프로젝트 납품 폴더를 클라이언트별 스펙에 맞춰 **검증**하는 도구입니다.
GUI와 CLI 두 가지 모드를 지원하며, 파일을 이동/복사/수정하지 않고 현재 상태를 읽고 보고서만 생성합니다.

## 스크린샷

```
┌─────────────────────────────────────────────────────────┐
│  Handover Package Validator                             │
│  Delivery folder validation tool                        │
├─ Paths ─────────────────────────────────────────────────┤
│  Delivery Path  [/d/Projects/KFW_2026/Delivery] [Browse]│
│  Profile        [./profiles/generated/KFW...  ] [Browse]│
│  Line List      [./KFW_2026_linelist.csv      ] [Browse]│
│  Output (.xlsx) [KFW2026_report.xlsx          ] [Browse]│
├─ Variables ─────────────────┬─ Options ─────────────────┤
│  project_code = KFW2026     │  [ ] Basic mode           │
│  area_code    = OfECC       │  Folder filter: [       ] │
│  [+ Add Variable]           │                           │
├─────────────────────────────┴───────────────────────────┤
│          [Show Profile]    [▶  Validate]                │
├─ Console Output ────────────────────────────────────────┤
│  ================================================================  │
│    Handover Package Validation Report                   │
│    Project: KFW ... | Client: KFW                       │
│  Folder Checks:                                         │
│    01_MBES/Raw .......................... [PASS]         │
│    02_SSS/Raw ........................... [WARNING]      │
│    03_SBP/Raw ........................... [FAIL]         │
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

## 설치

### 방법 1: pip 설치 (개발용)

```bash
pip install -r requirements.txt
# SEG-Y 헤더 검증이 필요한 경우
pip install segyio
```

### 방법 2: 독립 실행 파일 (exe) 빌드

```bash
pip install pyinstaller
python build_exe.py              # 단일 파일 빌드
python build_exe.py --onedir     # 디렉토리 번들 빌드
```

빌드 결과: `dist/HandoverValidator` (Linux) 또는 `dist/HandoverValidator.exe` (Windows)

## 사용법

### GUI 모드 (권장)

```bash
# Python으로 실행
python run_gui.py

# 또는 빌드된 exe 실행
./dist/HandoverValidator          # Linux
dist\HandoverValidator.exe        # Windows
```

GUI에서:
1. **Delivery Path** — 납품 폴더 선택
2. **Profile** — YAML 프로파일 선택
3. **Line List** — 라인 리스트 CSV 선택 (선택사항)
4. **Output** — Excel 보고서 저장 경로 (선택사항)
5. **Variables** — `project_code`, `area_code` 등 변수 입력
6. **[Validate]** 클릭 — 검증 실행

결과는 **Console Output** 탭과 **Results Table** 탭에서 확인합니다.

### CLI 모드

```bash
# 프로젝트 프로파일로 검증
handover-check validate \
  --path /d/Projects/JAKO_2025/Delivery/ \
  --profile ./profiles/generated/JAKO_2025_Route.yaml \
  --linelist ./JAKO_2025_linelist.csv \
  --var project_code=JAKO2025 \
  --var area_code=RS \
  --output JAKO2025_report.xlsx

# 기본 검증 (base_geoview만)
handover-check validate --path ./Delivery/ --basic

# 특정 폴더만 검증
handover-check validate \
  --path ./Delivery/ \
  --profile JAKO_2025_Route.yaml \
  --folder "02_Processed_Data/01_SBP"

# 병합된 프로파일 확인
handover-check show-profile \
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
| `0` | PASS — 전체 통과 |
| `1` | FAIL — 1개 이상 실패 |
| `2` | 설정 오류 (프로파일 오류, 파일 미존재 등) |

## 실행 예시

`examples/` 폴더에 완전한 동작 예시가 포함되어 있습니다.

```bash
# 샘플 데이터로 검증 실행
python -m handover_check.cli validate \
  --path ./examples/sample_delivery/ \
  --profile ./examples/sample_profile.yaml \
  --linelist ./examples/sample_linelist.csv \
  --var project_code=PRJ001 \
  --var area_code=RS \
  --output ./sample_report.xlsx
```

샘플에는 5가지 의도적인 문제가 포함되어 있어 각 검증 규칙의 동작을 확인할 수 있습니다.
자세한 내용은 [`examples/README.md`](examples/README.md)를 참조하세요.

## 프로파일 시스템

### 구조

```
profiles/
├── base_geoview.yaml           # GeoView 기본 표준 (항상 적용)
└── generated/                  # 프로젝트별 프로파일
    └── KFW_2026_OfECC_Geophysical.yaml
```

### 병합 규칙

| 필드 | 규칙 |
|------|------|
| `folders` | 프로젝트 정의 시 base 완전 대체 |
| `global_rules` | base 유지 + 프로젝트 `global_rules_extra` 추가 |
| `variables` | 병합, 프로젝트가 우선 |
| 메타데이터 | 프로젝트가 base 오버라이드 |

### 변수 우선순위

`--var` (CLI/GUI) > 프로젝트 프로파일 > base 프로파일

## 검증 규칙 (12개)

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

## 보고서

### 콘솔 출력

폴더별 PASS/FAIL/WARNING 상태와 전역 체크 결과를 컬러로 표시합니다.

### Excel 보고서 (5개 탭)

1. **Summary** — 폴더별 PASS/FAIL 요약
2. **Issues** — 전체 문제 상세 목록
3. **Line Coverage** — 라인별 파일 존재 매트릭스 (✓/✗)
4. **File Inventory** — 전체 파일 목록 (크기, 날짜, 네이밍 검증)
5. **Naming Violations** — 네이밍 규칙 위반 파일 목록

## 프로파일 생성 워크플로우

프로젝트별 프로파일은 **별도 Claude 채팅**에서 생성합니다.

1. `prompts/profile_generator_prompt_body.txt`를 Claude Project Knowledge에 업로드
2. 새 대화에서 고객사 SoW PDF를 업로드하거나 인테이크 폼 작성
3. Claude가 YAML 프로파일을 생성 (3블록 출력: YAML + CLI 예시 + REVIEW 목록)
4. 검토 후 `profiles/generated/`에 저장
5. GUI 또는 CLI로 검증 실행

자세한 내용은 [`prompts/`](prompts/) 디렉토리를 참조하세요.
출력 예시는 [`prompts/example_output_KFW.md`](prompts/example_output_KFW.md)를 참조하세요.

## 테스트

```bash
python -m pytest tests/ -v
```

63개 테스트: config(21) + validators(25) + line_matcher(9) + engine(6) + GUI import(2)

## 프로젝트 구조

```
handover_check/
├── cli.py              # Click CLI (validate, show-profile)
├── gui.py              # PyQt5 GUI 애플리케이션
├── config.py           # 프로파일 로더, 변수 치환, 병합
├── engine.py           # 검증 오케스트레이터
├── line_matcher.py     # 라인 리스트 매칭
├── models.py           # 데이터 클래스 (RuleResult, FolderResult, ValidationReport...)
├── validators/         # 12개 검증기 + base + registry
│   ├── base.py         # BaseValidator ABC
│   ├── __init__.py     # VALIDATOR_REGISTRY
│   ├── file_pattern.py
│   ├── naming_regex.py
│   ├── count_match.py
│   ├── required_files.py
│   ├── file_size.py
│   ├── empty_folders.py
│   ├── zero_byte.py
│   ├── temp_files.py
│   ├── duplicates.py
│   ├── segy_check.py
│   ├── total_size.py
│   └── checksum.py
└── reporters/
    ├── console.py      # ANSI 컬러 콘솔 출력
    └── excel.py        # 5탭 Excel 리포트

profiles/
├── base_geoview.yaml   # GeoView 기본 표준
└── generated/          # 프로젝트별 프로파일
    └── KFW_2026_OfECC_Geophysical.yaml

prompts/
├── system_prompt_profile_generator.md   # 프로파일 생성 시스템 프롬프트 (원본)
├── profile_generator_prompt_body.txt    # Project Knowledge 업로드용 (추출본)
├── intake_form_ko.md                    # 수동 입력 양식
└── example_output_KFW.md               # 출력 예시

examples/
├── README.md               # 예시 설명서
├── sample_delivery/        # 샘플 납품 폴더 (5가지 문제 내장)
├── sample_profile.yaml     # 샘플 검증 프로파일
└── sample_linelist.csv     # 샘플 라인 리스트

run_gui.py              # GUI 실행 진입점
build_exe.py            # PyInstaller 빌드 스크립트
setup.py                # 패키지 설치
requirements.txt        # 의존성 목록
tests/                  # 63개 테스트
```

## 기술 스택

- Python 3.8+
- **GUI**: PyQt5 (다크 테마, Fusion 스타일)
- **CLI**: Click
- **Config**: PyYAML
- **Data**: pandas, openpyxl
- **SEG-Y**: segyio (선택)
- **Build**: PyInstaller
