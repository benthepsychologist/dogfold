#!/usr/bin/env python3
"""
DefineClass - Creates class files from inline code or templates
"""
import re
from pathlib import Path
from typing import Optional


class DefineClass:
  """Handler for defining new classes"""

  def __init__(self, target_resolver=None, explicit_target: Optional[str] = None):
    if target_resolver is None:
      # Fallback for backward compatibility
      from dogfold.kernel.target_resolver import TargetResolver
      target_resolver = TargetResolver()
    
    self.resolver = target_resolver
    self.explicit_target = explicit_target
    self.repo_root = target_resolver.repo_root

  def execute(self, args):
    """
    Usage:
      spec define class <ClassName> [--domain <name>] [<inline code>]
    If inline code is provided, write it verbatim.
    Otherwise, use a class-specific template if available, else a generic class template.
    """
    if not args:
      return "Usage: spec define class <ClassName> [<inline code>]"

    # Support optional domain prefix: --domain <name>
    class_name = args[0]
    inline_code = ""
    domain_name = None
    if len(args) > 1:
      if args[1] == "--domain" and len(args) > 2:
        domain_name = args[2]
        inline_code = args[3] if len(args) > 3 else ""
      else:
        inline_code = args[1]

    # Get target package root
    target_root = self.resolver.get_target_root(self.explicit_target)
    target_info = self.resolver.get_target_info(self.explicit_target)
    
    snake = self._to_snake(class_name)
    if domain_name:
      target_file = target_root / "domains" / domain_name / "classes" / f"{snake}.py"
      target_file.parent.mkdir(parents=True, exist_ok=True)
    else:
      target_file = target_root / f"{snake}.py"

    if target_file.exists():
      return f"⚠️  Class '{class_name}' already exists, not overwriting: {target_file}"

    if inline_code:
      content = inline_code
    else:
      target_templates = self.resolver.get_templates_root(self.explicit_target)
      generic_template = target_templates / "class_template.py"

      if domain_name:
        specific_template = target_templates / "domains" / domain_name / "classes" / f"{snake}.py"
      else:
        specific_template = target_templates / "classes" / f"{snake}.py"

      template_path = specific_template if specific_template.exists() else generic_template
      if not template_path.exists():
        return f"❌ Template file not found: {template_path}"
      content = template_path.read_text()
      content = content.replace("{CLASS_NAME}", class_name)

    target_file.write_text(content if content.endswith("\n") else content + "\n")
    return f"✅ Defined class '{class_name}' in {target_info['package']} -> {target_file}"

  def _to_snake(self, name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()
