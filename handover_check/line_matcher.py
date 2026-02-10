"""Line list CSV matching logic."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd


class LineMatchError(Exception):
    """Raised when line list processing fails."""
    pass


class LineMatcher:
    """Matches files against a line list CSV."""

    def __init__(
        self,
        csv_path: Path,
        line_id_column: str,
        status_column: Optional[str] = None,
        status_filter: Optional[str] = None,
    ):
        if not csv_path.exists():
            raise LineMatchError(f"Line list not found: {csv_path}")

        try:
            self.df = pd.read_csv(csv_path)
        except Exception as e:
            raise LineMatchError(f"Failed to read line list CSV: {e}")

        if line_id_column not in self.df.columns:
            raise LineMatchError(
                f"Column '{line_id_column}' not found in line list. "
                f"Available columns: {list(self.df.columns)}"
            )

        self.line_id_column = line_id_column
        self.line_ids = self._get_filtered_lines(
            line_id_column, status_column, status_filter
        )

    def _get_filtered_lines(
        self,
        id_col: str,
        status_col: Optional[str],
        status_filter: Optional[str],
    ) -> Set[str]:
        """Get filtered line IDs from the DataFrame."""
        df = self.df
        if status_col and status_filter:
            if status_col not in df.columns:
                raise LineMatchError(
                    f"Status column '{status_col}' not found in line list. "
                    f"Available columns: {list(df.columns)}"
                )
            df = df[df[status_col] == status_filter]
        return set(df[id_col].astype(str).str.strip())

    def compare(self, found_lines: Set[str]) -> Dict:
        """Compare found lines (from filenames) against expected lines.

        Returns dict with expected_count, found_count, missing, extra, matched.
        """
        return {
            "expected_count": len(self.line_ids),
            "found_count": len(found_lines),
            "missing": sorted(self.line_ids - found_lines),
            "extra": sorted(found_lines - self.line_ids),
            "matched": sorted(self.line_ids & found_lines),
        }

    @staticmethod
    def extract_lines_from_files(
        files: List[Path], naming_regex: str
    ) -> Set[str]:
        """Extract line identifiers from filenames using a naming regex.

        The regex must contain a named group (?P<line>...).
        """
        pattern = re.compile(naming_regex)
        lines = set()
        for f in files:
            m = pattern.match(f.name)
            if m and "line" in m.groupdict():
                lines.add(m.group("line"))
        return lines
