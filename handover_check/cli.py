"""Click CLI entry point for handover-check."""

import sys
from pathlib import Path
from typing import Optional, Tuple

import click
import yaml

from handover_check.config import ConfigError, load_and_merge_profile, resolve_variables, substitute_variables
from handover_check.engine import ValidationEngine
from handover_check.models import ResultStatus
from handover_check.reporters.console import print_console_report
from handover_check.reporters.excel import generate_excel_report


def parse_var(ctx, param, value) -> dict:
    """Parse --var KEY=VALUE pairs into a dict."""
    result = {}
    for item in value:
        if "=" not in item:
            raise click.BadParameter(f"Variable must be KEY=VALUE format: {item}")
        key, val = item.split("=", 1)
        result[key.strip()] = val.strip()
    return result


@click.group()
@click.version_option(version="1.0.0", prog_name="handover-check")
def cli():
    """Handover Package Validation Tool.

    Validates project delivery folders against client-specific specifications.
    Read-only operation — never modifies any files.
    """
    pass


@cli.command()
@click.option("--path", required=True, type=click.Path(exists=True),
              help="Path to delivery folder root")
@click.option("--profile", type=click.Path(exists=True), default=None,
              help="Path to project profile YAML")
@click.option("--linelist", type=click.Path(exists=True), default=None,
              help="Path to line list CSV (overrides profile)")
@click.option("--var", multiple=True, callback=parse_var, expose_value=True,
              help="Variable injection (KEY=VALUE), can be repeated")
@click.option("--output", type=click.Path(), default=None,
              help="Path for Excel report output")
@click.option("--summary-only", is_flag=True, default=False,
              help="Print console summary only, skip Excel")
@click.option("--folder", default=None,
              help="Validate only this subfolder (relative to delivery root)")
@click.option("--basic", is_flag=True, default=False,
              help="Use base_geoview.yaml only, ignore project profiles")
@click.option("--lang", type=click.Choice(["ko", "en"]), default="ko",
              help="Output language for console and report")
def validate(path, profile, linelist, var, output, summary_only, folder, basic, lang):
    """Validate a delivery folder against a profile."""
    try:
        engine = ValidationEngine(
            delivery_path=Path(path),
            profile_path=Path(profile) if profile else None,
            linelist_path=Path(linelist) if linelist else None,
            cli_vars=var,
            basic=basic,
            folder_filter=folder,
            language=lang,
        )

        report = engine.run()

        # Console output
        print_console_report(report)

        # Excel output
        if not summary_only and output:
            output_path = Path(output)
            generate_excel_report(report, output_path)
            click.echo(f"\nExcel report saved to: {output_path}")
        elif not summary_only and not output:
            # Auto-generate output filename if not summary-only and no output specified
            pass

        # Exit code
        if report.overall_status == ResultStatus.FAIL:
            sys.exit(1)
        else:
            sys.exit(0)

    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)


@cli.command("show-profile")
@click.option("--profile", required=True, type=click.Path(exists=True),
              help="Path to project profile YAML")
@click.option("--var", multiple=True, callback=parse_var, expose_value=True,
              help="Variable injection (KEY=VALUE)")
def show_profile(profile, var):
    """Show the merged profile (for debugging)."""
    try:
        merged = load_and_merge_profile(Path(profile))
        variables = resolve_variables(merged, var)
        merged["variables"] = variables

        click.echo("# Merged profile (base + project):")
        click.echo("# Variables resolved with CLI --var values")
        click.echo(yaml.dump(merged, default_flow_style=False, allow_unicode=True, sort_keys=False))

    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(2)


def main():
    cli()


if __name__ == "__main__":
    main()
