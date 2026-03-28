"""Tests for readiness and profile-plan insights."""

import shutil
from pathlib import Path

from handover_check.config import load_and_merge_profile, resolve_variables
from handover_check.engine import ValidationEngine
from handover_check.insights import (
    build_profile_plan,
    build_readiness_insight,
    build_report_preview_text,
    build_section_compare_text,
    format_profile_plan_text,
    format_issue_detail_text,
    format_readiness_text,
)


def test_build_readiness_insight(tmp_delivery, tmp_linelist, test_profile_yaml):
    shutil.copy(tmp_linelist, tmp_delivery / "line_list.csv")

    engine = ValidationEngine(
        delivery_path=tmp_delivery,
        profile_path=test_profile_yaml,
        cli_vars={"project_code": "TEST2025", "area_code": "RS"},
    )
    report = engine.run()

    insight = build_readiness_insight(report)

    assert insight.readiness_label == "Not ready"
    assert insight.failed_checks >= 2
    assert insight.blocker_count >= 1
    assert insight.coverage is not None
    assert insight.coverage.expected_lines == 3
    assert any("04_Reports" in action for action in insight.top_actions)


def test_build_profile_plan(test_profile_yaml):
    merged = load_and_merge_profile(Path(test_profile_yaml))
    variables = resolve_variables(
        merged,
        {"project_code": "TEST2025", "area_code": "RS"},
    )

    plan = build_profile_plan(merged, variables)

    assert plan.profile_name == "Test_Profile"
    assert plan.client == "TestClient"
    assert plan.project == "Test Project 2025"
    assert len(plan.folder_scope) == 5
    assert plan.unresolved_variables == []
    assert "line_list.csv" in plan.line_matching_note


def test_report_preview_and_compare_text(tmp_delivery, tmp_linelist, test_profile_yaml):
    shutil.copy(tmp_linelist, tmp_delivery / "line_list.csv")

    engine = ValidationEngine(
        delivery_path=tmp_delivery,
        profile_path=test_profile_yaml,
        cli_vars={"project_code": "TEST2025", "area_code": "RS"},
    )
    report = engine.run()

    preview_text = build_report_preview_text(report)
    compare_text = build_section_compare_text(
        report,
        "01_Raw_Data/01_SBP",
        "01_Raw_Data/02_MBES",
    )
    issue_detail = format_issue_detail_text(build_readiness_insight(report).issues[0])

    assert "Handover readiness report preview" in preview_text
    assert "Section comparison" in compare_text
    assert "01_Raw_Data/02_MBES" in compare_text
    assert "Recommended Action" in issue_detail


def test_korean_localized_insight_outputs(
    tmp_delivery,
    tmp_linelist,
    test_profile_yaml,
):
    shutil.copy(tmp_linelist, tmp_delivery / "line_list.csv")

    engine = ValidationEngine(
        delivery_path=tmp_delivery,
        profile_path=test_profile_yaml,
        cli_vars={"project_code": "TEST2025", "area_code": "RS"},
        language="ko",
    )
    report = engine.run()

    merged = load_and_merge_profile(Path(test_profile_yaml))
    variables = resolve_variables(
        merged,
        {"project_code": "TEST2025", "area_code": "RS"},
    )
    plan = build_profile_plan(merged, variables, lang="ko")
    readiness = build_readiness_insight(report, "ko")

    readiness_text = format_readiness_text(readiness, "ko")
    preview_text = build_report_preview_text(report, "ko")
    compare_text = build_section_compare_text(
        report,
        "01_Raw_Data/01_SBP",
        "01_Raw_Data/02_MBES",
        "ko",
    )
    issue_detail = format_issue_detail_text(readiness.issues[0], "ko")
    plan_text = format_profile_plan_text(plan, "ko")

    assert "준비도" in readiness_text
    assert "납품 준비도 보고서 미리보기" in preview_text
    assert "섹션 비교" in compare_text
    assert "권장 조치" in issue_detail
    assert "검증 계획" in plan_text
