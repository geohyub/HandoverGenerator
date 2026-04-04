from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import QThread, Signal

from handover_check.config import ConfigError, load_and_merge_profile, load_yaml, resolve_variables
from handover_check.engine import ValidationEngine
from handover_check.i18n import normalize_lang, tr
from handover_check.insights import (
    ProfilePlanInsight,
    ReadinessInsight,
    ValidationReport,
    build_profile_plan,
    build_readiness_insight,
    build_report_preview_text,
)
from handover_check.reporters.excel import generate_excel_report


THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]


def _project_base_profile() -> Path:
    return PROJECT_ROOT / "profiles" / "base_geoview.yaml"


@dataclass
class ValidationRequest:
    delivery_path: str = ""
    profile_path: str = ""
    linelist_path: str = ""
    output_path: str = ""
    folder_filter: str = ""
    basic: bool = False
    variables: dict[str, str] = field(default_factory=dict)
    language: str = "ko"


@dataclass
class ProfileBundle:
    profile: dict
    variables: dict[str, str]
    plan: ProfilePlanInsight


@dataclass
class ValidationBundle:
    request: ValidationRequest
    profile_bundle: ProfileBundle
    report: ValidationReport
    readiness: ReadinessInsight
    preview_text: str
    export_path: str = ""


def prepare_profile_bundle(request: ValidationRequest) -> ProfileBundle:
    lang = normalize_lang(request.language)
    if not request.basic and not request.profile_path:
        raise ConfigError(tr("profile_required", lang))

    if request.basic or not request.profile_path:
        profile = load_yaml(_project_base_profile())
    else:
        profile = load_and_merge_profile(Path(request.profile_path))

    variables = resolve_variables(profile, request.variables)
    plan = build_profile_plan(
        profile,
        variables,
        basic=request.basic,
        folder_filter=request.folder_filter or None,
        linelist_override=request.linelist_path or None,
        lang=lang,
    )
    return ProfileBundle(profile=profile, variables=variables, plan=plan)


def run_validation_sync(
    request: ValidationRequest,
    status_cb: Optional[Callable[[str], None]] = None,
) -> ValidationBundle:
    lang = normalize_lang(request.language)
    emit = status_cb or (lambda _msg: None)
    profile_bundle = prepare_profile_bundle(request)

    emit(tr("initializing_engine", lang))
    engine = ValidationEngine(
        delivery_path=Path(request.delivery_path),
        profile_path=Path(request.profile_path) if request.profile_path else None,
        linelist_path=Path(request.linelist_path) if request.linelist_path else None,
        cli_vars=request.variables,
        basic=request.basic,
        folder_filter=request.folder_filter or None,
        language=lang,
    )
    emit(tr("running_validation", lang))
    report = engine.run()
    readiness = build_readiness_insight(report, lang)
    preview_text = build_report_preview_text(report, lang)

    export_path = ""
    if request.output_path:
        output = Path(request.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        emit(tr("saving_excel_report", lang, path=str(output)))
        generate_excel_report(report, output)
        emit(tr("excel_report_saved", lang))
        export_path = str(output)

    return ValidationBundle(
        request=request,
        profile_bundle=profile_bundle,
        report=report,
        readiness=readiness,
        preview_text=preview_text,
        export_path=export_path,
    )


class ValidationWorker(QThread):
    status = Signal(str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, request: ValidationRequest):
        super().__init__()
        self.request = request

    def run(self) -> None:
        try:
            bundle = run_validation_sync(self.request, status_cb=self.status.emit)
            self.finished.emit(bundle)
        except Exception as exc:  # pragma: no cover
            self.failed.emit(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
