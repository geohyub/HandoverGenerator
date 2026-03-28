"""Console summary output."""

from handover_check.insights import build_readiness_insight
from handover_check.i18n import normalize_lang, status_text, tr
from handover_check.models import ResultStatus, ValidationReport
from handover_check.validators.total_size import format_size


# ANSI color codes
COLORS = {
    ResultStatus.PASS: "\033[92m",     # green
    ResultStatus.FAIL: "\033[91m",     # red
    ResultStatus.WARNING: "\033[93m",  # yellow
    ResultStatus.SKIP: "\033[90m",     # gray
    ResultStatus.INFO: "\033[94m",     # blue
}
RESET = "\033[0m"


def _colored(status: ResultStatus, text: str) -> str:
    return f"{COLORS.get(status, '')}{text}{RESET}"


def print_console_report(report: ValidationReport) -> None:
    """Print formatted console summary."""
    width = 64
    lang = normalize_lang(getattr(report, "language", "en"))
    insight = build_readiness_insight(report, lang)

    print("=" * width)
    print(f"  {tr('console_header', lang)}")
    if report.client or report.project:
        parts = []
        if report.project:
            parts.append(f"{tr('project', lang)}: {report.project}")
        if report.client:
            parts.append(f"{tr('client', lang)}: {report.client}")
        print(f"  {' | '.join(parts)}")
    print(f"  {tr('profile', lang)}: {report.profile_name}")
    print(f"  {tr('delivery_path', lang)}: {report.delivery_path}")
    print(f"  {tr('validated_on', lang)}: {report.timestamp}")
    print("=" * width)

    print()
    print(f"{tr('tab_summary', lang)}:")
    print(f"  {insight.headline}")
    if insight.top_actions:
        print(f"  {tr('section_next_actions', lang)}:")
        for action in insight.top_actions:
            print(f"    - {action}")
    if insight.trust_notes:
        print(f"  {tr('section_trust_notes', lang)}:")
        for note in insight.trust_notes:
            print(f"    - {note}")

    # Folder checks
    if report.folder_results:
        print()
        print(f"{tr('folder_checks', lang)}:")
        for fr in report.folder_results:
            # Determine folder summary
            status = fr.status
            label = _colored(status, status_text(status.value, lang))

            # Count info for count_match results
            count_info = ""
            for rr in fr.rule_results:
                if rr.rule_type == "count_match" and rr.status != ResultStatus.SKIP:
                    count_info = f"  ({rr.message})"
                    break

            # Format line with dots
            path_str = fr.path
            max_path = 38
            if len(path_str) > max_path:
                path_str = "..." + path_str[-(max_path - 3):]
            dots = "." * max(2, 42 - len(path_str))
            print(f"  {path_str} {dots} {label}{count_info}")

            # Print details for non-PASS results
            if status in (ResultStatus.FAIL, ResultStatus.WARNING):
                for rr in fr.rule_results:
                    if rr.status in (ResultStatus.FAIL, ResultStatus.WARNING):
                        for detail in rr.details[:5]:  # limit to 5 details
                            print(f"    \u2514 {detail}")
                        if len(rr.details) > 5:
                            print(f"    \u2514 ... and {len(rr.details) - 5} more")

    # Global checks
    if report.global_results:
        print()
        print(f"{tr('global_checks_console', lang)}:")
        for gr in report.global_results:
            status = gr.status
            label = _colored(status, status_text(status.value, lang))

            rule_name = gr.rule_type.replace("_", " ").title()
            dots = "." * max(2, 42 - len(rule_name))
            extra = ""
            if gr.details:
                extra = f"  ({tr('found_count', lang, count=len(gr.details))})"

            if status == ResultStatus.INFO:
                print(f"  {rule_name} {dots} {label}  {gr.message}")
            else:
                print(f"  {rule_name} {dots} {label}{extra}")

            if status in (ResultStatus.FAIL, ResultStatus.WARNING):
                for detail in gr.details[:5]:
                    print(f"    \u2514 {detail}")
                if len(gr.details) > 5:
                    print(f"    \u2514 ... and {len(gr.details) - 5} more")

    # Summary
    print()
    print("=" * width)
    total_size_str = format_size(report.total_size_bytes)
    print(
        f"  {tr('total_files', lang)}: {report.total_files:,}  |  "
        f"{tr('total_size', lang)}: {total_size_str}"
    )

    overall = report.overall_status
    issues = report.fail_count + report.warning_count
    if overall == ResultStatus.PASS:
        passed_text = tr("all_checks_passed", lang)
        print(
            f"  {tr('result_label', lang)}: "
            f"{_colored(overall, status_text('PASS', lang))} ({passed_text})"
        )
    else:
        result_str = _colored(overall, status_text(overall.value, lang))
        issue_text = tr("issues_found_count", lang, count=issues)
        print(f"  {tr('result_label', lang)}: {result_str} ({issue_text})")
    print("=" * width)
