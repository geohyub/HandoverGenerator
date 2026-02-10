"""Excel detailed report generation with 5 tabs."""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from handover_check.models import ResultStatus, ValidationReport
from handover_check.validators.total_size import format_size


# Style constants
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
PASS_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
FAIL_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
WARN_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
SKIP_FILL = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
INFO_FILL = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)
WRAP_ALIGNMENT = Alignment(wrap_text=True, vertical="top")

STATUS_FILLS = {
    ResultStatus.PASS: PASS_FILL,
    ResultStatus.FAIL: FAIL_FILL,
    ResultStatus.WARNING: WARN_FILL,
    ResultStatus.SKIP: SKIP_FILL,
    ResultStatus.INFO: INFO_FILL,
}


def _write_header(ws, headers, row=1):
    """Write header row with formatting."""
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")


def _auto_width(ws, min_width=10, max_width=60):
    """Auto-adjust column widths."""
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        adjusted = min(max(max_len + 2, min_width), max_width)
        ws.column_dimensions[col_letter].width = adjusted


def _write_summary_tab(wb, report: ValidationReport):
    """Tab 1: Summary — folder-level overview."""
    ws = wb.active
    ws.title = "Summary"

    headers = ["Folder", "Status", "Files Found", "Files Expected", "Issues"]
    _write_header(ws, headers)

    row = 2
    for fr in report.folder_results:
        status = fr.status

        # Count files found
        files_found = ""
        files_expected = ""
        issues_text = ""

        for rr in fr.rule_results:
            if rr.rule_type == "count_match" and rr.status != ResultStatus.SKIP:
                parts = rr.message.split("/")
                if len(parts) == 2:
                    files_found = parts[0]
                    files_expected = parts[1].split(" ")[0]
            if rr.status in (ResultStatus.FAIL, ResultStatus.WARNING):
                if issues_text:
                    issues_text += "; "
                issues_text += rr.message

        if not files_found:
            # Count actual files in inventory
            count = sum(
                1 for fi in report.file_inventory
                if fi.folder == fr.path or fi.folder.startswith(fr.path + "/")
            )
            files_found = str(count) if count > 0 else ""

        ws.cell(row=row, column=1, value=fr.path).border = THIN_BORDER
        status_cell = ws.cell(row=row, column=2, value=status.value)
        status_cell.fill = STATUS_FILLS.get(status, SKIP_FILL)
        status_cell.border = THIN_BORDER
        ws.cell(row=row, column=3, value=files_found).border = THIN_BORDER
        ws.cell(row=row, column=4, value=files_expected).border = THIN_BORDER
        ws.cell(row=row, column=5, value=issues_text or "\u2014").border = THIN_BORDER
        ws[f"E{row}"].alignment = WRAP_ALIGNMENT
        row += 1

    # Global rules
    for gr in report.global_results:
        ws.cell(row=row, column=1, value=f"GLOBAL: {gr.rule_type}").border = THIN_BORDER
        status_cell = ws.cell(row=row, column=2, value=gr.status.value)
        status_cell.fill = STATUS_FILLS.get(gr.status, SKIP_FILL)
        status_cell.border = THIN_BORDER
        ws.cell(row=row, column=3, value="").border = THIN_BORDER
        ws.cell(row=row, column=4, value="").border = THIN_BORDER
        detail_text = gr.message
        if gr.details:
            detail_text += f" ({len(gr.details)} items)"
        ws.cell(row=row, column=5, value=detail_text).border = THIN_BORDER
        row += 1

    _auto_width(ws)


def _write_issues_tab(wb, report: ValidationReport):
    """Tab 2: Issues — detailed list of all non-PASS results."""
    ws = wb.create_sheet("Issues")
    headers = ["#", "Folder", "Rule", "Status", "Description", "File(s)"]
    _write_header(ws, headers)

    row = 2
    issue_num = 1

    for fr in report.folder_results:
        for rr in fr.rule_results:
            if rr.status in (ResultStatus.FAIL, ResultStatus.WARNING):
                ws.cell(row=row, column=1, value=issue_num).border = THIN_BORDER
                ws.cell(row=row, column=2, value=fr.path).border = THIN_BORDER
                ws.cell(row=row, column=3, value=rr.rule_type).border = THIN_BORDER
                status_cell = ws.cell(row=row, column=4, value=rr.status.value)
                status_cell.fill = STATUS_FILLS.get(rr.status, SKIP_FILL)
                status_cell.border = THIN_BORDER
                ws.cell(row=row, column=5, value=rr.message).border = THIN_BORDER
                files_text = "\n".join(rr.details[:20])
                if len(rr.details) > 20:
                    files_text += f"\n... +{len(rr.details) - 20} more"
                ws.cell(row=row, column=6, value=files_text).border = THIN_BORDER
                ws[f"F{row}"].alignment = WRAP_ALIGNMENT
                row += 1
                issue_num += 1

    for gr in report.global_results:
        if gr.status in (ResultStatus.FAIL, ResultStatus.WARNING):
            ws.cell(row=row, column=1, value=issue_num).border = THIN_BORDER
            ws.cell(row=row, column=2, value="(global)").border = THIN_BORDER
            ws.cell(row=row, column=3, value=gr.rule_type).border = THIN_BORDER
            status_cell = ws.cell(row=row, column=4, value=gr.status.value)
            status_cell.fill = STATUS_FILLS.get(gr.status, SKIP_FILL)
            status_cell.border = THIN_BORDER
            ws.cell(row=row, column=5, value=gr.message).border = THIN_BORDER
            files_text = "\n".join(gr.details[:20])
            if len(gr.details) > 20:
                files_text += f"\n... +{len(gr.details) - 20} more"
            ws.cell(row=row, column=6, value=files_text).border = THIN_BORDER
            ws[f"F{row}"].alignment = WRAP_ALIGNMENT
            row += 1
            issue_num += 1

    if issue_num == 1:
        ws.cell(row=2, column=1, value="No issues found")

    _auto_width(ws)


def _write_line_coverage_tab(wb, report: ValidationReport):
    """Tab 3: Line Coverage Matrix."""
    ws = wb.create_sheet("Line Coverage")

    if not report.line_coverage:
        ws.cell(row=1, column=1, value="No line list used — line coverage not available")
        return

    coverage = report.line_coverage
    folders = coverage["folders"]
    lines = coverage["lines"]
    matrix = coverage["matrix"]

    # Headers
    headers = ["Line"] + folders
    _write_header(ws, headers)

    row = 2
    check_mark = "\u2713"
    cross_mark = "\u2717"
    for line in lines:
        ws.cell(row=row, column=1, value=line).border = THIN_BORDER
        for col_idx, folder in enumerate(folders, 2):
            found = matrix.get(line, {}).get(folder, False)
            cell = ws.cell(row=row, column=col_idx)
            if found:
                cell.value = check_mark
                cell.fill = PASS_FILL
            else:
                cell.value = cross_mark
                cell.fill = FAIL_FILL
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal="center")
        row += 1

    _auto_width(ws)


def _write_file_inventory_tab(wb, report: ValidationReport):
    """Tab 4: File Inventory — complete file listing."""
    ws = wb.create_sheet("File Inventory")
    headers = ["#", "Folder", "Filename", "Size (MB)", "Modified", "Naming OK", "Notes"]
    _write_header(ws, headers)

    row = 2
    for idx, fi in enumerate(report.file_inventory, 1):
        ws.cell(row=row, column=1, value=idx).border = THIN_BORDER
        ws.cell(row=row, column=2, value=fi.folder).border = THIN_BORDER
        ws.cell(row=row, column=3, value=fi.filename).border = THIN_BORDER
        size_mb = fi.size_bytes / (1024 * 1024)
        ws.cell(row=row, column=4, value=round(size_mb, 2)).border = THIN_BORDER
        ws.cell(row=row, column=5, value=fi.modified).border = THIN_BORDER

        naming_cell = ws.cell(row=row, column=6)
        if fi.naming_ok is True:
            naming_cell.value = check_mark if 'check_mark' in dir() else "\u2713"
            naming_cell.fill = PASS_FILL
        elif fi.naming_ok is False:
            naming_cell.value = "\u2717"
            naming_cell.fill = FAIL_FILL
        else:
            naming_cell.value = "\u2014"
        naming_cell.border = THIN_BORDER
        naming_cell.alignment = Alignment(horizontal="center")

        ws.cell(row=row, column=7, value=fi.notes).border = THIN_BORDER
        row += 1

        # Limit rows for very large inventories
        if idx >= 10000:
            ws.cell(row=row, column=1, value="...")
            ws.cell(row=row, column=2, value=f"Truncated at 10,000 files (total: {len(report.file_inventory)})")
            break

    _auto_width(ws)


def _write_naming_violations_tab(wb, report: ValidationReport):
    """Tab 5: Naming Violations."""
    ws = wb.create_sheet("Naming Violations")
    headers = ["#", "Folder", "Filename", "Expected Pattern", "Issue"]
    _write_header(ws, headers)

    row = 2
    for idx, violation in enumerate(report.naming_violations, 1):
        ws.cell(row=row, column=1, value=idx).border = THIN_BORDER
        ws.cell(row=row, column=2, value=violation.get("folder", "")).border = THIN_BORDER
        ws.cell(row=row, column=3, value=violation.get("filename", "")).border = THIN_BORDER
        ws.cell(row=row, column=4, value=violation.get("expected_pattern", "")).border = THIN_BORDER
        ws[f"D{row}"].alignment = WRAP_ALIGNMENT
        ws.cell(row=row, column=5, value=violation.get("issue", "")).border = THIN_BORDER
        row += 1

    if not report.naming_violations:
        ws.cell(row=2, column=1, value="No naming violations found")

    _auto_width(ws)


def generate_excel_report(report: ValidationReport, output_path: Path) -> None:
    """Generate the full Excel report with all 5 tabs."""
    wb = Workbook()

    _write_summary_tab(wb, report)
    _write_issues_tab(wb, report)
    _write_line_coverage_tab(wb, report)
    _write_file_inventory_tab(wb, report)
    _write_naming_violations_tab(wb, report)

    wb.save(str(output_path))
