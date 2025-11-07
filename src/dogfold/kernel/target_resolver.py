"""Target resolution utilities for spec-core scaffolding verbs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Target:
    """Representation of a registered scaffolding target."""

    key: str
    package: str
    root: Path
    templates: Path
    repo_root: Path
    project_root: Path

    def to_dict(self) -> Dict[str, object]:
        return {
            "key": self.key,
            "package": self.package,
            "root": self.root,
            "templates": self.templates,
            "repo_root": self.repo_root,
            "project_root": self.project_root,
        }


class TargetResolver:
    """Locate package roots and template directories for scaffolding verbs."""

    def __init__(self, repo_root: Optional[Path] = None, package_root: Optional[Path] = None):
        current_file = Path(__file__).resolve()
        self.repo_root = Path(repo_root).resolve() if repo_root else current_file.parents[3]
        self.package_root = Path(package_root).resolve() if package_root else current_file.parents[1]
        self.package_templates = self.package_root / "templates"

        self._targets: Dict[str, Target] = self._discover_targets()
        self._aliases: Dict[str, str] = {
            "spec": "spec-core",
            "spec-dev": "spec-core",
            "spec_core": "spec-core",
            "spec-core": "spec-core",
        }
        self.default_target = "spec-core"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def parse_target_from_args(self, args: Iterable[str]) -> Tuple[Optional[str], List[str]]:
        """Extract the target selector from a verb argument list."""

        args = list(args)
        target: Optional[str] = None
        remaining: List[str] = []
        i = 0
        while i < len(args):
            token = args[i]
            if token == "--target" and i + 1 < len(args):
                target = args[i + 1]
                i += 2
                continue
            if token == "--self":
                target = target or self.default_target
                i += 1
                continue
            remaining.append(token)
            i += 1
        return target, remaining

    def get_target_root(self, target: Optional[str] = None) -> Path:
        """Return the filesystem root for the selected target package."""
        return self._resolve_target(target).root

    def get_templates_root(self, target: Optional[str] = None) -> Path:
        """Return the template directory root for a target."""
        return self._resolve_target(target).templates

    def get_target_info(self, target: Optional[str] = None) -> Dict[str, object]:
        """Return metadata describing the desired target."""
        return self._resolve_target(target).to_dict()

    def get_project_root(self, target: Optional[str] = None) -> Path:
        """Return the project root (directory containing pyproject) for a target."""
        return self._resolve_target(target).project_root

    def list_targets(self) -> List[str]:
        """Return a sorted list of known target identifiers."""
        return sorted(self._targets.keys())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_target(self, target: Optional[str]) -> Target:
        key = self._normalise_key(target)
        try:
            return self._targets[key]
        except KeyError as exc:
            available = ", ".join(sorted(self._targets)) or "<none>"
            raise ValueError(f"Unknown target '{target}'. Known targets: {available}") from exc

    def _normalise_key(self, target: Optional[str]) -> str:
        if not target:
            return self.default_target
        key = target.lower()
        return self._aliases.get(key, key)

    def _discover_targets(self) -> Dict[str, Target]:
        """Discover available targets within the repository."""
        targets: Dict[str, Target] = {}

        # spec-core (default) lives directly under src/spec
        spec_root = self.repo_root / "src" / "spec"
        targets["spec-core"] = Target(
            key="spec-core",
            package="spec-core",
            root=spec_root,
            templates=self.package_templates,
            repo_root=self.repo_root,
            project_root=self.repo_root,
        )

        # Legacy alias for backwards compatibility
        targets["spec-dev"] = Target(
            key="spec-dev",
            package="spec-core",
            root=spec_root,
            templates=self.package_templates,
            repo_root=self.repo_root,
            project_root=self.repo_root,
        )

        # Optional life-cli target if present in this checkout
        life_cli_src_root = self.repo_root / "life-cli" / "src"
        if life_cli_src_root.exists():
            package_dir = self._discover_first_package_dir(life_cli_src_root)
            templates_dir = self.repo_root / "scripts" / "life-cli" / "templates"
            if package_dir and templates_dir.exists():
                targets["life-cli"] = Target(
                    key="life-cli",
                    package="life-cli",
                    root=package_dir,
                    templates=templates_dir,
                    repo_root=self.repo_root,
                    project_root=life_cli_src_root.parent,
                )

        return targets

    @staticmethod
    def _discover_first_package_dir(src_root: Path) -> Optional[Path]:
        for candidate in src_root.iterdir():
            if candidate.is_dir() and not candidate.name.startswith("__"):
                return candidate
        return None
