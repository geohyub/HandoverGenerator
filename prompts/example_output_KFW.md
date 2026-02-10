# Profile Generator 출력 예시

> 아래는 **KFW Offshore Floating Wind Farm Geophysical Survey** SoW를 기반으로
> Profile Generator Claude가 출력하는 형태의 예시입니다.
> 실제 다른 채팅에서 SoW PDF 업로드 시 이런 형태로 결과가 나옵니다.

---

## 추출 요약표 (블록 0 — 사용자 확인용)

Claude가 SoW에서 정보를 추출한 뒤 **먼저** 아래 요약표를 보여주고, 사용자 확인 후 YAML을 생성합니다.

---

SoW에서 추출한 정보를 정리했습니다. 확인해 주세요.

| 항목 | 추출 내용 |
|------|-----------|
| 클라이언트 | KFW / EBP |
| 프로젝트명 | KFW Offshore Floating Wind Farm Geophysical Survey - Export Cable Route |
| 참조 문서 | Schedule 2. KRKFW-KFW-GEO-GPH-SOW-00002 + Geophysical Surveys Tech_Specs_v.1_0609.pdf |
| 센서 목록 | MBES, SSS, SBP, UHRS(Multi-Freq SBP), MAG |
| 추가 데이터 | SVP, Navigation, Targets, GIS(SSDM V2), Reports |
| 폴더 구조 | SoW 미명시 → 센서별 기본 패턴 적용 |
| 파일 네이밍 | SoW 미명시 → 일반 패턴 적용 |
| 라인 리스트 | 사용 예상, 컬럼명 미명시 |
| SEG-Y | 좌표 검증 필요, 샘플레이트 미명시 |
| MBES 그리드 | DTM, TVU, THU, SD, Density, Contours, Backscatter |
| GIS | SSDM V2 Esri ArcGIS Geodatabase |
| 체크섬 | SoW 미명시 |

**REVIEW 필요 항목: 7개** (폴더 구조, 파일 네이밍, 라인 리스트 컬럼, SEG-Y 샘플레이트, Raw 확장자, 그리드 패턴, 프로젝트 파일 패턴)

위 내용이 맞으면 YAML 프로파일을 생성하겠습니다. 수정할 부분이 있으면 말씀해 주세요.

---

(사용자가 "확인" 또는 "ㅇㅇ" 등으로 응답하면 아래 3개 블록을 출력합니다)

---

## 최종 출력 (블록 1 + 2 + 3)

**파일명: `KFW_2026_OfECC_Geophysical.yaml`**

```yaml
# ============================================
# Handover Validation Profile
# Client: KFW / EBP
# Project: KFW Offshore Floating Wind Farm Geophysical Survey
# Generated: 2026-02-10
# ============================================

profile_name: "KFW_2026_OfECC_Geophysical"
base: "base_geoview.yaml"
client: "KFW"
project: "KFW Offshore Floating Wind Farm Geophysical Survey - Export Cable Route"
generated_from: "Schedule 2. KRKFW-KFW-GEO-GPH-SOW-00002_Scope of Work.pdf + Geophysical Surveys Tech_Specs_v.1_0609.pdf"
generated_date: "2026-02-10"
notes: "Auto-generated from SoW + Tech Specs. 7 REVIEW items - search # REVIEW comments and verify before use"

# -- Variables --
variables:
  project_code: null    # CLI에서 --var project_code=KFW2026 으로 주입
  area_code: null        # CLI에서 --var area_code=OfECC 로 주입

# -- Line List --
line_list:  # REVIEW: Line list format/column names not specified in SoW or Tech Specs
  source: "line_list.csv"
  line_id_column: "LineID"      # REVIEW: Column name not specified
  status_column: "Status"       # REVIEW: Column name not specified
  status_filter: "Completed"

# ============================================
# Folder Validation Rules
# ============================================
# REVIEW: Folder structure not specified in SoW or Tech Specs, default pattern applied
folders:

  # -------------------------------------------------------
  # 01_MBES - Multibeam Echosounder (IHO Order 1a)
  # -------------------------------------------------------
  - path: "01_MBES/Raw"
    description: "MBES raw data"
    rules:
      - type: file_pattern
        pattern: "*.*"  # REVIEW: Raw data extensions vary by acquisition software (*.all, *.kmall, etc.)

  - path: "01_MBES/Processed"
    description: "MBES processed data - gridded/un-gridded XYZ"
    rules:
      - type: file_pattern
        pattern: "*.xyz"

  - path: "01_MBES/Grids/DTM"
    description: "MBES DTM grids - GeoTIFF (2m array / 4m route)"
    rules:
      - type: file_pattern
        pattern: "*.tif"  # REVIEW: Grid filename patterns not specified

  - path: "01_MBES/Grids/TVU"
    description: "MBES Total Vertical Uncertainty grid"
    rules:
      - type: file_pattern
        pattern: "*.tif"

  - path: "01_MBES/Grids/THU"
    description: "MBES Total Horizontal Uncertainty grid"
    rules:
      - type: file_pattern
        pattern: "*.tif"

  - path: "01_MBES/Grids/SD"
    description: "MBES Standard Deviation grid"
    rules:
      - type: file_pattern
        pattern: "*.tif"

  - path: "01_MBES/Grids/Density"
    description: "MBES Sounding Density grid"
    rules:
      - type: file_pattern
        pattern: "*.tif"

  - path: "01_MBES/Grids/Contours"
    description: "MBES depth contours - Shapefile"
    rules:
      - type: file_pattern
        pattern: "*.shp"

  - path: "01_MBES/Backscatter"
    description: "MBES backscatter mosaic"
    rules:
      - type: file_pattern
        pattern: "*.tif"

  - path: "01_MBES/Metadata"
    description: "MBES MEDIN XML metadata"
    rules:
      - type: file_pattern
        pattern: "*.xml"

  # -------------------------------------------------------
  # 02_SSS - Side Scan Sonar (Dual Freq HF/LF)
  # -------------------------------------------------------
  - path: "02_SSS/Raw"
    description: "SSS raw XTF data (both channels)"
    rules:
      - type: file_pattern
        pattern: "*.xtf"
        naming_regex: "^(?P<line>.+?)\\.xtf$"  # REVIEW: File naming convention not specified
      - type: count_match
        match_to: line_list

  - path: "02_SSS/Mosaics/HF"
    description: "SSS HF mosaic GeoTIFF - 1x1km tiles"
    rules:
      - type: file_pattern
        pattern: "*.tif"

  - path: "02_SSS/Mosaics/LF"
    description: "SSS LF mosaic GeoTIFF - 1x1km tiles"
    rules:
      - type: file_pattern
        pattern: "*.tif"

  - path: "02_SSS/Contacts"
    description: "SSS contact list - SHP and CSV"
    rules:
      - type: file_pattern
        pattern: "*.shp"
      - type: file_pattern
        pattern: "*.csv"

  - path: "02_SSS/Project"
    description: "SonarWiz project files"
    optional: true
    rules:
      - type: file_pattern
        pattern: "*.*"  # REVIEW: Processing software project file patterns not specified

  - path: "02_SSS/Metadata"
    description: "SSS MEDIN XML metadata"
    rules:
      - type: file_pattern
        pattern: "*.xml"

  # -------------------------------------------------------
  # 03_SBP - Sub-Bottom Profiler (HF Parametric/Chirp)
  # -------------------------------------------------------
  - path: "03_SBP/Raw"
    description: "SBP raw data - full waveform 24-bit SEG-Y"
    rules:
      - type: file_pattern
        pattern: "*.sgy"
        naming_regex: "^(?P<line>.+?)\\.sgy$"  # REVIEW: File naming convention not specified
      - type: count_match
        match_to: line_list
      - type: segy_header_check
        check_coordinates: true
        check_sample_rate: true  # REVIEW: SEG-Y sample rate not specified in SoW or Tech Specs

  - path: "03_SBP/Processed"
    description: "SBP processed SEG-Y - motion corrected, datum aligned"
    rules:
      - type: file_pattern
        pattern: "*.sgy"
        naming_regex: "^(?P<line>.+?)\\.sgy$"  # REVIEW: File naming convention not specified
      - type: count_match
        match_to: line_list
      - type: segy_header_check
        check_coordinates: true
        check_sample_rate: true  # REVIEW: SEG-Y sample rate not specified

  - path: "03_SBP/Images"
    description: "SBP profile images - TIFF/PNG"
    rules:
      - type: file_pattern
        pattern: "*.tif"
      - type: file_pattern
        pattern: "*.png"

  - path: "03_SBP/Interpretation"
    description: "SBP interpretation CSV (horizons, TWT, Elevation, Depth BSB)"
    rules:
      - type: file_pattern
        pattern: "*.csv"

  - path: "03_SBP/Grids"
    description: "SBP elevation/BSB/isochore grids - GeoTIFF + XYZ (5m)"
    rules:
      - type: file_pattern
        pattern: "*.tif"  # REVIEW: Grid filename patterns not specified
      - type: file_pattern
        pattern: "*.xyz"

  - path: "03_SBP/Metadata"
    description: "SBP MEDIN XML metadata"
    rules:
      - type: file_pattern
        pattern: "*.xml"

  # -------------------------------------------------------
  # 04_UHRS - Multi-Frequency SBP (Sparker/Boomer)
  # -------------------------------------------------------
  - path: "04_UHRS/Raw"
    description: "UHRS raw SEG-Y data"
    rules:
      - type: file_pattern
        pattern: "*.sgy"
        naming_regex: "^(?P<line>.+?)\\.sgy$"  # REVIEW: File naming convention not specified
      - type: count_match
        match_to: line_list
      - type: segy_header_check
        check_coordinates: true
        check_sample_rate: true  # REVIEW: SEG-Y sample rate not specified

  - path: "04_UHRS/Processed"
    description: "UHRS processed SEG-Y - motion corrected, datum aligned"
    rules:
      - type: file_pattern
        pattern: "*.sgy"
        naming_regex: "^(?P<line>.+?)\\.sgy$"  # REVIEW: File naming convention not specified
      - type: count_match
        match_to: line_list
      - type: segy_header_check
        check_coordinates: true
        check_sample_rate: true  # REVIEW: SEG-Y sample rate not specified

  - path: "04_UHRS/Images"
    description: "UHRS profile images - TIFF/PNG"
    rules:
      - type: file_pattern
        pattern: "*.tif"
      - type: file_pattern
        pattern: "*.png"

  - path: "04_UHRS/Interpretation"
    description: "UHRS interpretation CSV"
    rules:
      - type: file_pattern
        pattern: "*.csv"

  - path: "04_UHRS/Grids"
    description: "UHRS elevation/BSB/isochore grids - GeoTIFF + XYZ (5m)"
    rules:
      - type: file_pattern
        pattern: "*.tif"  # REVIEW: Grid filename patterns not specified
      - type: file_pattern
        pattern: "*.xyz"

  - path: "04_UHRS/Metadata"
    description: "UHRS MEDIN XML metadata"
    rules:
      - type: file_pattern
        pattern: "*.xml"

  # -------------------------------------------------------
  # 05_MAG - Magnetometer (Cesium Vapor)
  # -------------------------------------------------------
  - path: "05_MAG/Raw"
    description: "MAG raw data - CSV/ASCII"
    rules:
      - type: file_pattern
        pattern: "*.csv"
      - type: file_pattern
        pattern: "*.ascii"

  - path: "05_MAG/Processed"
    description: "MAG processed data - CSV (Date/Time/E/N/Depth/Alt/Heading/Signal)"
    rules:
      - type: file_pattern
        pattern: "*.csv"

  - path: "05_MAG/Grids"
    description: "MAG altitude/signal/residual grids (0.5m bin) - GRD/FLT/GeoTIFF"
    rules:
      - type: file_pattern
        pattern: "*.grd"
      - type: file_pattern
        pattern: "*.tif"

  - path: "05_MAG/Contacts"
    description: "MAG contact list - SHP and CSV"
    rules:
      - type: file_pattern
        pattern: "*.shp"
      - type: file_pattern
        pattern: "*.csv"

  - path: "05_MAG/Project"
    description: "Oasis Montaj project files (*.gdb)"
    optional: true
    rules:
      - type: file_pattern
        pattern: "*.gdb"  # REVIEW: Processing software project file patterns not specified

  - path: "05_MAG/Metadata"
    description: "MAG MEDIN XML metadata"
    rules:
      - type: file_pattern
        pattern: "*.xml"

  # -------------------------------------------------------
  # 06_Kingdom - Kingdom Project (SBP + UHRS combined)
  # -------------------------------------------------------
  - path: "06_Kingdom"
    description: "Kingdom project - TWT + DEPTH domains"
    optional: true
    rules:
      - type: file_pattern
        pattern: "*.*"  # REVIEW: Processing software project file patterns not specified

  # -------------------------------------------------------
  # 07_SVP - Sound Velocity Profiles
  # -------------------------------------------------------
  - path: "07_SVP"
    description: "SVP data files"
    rules:
      - type: file_pattern
        pattern: "*.csv"
      - type: file_pattern
        pattern: "*.xls"  # Tech Specs Sec 8.5 specifies XLS

  # -------------------------------------------------------
  # 08_Navigation - Positioning Data
  # -------------------------------------------------------
  - path: "08_Navigation"
    description: "Positioning data - CSV, TXT, SHP (Tech Specs Sec 7.4)"
    rules:
      - type: file_pattern
        pattern: "*.csv"
      - type: file_pattern
        pattern: "*.shp"

  # -------------------------------------------------------
  # 09_Targets - Combined Target Lists
  # -------------------------------------------------------
  - path: "09_Targets"
    description: "MBES/SSS/MAG/SBP target picks - SHP + XLSX"
    rules:
      - type: file_pattern
        pattern: "*.shp"
      - type: file_pattern
        pattern: "*.xlsx"

  # -------------------------------------------------------
  # 10_GIS - SSDM V2 Geodatabase
  # -------------------------------------------------------
  - path: "10_GIS"
    description: "SSDM V2 Esri ArcGIS geodatabase + supporting shapefiles"
    rules:
      - type: file_pattern
        pattern: "*.gdb"
      - type: file_pattern
        pattern: "*.shp"

  # -------------------------------------------------------
  # 11_Reports - Reports and Drawings
  # -------------------------------------------------------
  - path: "11_Reports"
    description: "Survey reports (PDF + MS Word) and drawings (MXD + PDF + DWG)"
    rules:
      - type: file_pattern
        pattern: "*.pdf"
      - type: file_pattern
        pattern: "*.docx"
      - type: file_pattern
        pattern: "*.mxd"
      - type: file_pattern
        pattern: "*.dwg"
```

(base의 global_rules로 충분하므로 global_rules_extra를 생략합니다.)

**CLI 실행 예시:**

```bash
handover-check validate \
  --path /d/Projects/KFW_2026/Delivery/ \
  --profile ./profiles/generated/KFW_2026_OfECC_Geophysical.yaml \
  --linelist ./KFW_2026_linelist.csv \
  --var project_code=KFW2026 \
  --var area_code=OfECC \
  --output KFW2026_report.xlsx
```

**REVIEW 항목 (7개):**
1. `line_list` > `line_id_column` / `status_column`: Line list 컬럼명이 SoW/Tech Specs에 미명시
2. `folders`: 전체 폴더 구조가 SoW에 미명시, 센서별 기본 패턴 적용
3. `01_MBES/Raw` > `file_pattern`: Raw 확장자가 장비별로 다름 (*.all, *.kmall 등)
4. `01_MBES/Grids/DTM` > `file_pattern`: 그리드 파일명 패턴 미명시
5. `02_SSS/Raw`, `03_SBP/Raw/Processed`, `04_UHRS/Raw/Processed` > `naming_regex`: 파일 네이밍 규칙 미명시
6. `03_SBP/Raw`, `04_UHRS/Raw/Processed` > `segy_header_check`: SEG-Y 샘플레이트 미명시
7. `02_SSS/Project`, `05_MAG/Project`, `06_Kingdom` > `file_pattern`: 처리 소프트웨어 프로젝트 파일 패턴 미명시

수정이 필요하면 말씀해 주세요.

---

> **참고**: 위 출력은 Profile Generator Claude가 SoW PDF를 분석한 후 생성하는 실제 출력 형태입니다.
> 사용자는 YAML 코드블록을 복사하여 `profiles/generated/KFW_2026_OfECC_Geophysical.yaml`로 저장한 뒤
> CLI 명령어를 실행하면 됩니다.
