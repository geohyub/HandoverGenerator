"""checksum_file validator — verify checksum file exists and contents match."""

import hashlib
from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class ChecksumFileValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        algorithm = self.config.get("algorithm", "md5")
        expected_file = self.config.get("expected_file", f"checksum.{algorithm}")

        if not folder_path.exists():
            return RuleResult(
                rule_type="checksum_file",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        checksum_path = folder_path / expected_file
        if not checksum_path.exists():
            return RuleResult(
                rule_type="checksum_file",
                status=ResultStatus.FAIL,
                message=f"Checksum file '{expected_file}' not found",
                folder_path=str(folder_path),
            )

        # Parse checksum file and verify
        issues = []
        try:
            lines = checksum_path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 1)
                if len(parts) != 2:
                    # Try alternative format: hash *filename or hash  filename
                    parts = line.split("*", 1)
                    if len(parts) == 2:
                        expected_hash = parts[0].strip()
                        filename = parts[1].strip()
                    else:
                        continue
                else:
                    expected_hash = parts[0].strip()
                    filename = parts[1].strip().lstrip("*")

                file_path = folder_path / filename
                if not file_path.exists():
                    issues.append(f"File listed in checksum but not found: {filename}")
                    continue

                # Compute actual hash
                h = hashlib.new(algorithm)
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        h.update(chunk)
                actual_hash = h.hexdigest()

                if actual_hash.lower() != expected_hash.lower():
                    issues.append(
                        f"Checksum mismatch for {filename}: "
                        f"expected {expected_hash[:16]}..., got {actual_hash[:16]}..."
                    )
        except Exception as e:
            return RuleResult(
                rule_type="checksum_file",
                status=ResultStatus.FAIL,
                message=f"Error reading checksum file: {e}",
                folder_path=str(folder_path),
            )

        if issues:
            return RuleResult(
                rule_type="checksum_file",
                status=ResultStatus.FAIL,
                message=f"{len(issues)} checksum issue(s)",
                details=issues,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="checksum_file",
            status=ResultStatus.PASS,
            message=f"Checksum file '{expected_file}' verified OK",
            folder_path=str(folder_path),
        )
