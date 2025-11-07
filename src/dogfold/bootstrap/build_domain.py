#!/usr/bin/env python3
"""BuildDomain bootstrap utility - create domains from package templates."""
import shutil
from pathlib import Path

from dogfold.kernel.target_resolver import TargetResolver


class BuildDomain:
    """Bootstrap utility to build domains from templates"""

    def __init__(self, target_resolver: TargetResolver | None = None):
        self.resolver = target_resolver or TargetResolver()

    def build_domain(self, domain_name: str, target_package: str | None = None):
        """Build a domain from templates

        Args:
            domain_name: Name of domain to build (version, package, docs, etc)
            target_package: Target package (spec-core or life-cli)

        Returns:
            int: 0 for success, 1 for error
        """
        try:
            target_key = target_package
            target_info = self.resolver.get_target_info(target_key)
            target_root = Path(target_info["root"])
            templates_root = self.resolver.get_templates_root(target_key) / "domains"
            templates_dir = templates_root / domain_name

            if not templates_dir.exists():
                print(f"❌ Templates not found for domain '{domain_name}': {templates_dir}")
                return 1

            # Target directories
            if not target_root.exists():
                target_root.mkdir(parents=True, exist_ok=True)
            domain_dir = target_root / "domains" / domain_name

            print(f"🏗️  Building domain '{domain_name}' for {target_info['package']} from templates...")
            print(f"📂 Source: {templates_dir}")
            print(f"📂 Target: {domain_dir}")

            # Ensure target domain directory exists
            domain_dir.mkdir(parents=True, exist_ok=True)

            # Copy all template files recursively
            files_copied = 0
            for item in templates_dir.rglob("*"):
                if item.is_file():
                    # Calculate relative path within templates
                    rel_path = item.relative_to(templates_dir)

                    # Handle special cases
                    if rel_path.parts[0] == "schemas":
                        # JSON schemas go to separate schemas directory
                        schemas_target = target_root / "schemas" / domain_name
                        schemas_target.mkdir(parents=True, exist_ok=True)
                        schema_file = schemas_target / rel_path.name
                        shutil.copy2(item, schema_file)
                        print(f"📋 Schema: {rel_path} -> schemas/{domain_name}/{rel_path.name}")
                    else:
                        # Regular files go to domain structure
                        target_file = domain_dir / rel_path

                        # Ensure parent directories exist
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_file)
                        print(f"📋 File: {rel_path}")

                    files_copied += 1

            # Ensure __init__.py files exist where needed
            for subdir in ["classes", "verbs"]:
                init_file = domain_dir / subdir / "__init__.py"
                if not init_file.exists() and (domain_dir / subdir).exists():
                    init_file.touch()
                    print(f"📋 Created: {subdir}/__init__.py")

            print(f"✅ Built domain '{domain_name}' in {target_info['package']}: {files_copied} files copied")
            return 0

        except Exception as e:
            print(f"❌ Error building domain '{domain_name}': {e}")
            return 1