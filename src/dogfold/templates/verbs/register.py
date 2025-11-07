#!/usr/bin/env python3
"""
RegisterSpecVerb - Register resources (domain, cli, verb)
"""
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class RegisterSpecVerb:
  def execute(self, args):
    if not args:
      print("Usage: spec register <domain|cli|verb> ...")
      return 1

    resource = args[0]
    rest = args[1:]
    if resource == "domain":
      return self._register_domain(rest)
    if resource == "cli":
      return self._register_cli(rest)
    if resource == "verb":
      return self._register_verb(rest)
    print("Usage: spec register <domain|cli|verb> ...")
    return 1

  def _register_domain(self, args):
    if not args:
      print("Usage: spec register domain <name>")
      return 1
    name = args[0]
    domain_root = PROJECT_ROOT / "src" / "domains" / name
    classes_dir = domain_root / "classes"
    verbs_dir = domain_root / "verbs"
    classes_dir.mkdir(parents=True, exist_ok=True)
    verbs_dir.mkdir(parents=True, exist_ok=True)
    (domain_root / "__init__.py").write_text("") if not (domain_root / "__init__.py").exists() else None
    (classes_dir / "__init__.py").write_text("") if not (classes_dir / "__init__.py").exists() else None
    (verbs_dir / "__init__.py").write_text("") if not (verbs_dir / "__init__.py").exists() else None
    print(f"✅ Registered domain '{name}' -> {domain_root}")
    return 0

  def _register_cli(self, args):
    if not args:
      print("Usage: spec register cli <org|spec>")
      return 1
    cli = args[0]
    # CLIs are seeded from templates in setup; warn for now
    print("⚠️  Not able to inject code yet; using template (no-op).")
    return 0

  def _register_verb(self, args):
    if not args:
      print("Usage: spec register verb <name>|<domain.verb> [<inline code>]")
      return 1
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
      from src.register_verb import RegisterVerb
      handler = RegisterVerb()
      result = handler.execute(args)
      print(result)
      return 0 if result.startswith("✅") or result.startswith("⚠️") else 1
    except Exception as e:
      print(f"Error: {e}")
      return 1


