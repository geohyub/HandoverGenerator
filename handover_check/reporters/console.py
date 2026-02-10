"""Console summary output."""

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

    print("=" * width)
    print("  Handover Package Validation Report")
    if report.client or report.project:
        parts = []
        if report.project:
            parts.append(f"Project: {report.project}")
        if report.client:
            parts.append(f"Client: {report.client}")
        print(f"  {' | '.join(parts)}")
    print(f"  Profile: {report.profile_name}")
    print(f"  Path: {report.delivery_path}")
    print(f"  Date: {report.timestamp}")
    print("=" * width)

    # Folder checks
    if report.folder_results:
        print()
        print("Folder Checks:")
        for fr in report.folder_results:
            # Determine folder summary
            status = fr.status
            label = _colored(status, status.value)

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
        print("Global Checks:")
        for gr in report.global_results:
            status = gr.status
            label = _colored(status, status.value)

            rule_name = gr.rule_type.replace("_", " ").title()
            dots = "." * max(2, 42 - len(rule_name))
            extra = ""
            if gr.details:
                extra = f"  ({len(gr.details)} found)"

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
    print(f"  Total files: {report.total_files:,}  |  Total size: {total_size_str}")

    overall = report.overall_status
    issues = report.fail_count + report.warning_count
    if overall == ResultStatus.PASS:
        print(f"  Result: {_colored(overall, 'PASS')} (all checks passed)")
    else:
        result_str = _colored(overall, overall.value)
        print(f"  Result: {result_str} ({issues} issue(s) found)")
    print("=" * width)
