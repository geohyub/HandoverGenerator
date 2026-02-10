# Examples — 실행 예시

이 폴더는 `handover-check validate` CLI 도구의 실제 입력/출력 예시입니다.

---

## 1. 입력 파일

### 1-1. 납품 폴더 (`sample_delivery/`)

일부러 **5가지 문제**를 심어둔 샘플 납품 폴더입니다.

```
sample_delivery/
├── 01_Raw_Data/
│   ├── 01_SBP/
│   │   ├── PRJ001_RS_L0001_SBP_RAW.sgy     ← 정상
│   │   ├── PRJ001_RS_L0002_SBP_RAW.sgy     ← 정상
│   │   ├── PRJ001_RS_L0003_SBP_RAW.sgy     ← 정상
│   │   ├── PRJ001_RS_L0004_SBP_RAW.sgy     ← 정상
│   │   └── wrong_name.sgy                   ← ❌ 네이밍 규칙 위반
│   └── 02_MBES/
│       ├── PRJ001_RS_L0001_MBES.all         ← 정상
│       ├── PRJ001_RS_L0002_MBES.all         ← 정상
│       ├── PRJ001_RS_L0003_MBES.all         ← 정상 (L0004 누락!)
│       └── empty_file.txt                   ← ❌ 0바이트 파일
├── 02_Processed_Data/
│   └── 01_SBP/
│       ├── PRJ001_RS_L0001_SBP_PROC.sgy     ← 정상
│       ├── PRJ001_RS_L0002_SBP_PROC.sgy     ← 정상
│       ├── PRJ001_RS_L0003_SBP_PROC.sgy     ← 정상
│       └── PRJ001_RS_L0004_SBP_PROC.sgy     ← 정상
├── 03_Navigation/
│   └── PRJ001_Final_Navigation.csv          ← 정상 (Track_Chart.pdf 누락!)
├── 04_Reports/
│   ├── PRJ001_Processing_Report_Rev01.pdf   ← 정상
│   ├── PRJ001_Processing_Report_Rev01.docx  ← 정상
│   ├── PRJ001_Equipment_Calibration.pdf     ← 정상
│   └── ~$temp_doc.docx                      ← ❌ 임시 파일
└── 05_GIS/
    ├── PRJ001_Survey_Area.shp               ← 정상
    └── PRJ001_Pipeline_Route.kml            ← 정상
```

**심어둔 문제 5가지:**

| # | 위치 | 문제 | 검출 규칙 |
|---|------|------|-----------|
| 1 | `01_SBP/wrong_name.sgy` | 네이밍 규칙 불일치 | `naming_regex` |
| 2 | `02_MBES/` | L0004 파일 누락 (3/4) | `count_match` |
| 3 | `03_Navigation/` | `Track_Chart.pdf` 미존재 | `required_files` |
| 4 | `04_Reports/~$temp_doc.docx` | 임시 파일 존재 | `no_temp_files` |
| 5 | `02_MBES/empty_file.txt` | 0바이트 파일 | `no_zero_byte_files` |

### 1-2. 프로파일 (`sample_profile.yaml`)

- 6개 폴더 검증 (SBP Raw, MBES Raw, SBP Proc, Navigation, Reports, GIS)
- `base_geoview.yaml` 상속 → 전역 규칙 자동 적용
- 변수: `project_code`, `area_code` (CLI에서 주입)

### 1-3. 라인 리스트 (`sample_linelist.csv`)

```csv
LineName,Status,StartEasting,StartNorthing
L0001,Completed,500000,4000000
L0002,Completed,500100,4000100
L0003,Completed,500200,4000200
L0004,Completed,500300,4000300
L0005,Planned,500400,4000400
```

- L0001~L0004: `Completed` → 검증 대상 (4개 라인)
- L0005: `Planned` → `status_filter`에 의해 제외

---

## 2. 실행 명령어

```bash
handover-check validate \
  --path ./examples/sample_delivery/ \
  --profile ./examples/sample_profile.yaml \
  --linelist ./examples/sample_linelist.csv \
  --var project_code=PRJ001 \
  --var area_code=RS \
  --output ./examples/sample_output_report.xlsx
```

또는 `python -m` 형태:

```bash
python -m handover_check.cli validate \
  --path ./examples/sample_delivery/ \
  --profile ./examples/sample_profile.yaml \
  --linelist ./examples/sample_linelist.csv \
  --var project_code=PRJ001 \
  --var area_code=RS \
  --output ./examples/sample_output_report.xlsx
```

---

## 3. 콘솔 출력 결과

```
================================================================
  Handover Package Validation Report
  Project: Example Route Survey 2026 | Client: SAMPLE
  Profile: SAMPLE_2026_Route_Survey
  Path: ./examples/sample_delivery
  Date: 2026-02-10 10:33:10
================================================================

Folder Checks:
  01_Raw_Data/01_SBP ........................ WARNING  (4/4 files)
    └ NAMING VIOLATION: wrong_name.sgy
  01_Raw_Data/02_MBES ....................... FAIL  (3/4 files (1 missing))
    └ MISSING: L0004
  02_Processed_Data/01_SBP .................. PASS  (4/4 files)
  03_Navigation ............................. FAIL
    └ MISSING: PRJ001_Track_Chart.pdf
  04_Reports ................................ FAIL
    └ ~$temp_doc.docx
  05_GIS .................................... PASS

Global Checks:
  No Empty Folders .......................... PASS
  No Zero Byte Files ........................ FAIL  (1 found)
    └ 01_Raw_Data/02_MBES/empty_file.txt
  No Temp Files ............................. FAIL  (1 found)
    └ 04_Reports/~$temp_doc.docx
  No Duplicate Files ........................ PASS
  Total Size Report ......................... INFO  20 files, 870.1 KB

================================================================
  Total files: 20  |  Total size: 870.1 KB
  Result: FAIL (6 issue(s) found)
================================================================

Excel report saved to: examples/sample_output_report.xlsx
```

**Exit Code: `1`** (FAIL)

---

## 4. Excel 리포트 (`sample_output_report.xlsx`)

5개 탭으로 구성됩니다:

### Tab 1: Summary
| Folder | Status | Details |
|--------|--------|---------|
| 01_Raw_Data/01_SBP | WARNING | 4/4 files, 1 naming violation |
| 01_Raw_Data/02_MBES | FAIL | 3/4 files, L0004 missing |
| 02_Processed_Data/01_SBP | PASS | 4/4 files |
| 03_Navigation | FAIL | PRJ001_Track_Chart.pdf missing |
| 04_Reports | FAIL | Temp file found |
| 05_GIS | PASS | All required files present |

### Tab 2: Issues
| Folder | Rule | Status | Message |
|--------|------|--------|---------|
| 01_Raw_Data/01_SBP | naming_regex | WARNING | 1 file(s) violate naming: wrong_name.sgy |
| 01_Raw_Data/02_MBES | count_match | FAIL | 3/4 lines matched. Missing: L0004 |
| 03_Navigation | required_files | FAIL | Missing: PRJ001_Track_Chart.pdf |
| 04_Reports | no_temp_files | FAIL | ~$temp_doc.docx |
| (global) | no_zero_byte_files | FAIL | empty_file.txt |
| (global) | no_temp_files | FAIL | ~$temp_doc.docx |

### Tab 3: Line Coverage Matrix
| Line | 01_SBP Raw | 02_MBES Raw | 01_SBP Proc |
|------|-----------|-------------|-------------|
| L0001 | ✓ | ✓ | ✓ |
| L0002 | ✓ | ✓ | ✓ |
| L0003 | ✓ | ✓ | ✓ |
| L0004 | ✓ | ✗ | ✓ |

### Tab 4: File Inventory
전체 20개 파일의 경로, 크기, 수정일, 네이밍 상태 등

### Tab 5: Naming Violations
| Folder | File | Expected Pattern |
|--------|------|-----------------|
| 01_Raw_Data/01_SBP | wrong_name.sgy | `^PRJ001_RS_(?P<line>L\d{4})_SBP_RAW\.sgy$` |

---

## 5. Exit Code 정리

| Code | 의미 |
|------|------|
| `0` | PASS — 모든 검증 통과 |
| `1` | FAIL — 하나 이상의 검증 실패 |
| `2` | 설정 오류 (프로파일/경로 문제) |
