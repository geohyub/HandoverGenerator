"""Simple Korean/English localization helpers."""

from typing import Dict


LANGUAGE_LABELS = {
    "ko": "한국어",
    "en": "English",
}

STATUS_LABELS = {
    "PASS": {"ko": "통과", "en": "PASS"},
    "FAIL": {"ko": "실패", "en": "FAIL"},
    "WARNING": {"ko": "경고", "en": "WARNING"},
    "SKIP": {"ko": "건너뜀", "en": "SKIP"},
    "INFO": {"ko": "정보", "en": "INFO"},
}

SEVERITY_LABELS = {
    "Blocker": {"ko": "중단", "en": "Blocker"},
    "Major": {"ko": "주요", "en": "Major"},
    "Minor": {"ko": "경미", "en": "Minor"},
    "Info": {"ko": "정보", "en": "Info"},
}


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "app_title": {"ko": "납품 패키지 검증기", "en": "Handover Package Validator"},
    "app_subtitle": {
        "ko": "검증 결과를 단순 로그가 아니라 납품 준비도 관점에서 해석합니다.",
        "en": "Interpret validation results as delivery readiness, not just log output.",
    },
    "group_paths": {"ko": "경로", "en": "Paths"},
    "group_variables": {"ko": "변수 (--var)", "en": "Variables (--var)"},
    "group_options": {"ko": "옵션", "en": "Options"},
    "browse": {"ko": "찾아보기", "en": "Browse"},
    "preview_plan": {"ko": "검증 계획 보기", "en": "Preview Plan"},
    "validate": {"ko": "검증 실행", "en": "Validate"},
    "language": {"ko": "언어", "en": "Language"},
    "basic_mode": {
        "ko": "기본 모드 (base profile만 사용)",
        "en": "Basic mode (use the base profile only)",
    },
    "folder_filter": {"ko": "폴더 필터", "en": "Folder filter"},
    "left_section": {"ko": "왼쪽 섹션", "en": "Left section"},
    "right_section": {"ko": "오른쪽 섹션", "en": "Right section"},
    "delivery_path": {"ko": "납품 폴더", "en": "Delivery Path"},
    "profile": {"ko": "프로파일", "en": "Profile"},
    "line_list": {"ko": "라인 리스트", "en": "Line List"},
    "output_excel": {"ko": "출력 (.xlsx)", "en": "Output (.xlsx)"},
    "placeholder_delivery": {
        "ko": "검증할 납품 폴더를 선택하세요...",
        "en": "Select the delivery folder to validate...",
    },
    "placeholder_profile": {
        "ko": "YAML 프로파일을 선택하세요...",
        "en": "Select a YAML profile...",
    },
    "placeholder_linelist": {
        "ko": "(선택) 라인 리스트 CSV를 선택하세요...",
        "en": "(Optional) Select a line list CSV...",
    },
    "placeholder_output": {
        "ko": "(선택) Excel 보고서 저장 위치를 정하세요...",
        "en": "(Optional) Choose where to save the Excel report...",
    },
    "placeholder_filter": {
        "ko": "예: 01_Raw_Data/01_SBP",
        "en": "Example: 01_Raw_Data/01_SBP",
    },
    "tab_summary": {"ko": "준비도 요약", "en": "Readiness Summary"},
    "tab_issue_register": {"ko": "이슈 등록부", "en": "Issue Register"},
    "tab_issue_detail": {"ko": "이슈 상세", "en": "Issue Detail"},
    "tab_line_coverage": {"ko": "라인 커버리지", "en": "Line Coverage"},
    "tab_section_compare": {"ko": "섹션 비교", "en": "Section Compare"},
    "tab_report_preview": {"ko": "보고서 미리보기", "en": "Report Preview"},
    "tab_validation_plan": {"ko": "검증 계획", "en": "Validation Plan"},
    "tab_console": {"ko": "콘솔 출력", "en": "Console Output"},
    "welcome_text": {
        "ko": "납품 패키지 검증기\n----------------------------------------\n1. 납품 폴더와 프로파일을 선택하세요.\n2. 검증 계획을 먼저 확인해 범위를 분명히 하세요.\n3. project_code, area_code 같은 변수를 입력하세요.\n4. 검증을 실행하고 준비도, 이슈, 라인 커버리지를 확인하세요.\n",
        "en": "Handover Package Validator\n----------------------------------------\n1. Select the delivery folder and profile.\n2. Preview the validation plan so the scope is clear.\n3. Add variables such as project_code or area_code.\n4. Run validation and review readiness, issues, and line coverage.\n",
    },
    "summary_placeholder": {
        "ko": "검증을 실행하면 준비도, 주요 이슈, 다음 조치가 여기에 표시됩니다.",
        "en": "Run validation to see readiness, grouped issues, and next actions.",
    },
    "issue_detail_placeholder": {
        "ko": "이슈 등록부에서 항목을 선택하면 상세 설명, 근거, 조치안이 여기에 표시됩니다.",
        "en": "Select an issue in Issue Register to see detail, evidence, and next action.",
    },
    "plan_placeholder": {
        "ko": "검증 계획 보기를 눌러 profile-driven validation 범위를 먼저 확인하세요.",
        "en": "Use Preview Plan to inspect the profile-driven validation scope before running.",
    },
    "compare_placeholder": {
        "ko": "검증 후 두 섹션을 고르면 준비도와 이슈 부하를 비교할 수 있습니다.",
        "en": "Run validation, then choose two sections to compare their readiness and issue load.",
    },
    "report_preview_placeholder": {
        "ko": "검증을 실행하면 보고서에 들어갈 서술 흐름을 여기서 미리 볼 수 있습니다.",
        "en": "Run validation to preview the narrative that will be exported to the report.",
    },
    "summary_running": {
        "ko": "검증 실행 중입니다. 준비도 요약이 곧 표시됩니다.",
        "en": "Validation is running. Readiness summary will appear here.",
    },
    "issue_detail_running": {
        "ko": "검증 실행 중입니다. 결과가 준비되면 이슈 상세가 표시됩니다.",
        "en": "Validation is running. Issue detail will appear after results are loaded.",
    },
    "compare_running": {
        "ko": "검증 실행 중입니다. 결과가 준비되면 섹션 비교가 표시됩니다.",
        "en": "Validation is running. Section comparison will appear after results are loaded.",
    },
    "report_preview_running": {
        "ko": "검증 실행 중입니다. 결과가 준비되면 보고서 미리보기가 표시됩니다.",
        "en": "Validation is running. Report preview will appear after results are loaded.",
    },
    "no_line_coverage": {
        "ko": "이번 실행에는 라인 커버리지 매트릭스가 없습니다.",
        "en": "No line coverage matrix is available for this run.",
    },
    "no_issue_detail": {
        "ko": "이슈를 선택하면 상세 설명, 근거, 권장 조치가 표시됩니다.",
        "en": "Select an issue to see its detail, evidence, and recommended action.",
    },
    "no_compare": {
        "ko": "두 섹션을 선택하면 준비도, 이슈 수, 라인 커버리지를 비교합니다.",
        "en": "Choose two sections to compare their readiness, issue load, and line coverage.",
    },
    "missing_input": {"ko": "입력 누락", "en": "Missing Input"},
    "delivery_required": {"ko": "납품 경로가 필요합니다.", "en": "Delivery path is required."},
    "profile_required": {"ko": "프로파일이 필요합니다.", "en": "Profile is required."},
    "invalid_path": {"ko": "잘못된 경로", "en": "Invalid Path"},
    "invalid_file": {"ko": "잘못된 파일", "en": "Invalid File"},
    "delivery_path_not_found": {
        "ko": "납품 경로가 존재하지 않습니다:\n{path}",
        "en": "Delivery path does not exist:\n{path}",
    },
    "profile_file_not_found": {
        "ko": "프로파일 파일이 존재하지 않습니다:\n{path}",
        "en": "Profile file does not exist:\n{path}",
    },
    "validating": {"ko": "패키지 검증 중...", "en": "Validating package..."},
    "initializing_engine": {"ko": "검증 엔진을 초기화하는 중...", "en": "Initializing validation engine..."},
    "running_validation": {"ko": "검증을 실행하는 중...", "en": "Running validation..."},
    "saving_excel_report": {"ko": "Excel 보고서 저장 중: {path}", "en": "Saving Excel report to: {path}"},
    "excel_report_saved": {"ko": "Excel 보고서를 저장했습니다.", "en": "Excel report saved successfully."},
    "validation_finished": {"ko": "검증 완료", "en": "Validation finished."},
    "validation_error": {"ko": "검증 오류", "en": "Validation error"},
    "profile_loaded": {"ko": "검증 계획을 불러왔습니다.", "en": "Validation plan loaded"},
    "profile_load_failed": {"ko": "프로파일 로드 실패", "en": "Failed to load profile"},
    "status_with_counts": {
        "ko": "{label} | 실패 체크 {failed}개, 경고 체크 {warning}개",
        "en": "{label} | {failed} failed check(s), {warning} warning check(s)",
    },
    "no_results_yet": {"ko": "아직 검증 결과가 없습니다.", "en": "No validation results yet."},
    "no_issues_found": {"ko": "이슈가 없습니다.", "en": "No issues found."},
    "see_finding": {"ko": "본문 참조", "en": "See finding"},
    "see_message": {"ko": "메시지 참조", "en": "See message"},
    "summary_title": {"ko": "납품 준비도 요약", "en": "Handover Package Readiness Summary"},
    "issues_title": {"ko": "시정 조치 등록부", "en": "Corrective Action Register"},
    "line_coverage_title": {"ko": "라인 커버리지 매트릭스", "en": "Line Coverage Matrix"},
    "file_inventory_title": {"ko": "파일 인벤토리", "en": "File Inventory"},
    "naming_violations_title": {"ko": "이름 규칙 위반", "en": "Naming Violations"},
    "sheet_summary": {"ko": "요약", "en": "Summary"},
    "sheet_issues": {"ko": "이슈", "en": "Issues"},
    "sheet_line_coverage": {"ko": "라인 커버리지", "en": "Line Coverage"},
    "sheet_file_inventory": {"ko": "파일 인벤토리", "en": "File Inventory"},
    "sheet_naming_violations": {"ko": "이름 위반", "en": "Naming Violations"},
    "section_executive_readiness": {"ko": "핵심 준비도", "en": "Executive Readiness"},
    "section_validation_basis": {"ko": "검증 기준", "en": "Validation Basis"},
    "section_next_actions": {"ko": "다음 조치", "en": "Next Actions"},
    "section_trust_notes": {"ko": "신뢰 참고사항", "en": "Trust Notes"},
    "section_overview": {"ko": "섹션 개요", "en": "Section Overview"},
    "section_issue_summary": {"ko": "이슈 요약", "en": "Issue Summary"},
    "section_matrix": {"ko": "매트릭스", "en": "Matrix"},
    "section_coverage_summary": {"ko": "커버리지 요약", "en": "Coverage Summary"},
    "col_section": {"ko": "섹션", "en": "Section"},
    "col_severity": {"ko": "심각도", "en": "Severity"},
    "col_status": {"ko": "상태", "en": "Status"},
    "col_check": {"ko": "체크", "en": "Check"},
    "col_category": {"ko": "분류", "en": "Category"},
    "col_finding": {"ko": "판정", "en": "Finding"},
    "col_next_step": {"ko": "권장 조치", "en": "Next Step"},
    "col_evidence": {"ko": "근거", "en": "Evidence"},
    "col_description": {"ko": "설명", "en": "Description"},
    "col_required": {"ko": "필수", "en": "Required"},
    "col_files_found": {"ko": "발견 파일", "en": "Files Found"},
    "col_files_expected": {"ko": "예상 파일", "en": "Files Expected"},
    "col_primary_finding": {"ko": "주요 판정", "en": "Primary Finding"},
    "col_line": {"ko": "라인", "en": "Line"},
    "col_folder": {"ko": "폴더", "en": "Folder"},
    "col_filename": {"ko": "파일명", "en": "Filename"},
    "col_size_mb": {"ko": "크기 (MB)", "en": "Size (MB)"},
    "col_modified": {"ko": "수정 시각", "en": "Modified"},
    "col_naming_ok": {"ko": "이름 규칙 적합", "en": "Naming OK"},
    "col_notes": {"ko": "메모", "en": "Notes"},
    "col_expected_pattern": {"ko": "예상 패턴", "en": "Expected Pattern"},
    "col_issue": {"ko": "문제", "en": "Issue"},
    "yes": {"ko": "예", "en": "Yes"},
    "no": {"ko": "아니오", "en": "No"},
    "ok": {"ko": "정상", "en": "OK"},
    "missing": {"ko": "누락", "en": "Missing"},
    "na": {"ko": "해당 없음", "en": "N/A"},
    "none": {"ko": "없음", "en": "None"},
    "not_used": {"ko": "사용 안 함", "en": "Not used"},
    "not_tracked": {"ko": "추적 안 함", "en": "Not tracked"},
    "direct_profile": {"ko": "직접 프로파일", "en": "Direct profile"},
    "no_status_filter": {"ko": "상태 필터 없음", "en": "No status filter"},
    "no_issues_raised": {"ko": "생성 이슈 없음", "en": "No issues raised"},
    "no_corrective_actions": {
        "ko": "권장 시정 조치가 없습니다.",
        "en": "No corrective actions recommended.",
    },
    "no_trust_caveats": {
        "ko": "이번 실행에 대한 추가 신뢰 주의사항은 없습니다.",
        "en": "No trust caveats were generated for this run.",
    },
    "readiness_label": {"ko": "준비도 등급", "en": "Readiness label"},
    "readiness_score": {"ko": "준비도 점수", "en": "Readiness score"},
    "overall_status": {"ko": "전체 상태", "en": "Overall status"},
    "headline": {"ko": "핵심 요약", "en": "Headline"},
    "validated_on": {"ko": "검증 시각", "en": "Validated on"},
    "check_mix": {"ko": "체크 구성", "en": "Check mix"},
    "severity_mix": {"ko": "심각도 구성", "en": "Severity mix"},
    "line_coverage": {"ko": "라인 커버리지", "en": "Line coverage"},
    "base_profile": {"ko": "기준 프로파일", "en": "Base profile"},
    "profile_description": {"ko": "프로파일 설명", "en": "Profile description"},
    "profile_notes": {"ko": "프로파일 메모", "en": "Profile notes"},
    "line_list_source": {"ko": "라인 리스트 경로", "en": "Line list source"},
    "line_id_column": {"ko": "라인 ID 컬럼", "en": "Line ID column"},
    "line_filter": {"ko": "라인 필터", "en": "Line filter"},
    "resolved_variables": {"ko": "적용 변수", "en": "Resolved variables"},
    "action_label": {"ko": "조치", "en": "Action"},
    "note_label": {"ko": "참고", "en": "Note"},
    "total_issues": {"ko": "총 이슈", "en": "Total issues"},
    "impacted_sections": {"ko": "영향 섹션 수", "en": "Impacted sections"},
    "expected_lines": {"ko": "예상 라인 수", "en": "Expected lines"},
    "tracked_folders": {"ko": "추적 폴더 수", "en": "Tracked folders"},
    "fully_covered_lines": {"ko": "완전 커버 라인", "en": "Fully covered lines"},
    "missing_lines": {"ko": "누락 라인", "en": "Missing lines"},
    "technical_message": {"ko": "기술 메시지", "en": "Technical message"},
    "recommendation": {"ko": "권장 조치", "en": "Recommended Action"},
    "finding_section": {"ko": "판정", "en": "Finding"},
    "evidence_section": {"ko": "근거", "en": "Evidence"},
    "project_context": {"ko": "프로젝트 정보", "en": "Project Context"},
    "profile_variables": {"ko": "프로파일 변수", "en": "Profile Variables"},
    "current_values": {"ko": "현재 값", "en": "Current values"},
    "unresolved": {"ko": "미해결", "en": "Unresolved"},
    "line_matching": {"ko": "라인 매칭", "en": "Line Matching"},
    "folder_scope": {"ko": "폴더 범위", "en": "Folder Scope"},
    "global_checks": {"ko": "전역 체크", "en": "Global Checks"},
    "decision_summary": {"ko": "판단 요약", "en": "Decision Summary"},
    "actionable_checks": {"ko": "실행 체크 수", "en": "Actionable checks"},
    "passed": {"ko": "통과", "en": "Passed"},
    "warnings": {"ko": "경고", "en": "Warnings"},
    "failed": {"ko": "실패", "en": "Failed"},
    "skipped": {"ko": "건너뜀", "en": "Skipped"},
    "priority_issues": {"ko": "우선 이슈", "en": "Priority Issues"},
    "report_preview_header": {"ko": "납품 준비도 보고서 미리보기", "en": "Handover readiness report preview"},
    "executive_summary": {"ko": "핵심 요약", "en": "Executive Summary"},
    "corrective_action_focus": {"ko": "우선 시정 조치", "en": "Corrective Action Focus"},
    "section_readiness": {"ko": "섹션 준비도", "en": "Section Readiness"},
    "issue_detail_header_default": {
        "ko": "이슈를 선택하면 상세 설명, 근거, 조치안이 표시됩니다.",
        "en": "Select an issue to see its detail, evidence, and recommended action.",
    },
    "compare_header": {"ko": "섹션 비교", "en": "Section comparison"},
    "compare_left": {"ko": "왼쪽", "en": "Left"},
    "compare_right": {"ko": "오른쪽", "en": "Right"},
    "compare_section": {"ko": "비교", "en": "Compare"},
    "status_line": {"ko": "상태", "en": "Status"},
    "description_line": {"ko": "설명", "en": "Description"},
    "file_count_line": {"ko": "인벤토리 파일 수", "en": "Files in inventory"},
    "issue_count_line": {"ko": "이슈 수", "en": "Issue count"},
    "coverage_line": {"ko": "라인 커버리지", "en": "Line coverage"},
    "top_issue_line": {"ko": "대표 이슈", "en": "Top issue"},
    "section_not_found": {
        "ko": "최근 보고서에서 이 섹션을 찾지 못했습니다.",
        "en": "Section not found in the latest report.",
    },
    "same_issue_count": {
        "ko": "두 섹션의 실행 이슈 수가 같습니다.",
        "en": "Both sections currently carry the same number of actionable issues.",
    },
    "riskier_by_issues": {
        "ko": "{scope} 쪽이 현재 이슈 {count}개만큼 더 위험합니다.",
        "en": "{scope} is currently riskier by {count} issue(s).",
    },
    "same_coverage": {
        "ko": "선택한 두 섹션의 계획 라인 커버리지는 같습니다.",
        "en": "Planned-line coverage is identical for the selected sections.",
    },
    "better_coverage": {
        "ko": "{scope} 쪽이 {count}% 더 높은 계획 라인 커버리지를 보입니다.",
        "en": "{scope} has {count}% better planned-line coverage.",
    },
    "language_changed": {"ko": "언어를 변경했습니다.", "en": "Language updated."},
    "console_header": {"ko": "납품 패키지 검증 보고서", "en": "Handover Package Validation Report"},
    "next_label": {"ko": "다음", "en": "Next"},
    "trust_note_label": {"ko": "참고", "en": "Note"},
    "folder_checks": {"ko": "폴더 체크", "en": "Folder Checks"},
    "global_checks_console": {"ko": "전역 체크", "en": "Global Checks"},
    "result_label": {"ko": "결과", "en": "Result"},
    "project": {"ko": "프로젝트", "en": "Project"},
    "client": {"ko": "고객", "en": "Client"},
    "total_files": {"ko": "총 파일 수", "en": "Total files"},
    "total_size": {"ko": "총 용량", "en": "Total size"},
    "all_checks_passed": {"ko": "모든 체크 통과", "en": "all checks passed"},
    "issues_found_count": {"ko": "이슈 {count}건 발견", "en": "{count} issue(s) found"},
    "found_count": {"ko": "{count}건 발견", "en": "{count} found"},
    "variable_name": {"ko": "변수명", "en": "variable name"},
    "variable_value": {"ko": "값", "en": "value"},
    "add_variable": {"ko": "+ 변수 추가", "en": "+ Add Variable"},
    "file_menu": {"ko": "파일", "en": "File"},
    "open_delivery_folder": {"ko": "납품 폴더 열기...", "en": "Open Delivery Folder..."},
    "exit": {"ko": "종료", "en": "Exit"},
    "help_menu": {"ko": "도움말", "en": "Help"},
    "about": {"ko": "정보", "en": "About"},
    "about_title": {"ko": "정보", "en": "About"},
    "about_html": {
        "ko": "<h3>납품 패키지 검증기</h3><p>지구물리 조사 프로젝트용 납품 폴더 검증 도구입니다.</p><p>Version 1.0.0</p><p>YAML 프로파일 기준으로 납품 폴더를 검증하고 상세 Excel 보고서를 생성합니다.</p>",
        "en": "<h3>Handover Package Validator</h3><p>Delivery folder validation tool for geophysical survey projects.</p><p>Version 1.0.0</p><p>Validates delivery folders against YAML profiles and generates detailed Excel reports.</p>",
    },
    "ready": {"ko": "준비", "en": "Ready"},
    "no_profile": {"ko": "프로파일 없음", "en": "No Profile"},
    "select_valid_profile_first": {
        "ko": "먼저 유효한 프로파일 파일을 선택하세요.",
        "en": "Select a valid profile file first.",
    },
    "select_delivery_folder": {"ko": "납품 폴더 선택", "en": "Select Delivery Folder"},
    "select_profile": {"ko": "프로파일 선택", "en": "Select Profile"},
    "select_line_list": {"ko": "라인 리스트 선택", "en": "Select Line List"},
    "save_excel_report": {"ko": "Excel 보고서 저장", "en": "Save Excel Report"},
    "yaml_filter": {"ko": "YAML 파일 (*.yaml *.yml)", "en": "YAML Files (*.yaml *.yml)"},
    "csv_filter": {"ko": "CSV 파일 (*.csv)", "en": "CSV Files (*.csv)"},
    "excel_filter": {"ko": "Excel 파일 (*.xlsx)", "en": "Excel Files (*.xlsx)"},
    "all_files": {"ko": "모든 파일 (*)", "en": "All Files (*)"},
    "validation_failed_summary": {
        "ko": "준비도 요약을 만들기 전에 검증이 실패했습니다.\n\n콘솔 출력 탭에서 상세 내용을 확인하세요.",
        "en": "Validation failed before a readiness summary could be generated.\n\nCheck the Console Output tab for details.",
    },
    "validation_failed_issue_detail": {
        "ko": "이슈 상세를 만들기 전에 검증이 실패했습니다.",
        "en": "Validation failed before issue detail could be generated.",
    },
    "validation_failed_compare": {
        "ko": "섹션 비교를 만들기 전에 검증이 실패했습니다.",
        "en": "Validation failed before section comparison could be generated.",
    },
    "validation_failed_report_preview": {
        "ko": "보고서 미리보기를 만들기 전에 검증이 실패했습니다.",
        "en": "Validation failed before the report preview could be generated.",
    },
    "check_console_tab": {
        "ko": "콘솔 출력 탭에서 상세 내용을 확인하세요.",
        "en": "Check the Console Output tab for details.",
    },
    "merged_profile_reference": {
        "ko": "병합된 프로파일 (참고용):",
        "en": "Merged Profile (for reference):",
    },
    "error_loading_profile": {"ko": "프로파일 로딩 오류", "en": "Error loading profile"},
    "required_label": {"ko": "필수", "en": "required"},
    "optional_label": {"ko": "선택", "en": "optional"},
    "checks_label": {"ko": "체크", "en": "Checks"},
    "no_rules_configured": {"ko": "설정된 규칙 없음", "en": "No rules configured"},
    "no_description": {"ko": "설명 없음", "en": "No description"},
    "plan_headline": {
        "ko": "폴더 섹션 {folders}개, 전역 체크 {global_checks}개, 변수 {variables}개가 이번 범위에 포함됩니다.",
        "en": "{folders} folder section(s), {global_checks} global check(s), and {variables} variable(s) are in scope.",
    },
    "line_matching_basic": {
        "ko": "기본 모드가 켜져 있어 base profile만 사용하며 라인 리스트 매칭은 비활성화됩니다.",
        "en": "Basic mode is enabled, so only the base profile is used and line-list matching is disabled.",
    },
    "line_matching_override": {
        "ko": "라인 완전성 비교는 선택한 override CSV를 사용합니다: {path}",
        "en": "Line completeness will use the selected override CSV: {path}.",
    },
    "line_matching_configured": {
        "ko": "라인 완전성 비교는 {source} 와(과) {column} 컬럼을 사용합니다.{filter_note}",
        "en": "Line completeness will use {source} and column {column}.{filter_note}",
    },
    "line_matching_filter_note": {
        "ko": " 필터: {column} == {value}.",
        "en": " Filter: {column} == {value}.",
    },
    "line_matching_not_configured": {
        "ko": "이 프로파일에는 라인 리스트가 설정되어 있지 않아 계획 라인 완전성 체크는 건너뜁니다.",
        "en": "No line list is configured in this profile, so planned-line completeness checks will be skipped.",
    },
    "unresolved_variables_note": {
        "ko": "일부 프로파일 변수가 아직 비어 있습니다. naming, required-file, line-match 체크를 신뢰하기 전에 값을 채우세요.",
        "en": "Some profile variables are still empty. Resolve them before relying on naming, required-file, or line-match checks.",
    },
    "no_folders_in_scope": {
        "ko": "현재 선택 기준으로 범위에 포함된 폴더가 없습니다.",
        "en": "No folders are in scope for the current selection.",
    },
    "missing_in_tracked_folders": {
        "ko": "추적 폴더 중 최소 한 곳에서 누락: {sample}{more}",
        "en": "Missing in at least one tracked folder: {sample}{more}",
    },
    "truncated_inventory": {
        "ko": "10,000개 파일에서 잘림 (전체: {count})",
        "en": "Truncated at 10,000 files (total: {count})",
    },
}


def normalize_lang(lang: str) -> str:
    if not lang:
        return "en"
    return "ko" if str(lang).lower().startswith("ko") else "en"


def tr(key: str, lang: str = "en", **kwargs) -> str:
    lang = normalize_lang(lang)
    value = TRANSLATIONS.get(key, {}).get(lang)
    if value is None:
        value = TRANSLATIONS.get(key, {}).get("en", key)
    return value.format(**kwargs)


def language_label(lang: str) -> str:
    return LANGUAGE_LABELS.get(normalize_lang(lang), LANGUAGE_LABELS["en"])


def status_text(status: str, lang: str = "en") -> str:
    lang = normalize_lang(lang)
    status = str(status)
    return STATUS_LABELS.get(status, {}).get(lang, status)


def severity_text(severity: str, lang: str = "en") -> str:
    lang = normalize_lang(lang)
    severity = str(severity)
    return SEVERITY_LABELS.get(severity, {}).get(lang, severity)
