"""Shared interpretation layer for readiness, severity, and corrective actions."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from handover_check.i18n import normalize_lang, severity_text, status_text, tr
from handover_check.models import FolderResult, ResultStatus, RuleResult, ValidationReport
from handover_check.validators.total_size import format_size


SEVERITY_ORDER = {
    "Blocker": 0,
    "Major": 1,
    "Minor": 2,
    "Info": 3,
}

SEVERITY_WEIGHT = {
    "Blocker": 5.0,
    "Major": 3.0,
    "Minor": 1.0,
}

STATUS_FACTOR = {
    ResultStatus.PASS: 1.0,
    ResultStatus.WARNING: 0.55,
    ResultStatus.FAIL: 0.0,
}

RULE_METADATA = {
    "folder_check": {
        "label": "Folder presence",
        "category": "Package completeness",
        "action": "Create the missing section or mark it optional in the profile if it is intentionally excluded.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "variable_error": {
        "label": "Profile variables",
        "category": "Profile readiness",
        "action": "Provide the missing variables before relying on the run result.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "file_pattern": {
        "label": "Expected files",
        "category": "Package completeness",
        "action": "Add the required deliverables to this section and confirm filenames match the agreed pattern.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "count_match": {
        "label": "Line completeness",
        "category": "Line matching",
        "action": "Compare the section against the line list and add missing line files or explain justified exclusions.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "required_files": {
        "label": "Required deliverables",
        "category": "Package completeness",
        "action": "Add the missing mandatory files or update the profile if the contract expectation has changed.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "min_file_size": {
        "label": "Minimum file size",
        "category": "File integrity",
        "action": "Review undersized files and confirm they are not incomplete exports or placeholders.",
        "severity": {
            ResultStatus.FAIL: "Major",
            ResultStatus.WARNING: "Minor",
            ResultStatus.SKIP: "Info",
        },
    },
    "no_empty_folders": {
        "label": "Empty folders",
        "category": "Readiness hygiene",
        "action": "Remove unused empty folders or populate them with the expected deliverables before issuing the package.",
        "severity": {
            ResultStatus.FAIL: "Major",
            ResultStatus.WARNING: "Minor",
            ResultStatus.SKIP: "Info",
        },
    },
    "no_zero_byte_files": {
        "label": "Zero-byte files",
        "category": "File integrity",
        "action": "Replace empty files with valid exports or remove them if they were created by mistake.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "no_temp_files": {
        "label": "Temp and system files",
        "category": "Readiness hygiene",
        "action": "Remove temp or lock files so the package looks intentional and safe to issue externally.",
        "severity": {
            ResultStatus.FAIL: "Major",
            ResultStatus.WARNING: "Minor",
            ResultStatus.SKIP: "Info",
        },
    },
    "no_duplicate_files": {
        "label": "Duplicate filenames",
        "category": "Traceability",
        "action": "Rename duplicate files or separate them clearly so recipients can trace each artifact without ambiguity.",
        "severity": {
            ResultStatus.FAIL: "Major",
            ResultStatus.WARNING: "Minor",
            ResultStatus.SKIP: "Info",
        },
    },
    "naming_regex": {
        "label": "Naming convention",
        "category": "Traceability",
        "action": "Rename files to the agreed convention so line matching and downstream review stay reliable.",
        "severity": {
            ResultStatus.FAIL: "Major",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "segy_header_check": {
        "label": "SEG-Y header sanity",
        "category": "Content QA",
        "action": "Fix SEG-Y headers or confirm equipment exports before sending the package downstream.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
    "total_size_report": {
        "label": "Inventory size report",
        "category": "Inventory context",
        "action": "Use the inventory totals as a reference check against what the client expects to receive.",
        "severity": {
            ResultStatus.INFO: "Info",
            ResultStatus.SKIP: "Info",
        },
    },
    "checksum_file": {
        "label": "Checksum verification",
        "category": "File integrity",
        "action": "Generate or correct the checksum manifest so recipients can verify file integrity after transfer.",
        "severity": {
            ResultStatus.FAIL: "Blocker",
            ResultStatus.WARNING: "Major",
            ResultStatus.SKIP: "Info",
        },
    },
}

RULE_LOCALIZATION_KO = {
    "folder_check": {
        "label": "폴더 존재 여부",
        "category": "패키지 완전성",
        "action": "누락된 섹션 폴더를 만들거나, 의도된 제외라면 프로파일에서 optional로 조정하세요.",
        "summary": {
            ResultStatus.FAIL: "필수 섹션 폴더가 누락되었습니다.",
            ResultStatus.WARNING: "폴더 구성이 재검토가 필요합니다.",
        },
    },
    "variable_error": {
        "label": "프로파일 변수",
        "category": "프로파일 준비 상태",
        "action": "프로파일 변수 값을 채운 뒤 다시 검증해 naming과 required file 판정을 신뢰하세요.",
        "summary": {ResultStatus.FAIL: "필수 프로파일 변수가 비어 있습니다."},
    },
    "file_pattern": {
        "label": "예상 파일 존재 여부",
        "category": "패키지 완전성",
        "action": "이 섹션에 필요한 산출물을 추가하고 파일명이 합의된 규칙을 따르는지 확인하세요.",
        "summary": {
            ResultStatus.FAIL: "기대한 파일 유형이 이 섹션에서 발견되지 않았습니다.",
            ResultStatus.WARNING: "파일은 있으나 이름 규칙이 흔들리고 있습니다.",
        },
    },
    "count_match": {
        "label": "라인 완전성",
        "category": "라인 매칭",
        "action": "라인 리스트와 대조해 누락 라인을 보완하거나 제외 사유를 명시하세요.",
        "summary": {
            ResultStatus.FAIL: "계획 라인 대비 납품 라인 구성이 부족합니다.",
            ResultStatus.WARNING: "라인 리스트에 없는 추가 라인이 발견되었습니다.",
            ResultStatus.SKIP: "라인 완전성 비교가 실행되지 않았습니다.",
        },
    },
    "required_files": {
        "label": "필수 납품물",
        "category": "패키지 완전성",
        "action": "누락된 필수 파일을 추가하거나 계약 기대치가 바뀌었다면 프로파일을 수정하세요.",
        "summary": {ResultStatus.FAIL: "필수 납품 파일이 누락되었습니다."},
    },
    "min_file_size": {
        "label": "최소 파일 크기",
        "category": "파일 무결성",
        "action": "비정상적으로 작은 파일이 미완성 export나 placeholder가 아닌지 확인하세요.",
        "summary": {ResultStatus.WARNING: "비정상적으로 작은 파일이 있습니다."},
    },
    "no_empty_folders": {
        "label": "빈 폴더",
        "category": "정리 상태",
        "action": "사용하지 않는 빈 폴더는 제거하거나 예상 산출물로 채우세요.",
        "summary": {ResultStatus.WARNING: "패키지 안에 빈 폴더가 남아 있습니다."},
    },
    "no_zero_byte_files": {
        "label": "0바이트 파일",
        "category": "파일 무결성",
        "action": "빈 파일을 올바른 산출물로 교체하거나 실수로 생성된 파일이면 제거하세요.",
        "summary": {ResultStatus.FAIL: "0바이트 파일이 발견되었습니다."},
    },
    "no_temp_files": {
        "label": "임시/시스템 파일",
        "category": "정리 상태",
        "action": "temp 또는 lock 파일을 제거해 외부 전달 패키지가 의도된 상태로 보이게 하세요.",
        "summary": {ResultStatus.FAIL: "임시 또는 시스템 파일이 남아 있습니다."},
    },
    "no_duplicate_files": {
        "label": "중복 파일명",
        "category": "추적성",
        "action": "중복 파일명을 구분 가능하게 바꾸어 수신자가 산출물을 혼동하지 않게 하세요.",
        "summary": {ResultStatus.WARNING: "중복 파일명이 발견되었습니다."},
    },
    "naming_regex": {
        "label": "이름 규칙",
        "category": "추적성",
        "action": "파일명을 합의된 규칙에 맞춰 정리해 라인 매칭과 후속 검토의 신뢰를 높이세요.",
        "summary": {ResultStatus.WARNING: "이름 규칙을 벗어난 파일이 있습니다."},
    },
    "segy_header_check": {
        "label": "SEG-Y 헤더 점검",
        "category": "콘텐츠 QA",
        "action": "SEG-Y 헤더나 장비 export 설정을 수정한 뒤 다시 확인하세요.",
        "summary": {
            ResultStatus.FAIL: "SEG-Y 헤더 수준의 문제가 발견되었습니다.",
            ResultStatus.SKIP: "SEG-Y 헤더 점검이 실행되지 않았습니다.",
        },
    },
    "total_size_report": {
        "label": "인벤토리 용량 보고",
        "category": "인벤토리 정보",
        "action": "용량과 파일 수를 클라이언트 기대치와 대조해 최종 누락 여부를 확인하세요.",
        "summary": {ResultStatus.INFO: "인벤토리 크기 참고 정보입니다."},
    },
    "checksum_file": {
        "label": "체크섬 검증",
        "category": "파일 무결성",
        "action": "체크섬 파일을 생성하거나 수정해 수신자가 전송 후 무결성을 검증할 수 있게 하세요.",
        "summary": {ResultStatus.FAIL: "체크섬 파일이 없거나 불일치합니다."},
    },
}


@dataclass
class IssueInsight:
    """Actionable interpretation of one validation issue."""

    scope: str
    scope_description: str
    rule_type: str
    check_label: str
    category: str
    status: ResultStatus
    severity: str
    message: str
    technical_message: str = ""
    details: List[str] = field(default_factory=list)
    action_hint: str = ""

    @property
    def evidence_count(self) -> int:
        return len(self.details)


@dataclass
class CoverageInsight:
    """Interpretation of the line coverage matrix."""

    expected_lines: int
    tracked_folders: int
    fully_covered_lines: int
    fully_covered_percent: int
    coverage_by_folder: Dict[str, int] = field(default_factory=dict)
    missing_by_folder: Dict[str, int] = field(default_factory=dict)
    missing_lines: List[str] = field(default_factory=list)


@dataclass
class ReadinessInsight:
    """Human-readable readiness summary for UI and reports."""

    readiness_percent: int
    readiness_label: str
    headline: str
    applicable_checks: int
    passed_checks: int
    warning_checks: int
    failed_checks: int
    skipped_checks: int
    blocker_count: int
    major_count: int
    minor_count: int
    impacted_sections: int
    issues: List[IssueInsight] = field(default_factory=list)
    top_actions: List[str] = field(default_factory=list)
    trust_notes: List[str] = field(default_factory=list)
    section_overview: List[dict] = field(default_factory=list)
    coverage: Optional[CoverageInsight] = None


@dataclass
class ProfilePlanInsight:
    """Profile-driven validation plan summary."""

    headline: str
    profile_name: str
    client: str
    project: str
    required_variables: List[str] = field(default_factory=list)
    unresolved_variables: List[str] = field(default_factory=list)
    resolved_variables: Dict[str, str] = field(default_factory=dict)
    folder_scope: List[dict] = field(default_factory=list)
    global_checks: List[str] = field(default_factory=list)
    line_matching_note: str = ""
    notes: List[str] = field(default_factory=list)


def _rule_meta(rule_type: str) -> dict:
    return RULE_METADATA.get(
        rule_type,
        {
            "label": rule_type.replace("_", " ").title(),
            "category": "Validation check",
            "action": "Review this validation rule and confirm the expected delivery content.",
            "severity": {
                ResultStatus.FAIL: "Major",
                ResultStatus.WARNING: "Minor",
                ResultStatus.INFO: "Info",
                ResultStatus.SKIP: "Info",
            },
        },
    )


def _severity_for(rule_type: str, status: ResultStatus) -> str:
    meta = _rule_meta(rule_type)
    return meta.get("severity", {}).get(status, "Minor")


def _rule_label(rule_type: str, lang: str) -> str:
    if lang == "ko":
        localized = RULE_LOCALIZATION_KO.get(rule_type)
        if localized:
            return localized["label"]
    return _rule_meta(rule_type)["label"]


def _rule_category(rule_type: str, lang: str) -> str:
    if lang == "ko":
        localized = RULE_LOCALIZATION_KO.get(rule_type)
        if localized:
            return localized["category"]
    return _rule_meta(rule_type)["category"]


def _rule_action(rule_type: str, lang: str) -> str:
    if lang == "ko":
        localized = RULE_LOCALIZATION_KO.get(rule_type)
        if localized:
            return localized["action"]
    return _rule_meta(rule_type)["action"]


def _rule_summary(rule_type: str, status: ResultStatus, raw_message: str, lang: str) -> str:
    if lang == "ko":
        localized = RULE_LOCALIZATION_KO.get(rule_type, {})
        summary = localized.get("summary", {}).get(status)
        if summary:
            return summary
    return raw_message


def _build_issue(scope: str, scope_description: str, result: RuleResult, lang: str) -> IssueInsight:
    meta = _rule_meta(result.rule_type)
    return IssueInsight(
        scope=scope,
        scope_description=scope_description,
        rule_type=result.rule_type,
        check_label=_rule_label(result.rule_type, lang),
        category=_rule_category(result.rule_type, lang),
        status=result.status,
        severity=_severity_for(result.rule_type, result.status),
        message=_rule_summary(result.rule_type, result.status, result.message, lang),
        technical_message=result.message,
        details=list(result.details),
        action_hint=_rule_action(result.rule_type, lang),
    )


def _sort_issues(issues: List[IssueInsight]) -> List[IssueInsight]:
    return sorted(
        issues,
        key=lambda issue: (
            SEVERITY_ORDER.get(issue.severity, 99),
            issue.scope.lower(),
            issue.check_label.lower(),
        ),
    )


def summarize_line_coverage(report: ValidationReport) -> Optional[CoverageInsight]:
    """Build a compact line-coverage summary from the matrix."""

    coverage = report.line_coverage
    if not coverage:
        return None

    lines = list(coverage.get("lines", []))
    folders = list(coverage.get("folders", []))
    matrix = coverage.get("matrix", {})

    if not lines or not folders:
        return CoverageInsight(
            expected_lines=len(lines),
            tracked_folders=len(folders),
            fully_covered_lines=0,
            fully_covered_percent=0,
        )

    fully_covered_lines = 0
    missing_lines: List[str] = []
    coverage_by_folder: Dict[str, int] = {}
    missing_by_folder: Dict[str, int] = {}

    for folder in folders:
        present_count = sum(1 for line in lines if matrix.get(line, {}).get(folder, False))
        coverage_by_folder[folder] = int(round((present_count / len(lines)) * 100))
        missing_by_folder[folder] = len(lines) - present_count

    for line in lines:
        found_in_all = all(matrix.get(line, {}).get(folder, False) for folder in folders)
        if found_in_all:
            fully_covered_lines += 1
        else:
            missing_lines.append(line)

    return CoverageInsight(
        expected_lines=len(lines),
        tracked_folders=len(folders),
        fully_covered_lines=fully_covered_lines,
        fully_covered_percent=int(round((fully_covered_lines / len(lines)) * 100)),
        coverage_by_folder=coverage_by_folder,
        missing_by_folder=missing_by_folder,
        missing_lines=missing_lines,
    )


def build_readiness_insight(report: ValidationReport, lang: Optional[str] = None) -> ReadinessInsight:
    """Create a readiness-focused summary from the raw validation report."""

    lang = normalize_lang(lang or getattr(report, "language", "en"))
    actionable_results: List[Tuple[str, str, RuleResult]] = []
    section_overview: List[dict] = []
    skipped_checks = 0
    passed_checks = 0
    warning_checks = 0
    failed_checks = 0
    weighted_total = 0.0
    weighted_score = 0.0

    for folder_result in report.folder_results:
        folder_issues: List[IssueInsight] = []
        for rule_result in folder_result.rule_results:
            actionable_results.append((folder_result.path, folder_result.description, rule_result))
            if rule_result.status == ResultStatus.SKIP:
                skipped_checks += 1
                continue
            if rule_result.status == ResultStatus.INFO:
                continue

            severity = _severity_for(rule_result.rule_type, rule_result.status)
            weight = SEVERITY_WEIGHT.get(severity, 1.0)
            weighted_total += weight
            weighted_score += weight * STATUS_FACTOR.get(rule_result.status, 0.0)

            if rule_result.status == ResultStatus.PASS:
                passed_checks += 1
                continue
            if rule_result.status == ResultStatus.WARNING:
                warning_checks += 1
            elif rule_result.status == ResultStatus.FAIL:
                failed_checks += 1

            folder_issues.append(
                _build_issue(folder_result.path, folder_result.description, rule_result, lang)
            )

        section_overview.append(
            {
                "scope": folder_result.path,
                "description": folder_result.description,
                "status": folder_result.status,
                "optional": folder_result.optional,
                "issue_count": len(folder_issues),
                "primary_message": folder_issues[0].message if folder_issues else "",
            }
        )

    for global_result in report.global_results:
        actionable_results.append(("(global)", "Cross-package validation", global_result))
        if global_result.status == ResultStatus.SKIP:
            skipped_checks += 1
            continue
        if global_result.status == ResultStatus.INFO:
            continue

        severity = _severity_for(global_result.rule_type, global_result.status)
        weight = SEVERITY_WEIGHT.get(severity, 1.0)
        weighted_total += weight
        weighted_score += weight * STATUS_FACTOR.get(global_result.status, 0.0)

        if global_result.status == ResultStatus.PASS:
            passed_checks += 1
            continue
        if global_result.status == ResultStatus.WARNING:
            warning_checks += 1
        elif global_result.status == ResultStatus.FAIL:
            failed_checks += 1

    issues = _sort_issues(
        [
            _build_issue(scope, scope_description, result, lang)
            for scope, scope_description, result in actionable_results
            if result.status in (ResultStatus.FAIL, ResultStatus.WARNING)
        ]
    )

    blocker_count = sum(1 for issue in issues if issue.severity == "Blocker")
    major_count = sum(1 for issue in issues if issue.severity == "Major")
    minor_count = sum(1 for issue in issues if issue.severity == "Minor")
    impacted_sections = len({issue.scope for issue in issues})
    applicable_checks = passed_checks + warning_checks + failed_checks

    readiness_percent = 100
    if weighted_total > 0:
        readiness_percent = int(round((weighted_score / weighted_total) * 100))

    if blocker_count and failed_checks:
        readiness_label = "납품 준비 전" if lang == "ko" else "Not ready"
    elif failed_checks:
        readiness_label = "부분 준비" if lang == "ko" else "Partial readiness"
    elif warning_checks:
        readiness_label = "주의 필요" if lang == "ko" else "Ready with cautions"
    else:
        readiness_label = "납품 가능" if lang == "ko" else "Ready for delivery"

    if lang == "ko":
        headline = (
            f"준비도 {readiness_percent}% - {readiness_label}. "
            f"실행 이슈 {len(issues)}건, 영향 섹션 {impacted_sections or 0}개입니다."
        )
    else:
        headline = (
            f"Readiness {readiness_percent}% - {readiness_label}. "
            f"{len(issues)} actionable issue(s) across {impacted_sections or 0} section(s)."
        )

    top_actions: List[str] = []
    seen_actions = set()
    for issue in issues:
        action = f"{issue.scope}: {issue.action_hint}"
        if action not in seen_actions:
            top_actions.append(action)
            seen_actions.add(action)
        if len(top_actions) == 3:
            break

    trust_notes: List[str] = []
    count_match_skips = sum(
        1
        for _, _, result in actionable_results
        if result.rule_type == "count_match" and result.status == ResultStatus.SKIP
    )
    if count_match_skips:
        if lang == "ko":
            trust_notes.append(
                f"라인 완전성 비교가 {count_match_skips}개 섹션에서 건너뛰어졌습니다. "
                "라인 리스트 경로, 컬럼명, naming_regex를 확인한 뒤 coverage를 신뢰하세요."
            )
        else:
            trust_notes.append(
                f"Line completeness was skipped in {count_match_skips} section(s). "
                "Confirm the line list path, columns, and naming_regex before treating coverage as complete."
            )

    segy_skips = [
        result.message
        for _, _, result in actionable_results
        if result.rule_type == "segy_header_check" and result.status == ResultStatus.SKIP
    ]
    if segy_skips:
        if any("segyio not installed" in message for message in segy_skips):
            trust_notes.append(
                "segyio가 없어 SEG-Y 헤더 점검이 건너뛰어졌습니다. 이번 실행의 헤더 수준 신뢰도는 제한적입니다."
                if lang == "ko"
                else "SEG-Y header checks were skipped because segyio is unavailable, so header-level confidence is limited for this run."
            )
        else:
            trust_notes.append(
                "적어도 한 SEG-Y 섹션이 헤더 점검되지 않아 좌표와 샘플레이트 신뢰가 불완전합니다."
                if lang == "ko"
                else "At least one SEG-Y section was not header-checked, so coordinate and sample-rate trust is incomplete."
            )

    if not report.line_coverage and report.line_list_source:
        trust_notes.append(
            "라인 리스트는 지정되었지만 라인 커버리지 매트릭스가 생성되지 않았습니다. 보통 선택 범위에서 count-match가 실행되지 못한 경우입니다."
            if lang == "ko"
            else "A line list was configured, but no line coverage matrix was produced. This usually means count-match rules could not execute for the selected scope."
        )
    elif not report.line_list_source:
        trust_notes.append(
            "이번 실행에는 라인 리스트가 지정되지 않았습니다. 파일 존재는 확인했지만 계획 라인 완전성은 전역적으로 측정되지 않았습니다."
            if lang == "ko"
            else "No line list was configured for this run. File presence was checked, but planned-line completeness was not measured globally."
        )

    optional_skips = sum(
        1
        for folder_result in report.folder_results
        if folder_result.optional and folder_result.status == ResultStatus.SKIP
    )
    if optional_skips:
        if lang == "ko":
            trust_notes.append(
                f"optional 섹션 {optional_skips}개가 제외되었거나 존재하지 않았습니다. 준비도를 직접 낮추지는 않지만 의도된 누락인지 확인하세요."
            )
        else:
            trust_notes.append(
                f"{optional_skips} optional section(s) were excluded or not present. They do not reduce readiness, but confirm that omission is intentional."
            )

    coverage = summarize_line_coverage(report)
    return ReadinessInsight(
        readiness_percent=readiness_percent,
        readiness_label=readiness_label,
        headline=headline,
        applicable_checks=applicable_checks,
        passed_checks=passed_checks,
        warning_checks=warning_checks,
        failed_checks=failed_checks,
        skipped_checks=skipped_checks,
        blocker_count=blocker_count,
        major_count=major_count,
        minor_count=minor_count,
        impacted_sections=impacted_sections,
        issues=issues,
        top_actions=top_actions,
        trust_notes=trust_notes,
        section_overview=section_overview,
        coverage=coverage,
    )


def build_profile_plan(
    profile: dict,
    variables: Dict[str, Optional[str]],
    basic: bool = False,
    folder_filter: Optional[str] = None,
    linelist_override: Optional[str] = None,
    lang: str = "en",
) -> ProfilePlanInsight:
    """Create a structured explanation of what the selected profile will validate."""

    lang = normalize_lang(lang)
    folders = []
    for folder in profile.get("folders", []):
        path = folder.get("path", "")
        if folder_filter and path != folder_filter:
            continue
        rules = folder.get("rules", [])
        folders.append(
            {
                "path": path,
                "description": folder.get("description", ""),
                "optional": folder.get("optional", False),
                "rules": [_rule_label(rule.get("type", "unknown"), lang) for rule in rules],
            }
        )

    required_variables = sorted(profile.get("variables", {}).keys())
    unresolved_variables = sorted(
        key
        for key, value in variables.items()
        if value in (None, "")
    )
    resolved_variables = {
        key: "" if value is None else str(value)
        for key, value in variables.items()
    }

    if basic:
        line_matching_note = tr("line_matching_basic", lang)
    else:
        line_list = profile.get("line_list") or {}
        if linelist_override:
            line_matching_note = tr(
                "line_matching_override",
                lang,
                path=linelist_override,
            )
        elif line_list.get("source"):
            filter_note = ""
            if line_list.get("status_column") and line_list.get("status_filter"):
                filter_note = tr(
                    "line_matching_filter_note",
                    lang,
                    column=line_list["status_column"],
                    value=line_list["status_filter"],
                )
            line_matching_note = tr(
                "line_matching_configured",
                lang,
                source=line_list["source"],
                column=line_list.get("line_id_column", "LineName"),
                filter_note=filter_note,
            )
        else:
            line_matching_note = tr("line_matching_not_configured", lang)

    notes = []
    if unresolved_variables:
        notes.append(tr("unresolved_variables_note", lang))
    if not folders:
        notes.append(tr("no_folders_in_scope", lang))
    if profile.get("notes"):
        notes.append(str(profile["notes"]))

    headline = tr(
        "plan_headline",
        lang,
        folders=len(folders),
        global_checks=len(profile.get("global_rules", [])),
        variables=len(required_variables),
    )

    return ProfilePlanInsight(
        headline=headline,
        profile_name=profile.get("profile_name", "unknown"),
        client=profile.get("client") or tr("na", lang),
        project=profile.get("project") or tr("na", lang),
        required_variables=required_variables,
        unresolved_variables=unresolved_variables,
        resolved_variables=resolved_variables,
        folder_scope=folders,
        global_checks=[
            _rule_label(rule.get("type", "unknown"), lang)
            for rule in profile.get("global_rules", [])
        ],
        line_matching_note=line_matching_note,
        notes=notes,
    )


def format_readiness_text(summary: ReadinessInsight, lang: str = "en") -> str:
    """Render a readable plain-text readiness summary."""

    lang = normalize_lang(lang)
    lines = [
        summary.headline,
        "",
        tr("decision_summary", lang),
        f"- {tr('readiness_label', lang)}: {summary.readiness_label}",
        f"- {tr('actionable_checks', lang)}: {summary.applicable_checks}",
        f"- {tr('passed', lang)}: {summary.passed_checks}",
        f"- {tr('warnings', lang)}: {summary.warning_checks}",
        f"- {tr('failed', lang)}: {summary.failed_checks}",
        f"- {tr('skipped', lang)}: {summary.skipped_checks}",
        f"- {tr('severity_mix', lang)}: {summary.blocker_count} {severity_text('Blocker', lang)}, {summary.major_count} {severity_text('Major', lang)}, {summary.minor_count} {severity_text('Minor', lang)}",
    ]

    if summary.coverage:
        coverage = summary.coverage
        lines.extend(
            [
                "",
                tr("line_coverage", lang),
                f"- {tr('fully_covered_lines', lang)}: {coverage.fully_covered_lines}/{coverage.expected_lines} ({coverage.fully_covered_percent}%)",
            ]
        )
        for folder, percent in coverage.coverage_by_folder.items():
            if lang == "ko":
                lines.append(f"- {folder}: 계획 라인 기준 {percent}% 존재")
            else:
                lines.append(f"- {folder}: {percent}% of planned lines present")
        if coverage.missing_lines:
            sample = ", ".join(coverage.missing_lines[:5])
            more = ""
            if len(coverage.missing_lines) > 5:
                more = f" (+{len(coverage.missing_lines) - 5} more)"
            lines.append(
                f"- {tr('missing_in_tracked_folders', lang, sample=sample, more=more)}"
            )

    if summary.top_actions:
        lines.extend(["", tr("section_next_actions", lang)])
        for action in summary.top_actions:
            lines.append(f"- {action}")

    if summary.issues:
        lines.extend(["", tr("priority_issues", lang)])
        for issue in summary.issues[:8]:
            lines.append(
                f"- [{severity_text(issue.severity, lang)}] {issue.scope} / {issue.check_label}: {issue.message}"
            )

    if summary.trust_notes:
        lines.extend(["", tr("section_trust_notes", lang)])
        for note in summary.trust_notes:
            lines.append(f"- {note}")

    return "\n".join(lines)


def format_profile_plan_text(plan: ProfilePlanInsight, lang: str = "en") -> str:
    """Render a readable plain-text validation-plan summary."""

    lang = normalize_lang(lang)
    lines = [
        f"{tr('tab_validation_plan', lang)} - {plan.profile_name}",
        "",
        plan.headline,
        "",
        tr("project_context", lang),
        f"- {tr('client', lang)}: {plan.client}",
        f"- {tr('project', lang)}: {plan.project}",
        "",
        tr("profile_variables", lang),
    ]

    if plan.required_variables:
        lines.append(f"- {tr('group_variables', lang)}: {', '.join(plan.required_variables)}")
    else:
        lines.append(f"- {tr('group_variables', lang)}: {tr('none', lang)}")

    if plan.resolved_variables:
        resolved_pairs = [
            f"{key}={value or '<empty>'}"
            for key, value in sorted(plan.resolved_variables.items())
        ]
        lines.append(f"- {tr('current_values', lang)}: {', '.join(resolved_pairs)}")

    if plan.unresolved_variables:
        lines.append(f"- {tr('unresolved', lang)}: {', '.join(plan.unresolved_variables)}")
    else:
        lines.append(f"- {tr('unresolved', lang)}: {tr('none', lang)}")

    lines.extend(
        [
            "",
            tr("line_matching", lang),
            f"- {plan.line_matching_note}",
            "",
            tr("folder_scope", lang),
        ]
    )

    for folder in plan.folder_scope:
        optional_label = (
            tr("optional_label", lang) if folder["optional"] else tr("required_label", lang)
        )
        rule_text = (
            ", ".join(folder["rules"]) if folder["rules"] else tr("no_rules_configured", lang)
        )
        desc = folder["description"] or tr("no_description", lang)
        lines.append(
            f"- {folder['path']} ({optional_label}): {desc}. {tr('checks_label', lang)}: {rule_text}"
        )

    lines.extend(["", "Global Checks"])
    lines[-1] = tr("global_checks", lang)
    if plan.global_checks:
        for check in plan.global_checks:
            lines.append(f"- {check}")
    else:
        lines.append(f"- {tr('none', lang)}")

    if plan.notes:
        lines.extend(["", tr("section_trust_notes", lang)])
        for note in plan.notes:
            lines.append(f"- {note}")

    return "\n".join(lines)


def format_issue_detail_text(issue: Optional[IssueInsight], lang: str = "en") -> str:
    """Render a detailed issue explanation for drill-down views."""

    lang = normalize_lang(lang)
    if issue is None:
        return tr("issue_detail_header_default", lang)

    lines = [
        f"{issue.scope} - {issue.check_label}",
        "",
        f"{tr('col_severity', lang)}: {severity_text(issue.severity, lang)}",
        f"{tr('col_status', lang)}: {status_text(issue.status.value, lang)}",
        f"{tr('col_category', lang)}: {issue.category}",
        "",
        tr("finding_section", lang),
        f"- {issue.message}",
        "",
        tr("recommendation", lang),
        f"- {issue.action_hint}",
    ]

    if issue.technical_message and issue.technical_message != issue.message:
        lines.extend(
            [
                "",
                tr("technical_message", lang),
                f"- {issue.technical_message}",
            ]
        )

    if issue.details:
        lines.extend(["", tr("evidence_section", lang)])
        for detail in issue.details[:20]:
            lines.append(f"- {detail}")
        if len(issue.details) > 20:
            lines.append(f"- ... +{len(issue.details) - 20} more")

    return "\n".join(lines)


def _folder_file_count(report: ValidationReport, scope: str) -> int:
    return sum(
        1
        for file_info in report.file_inventory
        if file_info.folder == scope or file_info.folder.startswith(scope + "/")
    )


def _folder_from_scope(report: ValidationReport, scope: str):
    return next((folder for folder in report.folder_results if folder.path == scope), None)


def build_report_preview_text(report: ValidationReport, lang: Optional[str] = None) -> str:
    """Render a plain-text preview of the report narrative before export."""

    lang = normalize_lang(lang or getattr(report, "language", "en"))
    insight = build_readiness_insight(report, lang)
    lines = [
        tr("report_preview_header", lang),
        "",
        tr("executive_summary", lang),
        f"- {insight.headline}",
        f"- {tr('profile', lang)}: {report.profile_name}",
        f"- {tr('project', lang)}: {report.project or tr('na', lang)}",
        f"- {tr('client', lang)}: {report.client or tr('na', lang)}",
        f"- {tr('delivery_path', lang)}: {report.delivery_path}",
        f"- {tr('total_files', lang)}: {report.total_files:,}",
        f"- {tr('total_size', lang)}: {format_size(report.total_size_bytes)}",
    ]

    lines.extend(
        [
            "",
            tr("section_validation_basis", lang),
            f"- {tr('base_profile', lang)}: {report.base_profile or tr('direct_profile', lang)}",
            f"- {tr('line_list_source', lang)}: {report.line_list_source or tr('not_used', lang)}",
            f"- {tr('resolved_variables', lang)}: "
            + (
                ", ".join(
                    f"{key}={value or '<empty>'}"
                    for key, value in sorted(report.resolved_variables.items())
                )
                or tr("none", lang)
            ),
        ]
    )

    if insight.top_actions:
        lines.extend(["", tr("corrective_action_focus", lang)])
        for action in insight.top_actions:
            lines.append(f"- {action}")

    lines.extend(["", tr("section_readiness", lang)])
    for section in insight.section_overview:
        description = section.get("description") or tr("na", lang)
        primary = section.get("primary_message") or tr("no_issues_raised", lang)
        lines.append(
            f"- {section['scope']}: {status_text(section['status'].value, lang)} | {description} | {primary}"
        )

    if insight.trust_notes:
        lines.extend(["", tr("section_trust_notes", lang)])
        for note in insight.trust_notes:
            lines.append(f"- {note}")

    return "\n".join(lines)


def build_section_compare_text(
    report: ValidationReport,
    left_scope: Optional[str],
    right_scope: Optional[str],
    lang: Optional[str] = None,
) -> str:
    """Render a side-by-side comparison between two validated sections."""

    lang = normalize_lang(lang or getattr(report, "language", "en"))
    if not left_scope or not right_scope:
        return tr("no_compare", lang)

    insight = build_readiness_insight(report, lang)
    issues_by_scope: Dict[str, List[IssueInsight]] = {}
    for issue in insight.issues:
        issues_by_scope.setdefault(issue.scope, []).append(issue)

    coverage = insight.coverage

    def build_block(scope: str) -> List[str]:
        folder = _folder_from_scope(report, scope)
        if folder is None:
            return [scope, f"- {tr('section_not_found', lang)}"]

        folder_issues = issues_by_scope.get(scope, [])
        coverage_note = tr("not_tracked", lang)
        if coverage and scope in coverage.coverage_by_folder:
            if lang == "ko":
                coverage_note = f"계획 라인 기준 {coverage.coverage_by_folder[scope]}% 존재"
            else:
                coverage_note = f"{coverage.coverage_by_folder[scope]}% of planned lines present"

        lines = [
            scope,
            f"- {tr('status_line', lang)}: {status_text(folder.status.value, lang)}",
            f"- {tr('description_line', lang)}: {folder.description or tr('na', lang)}",
            f"- {tr('file_count_line', lang)}: {_folder_file_count(report, scope)}",
            f"- {tr('issue_count_line', lang)}: {len(folder_issues)}",
            f"- {tr('coverage_line', lang)}: {coverage_note}",
        ]
        if folder_issues:
            top_issue = folder_issues[0]
            lines.append(
                f"- {tr('top_issue_line', lang)}: [{severity_text(top_issue.severity, lang)}] {top_issue.check_label} - {top_issue.message}"
            )
        else:
            lines.append(f"- {tr('top_issue_line', lang)}: {tr('none', lang)}")
        return lines

    left_block = build_block(left_scope)
    right_block = build_block(right_scope)

    comparison_lines = [
        tr("compare_header", lang),
        "",
        tr("compare_left", lang),
    ]
    comparison_lines.extend(left_block)
    comparison_lines.extend(["", tr("compare_right", lang)])
    comparison_lines.extend(right_block)
    comparison_lines.extend(["", tr("compare_section", lang)])

    left_issue_count = len(issues_by_scope.get(left_scope, []))
    right_issue_count = len(issues_by_scope.get(right_scope, []))
    if left_issue_count == right_issue_count:
        comparison_lines.append(f"- {tr('same_issue_count', lang)}")
    elif left_issue_count > right_issue_count:
        comparison_lines.append(
            f"- {tr('riskier_by_issues', lang, scope=left_scope, count=left_issue_count - right_issue_count)}"
        )
    else:
        comparison_lines.append(
            f"- {tr('riskier_by_issues', lang, scope=right_scope, count=right_issue_count - left_issue_count)}"
        )

    if coverage and left_scope in coverage.coverage_by_folder and right_scope in coverage.coverage_by_folder:
        delta = coverage.coverage_by_folder[left_scope] - coverage.coverage_by_folder[right_scope]
        if delta == 0:
            comparison_lines.append(f"- {tr('same_coverage', lang)}")
        elif delta > 0:
            comparison_lines.append(
                f"- {tr('better_coverage', lang, scope=left_scope, count=delta)}"
            )
        else:
            comparison_lines.append(
                f"- {tr('better_coverage', lang, scope=right_scope, count=abs(delta))}"
            )

    return "\n".join(comparison_lines)
