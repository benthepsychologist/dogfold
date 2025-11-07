#!/usr/bin/env python3
"""
RegisterSpecVerb - Register resources (domain, cli, verb)
"""
import sys
from pathlib import Path
from dogfold.kernel.target_resolver import TargetResolver


class RegisterSpecVerb:
  def __init__(self):
    self.resolver = TargetResolver()
  
  def execute(self, args):
    if not args:
      print("Usage: spec register <domain|cli|verb> [--target <package>] [--self] ...")
      return 1

    resource = args[0]
    rest = args[1:]
    
    try:
      if resource == "domain":
        return self._register_domain(rest)
      if resource == "cli":
        return self._register_cli(rest)
      if resource == "verb":
        return self._register_verb(rest)
      print("Usage: spec register <domain|cli|verb> [--target <package>] [--self] ...")
      return 1
    except ValueError as e:
      print(str(e))
      return 1

  def _register_domain(self, args):
    # Parse target flags
    target, remaining_args = self.resolver.parse_target_from_args(args)
    
    if not remaining_args:
      print("Usage: spec register domain <name> [--target <package>] [--self]")
      return 1
      
    name = remaining_args[0]
    
    # Get target package root
    target_root = self.resolver.get_target_root(target)
    target_info = self.resolver.get_target_info(target)
    
    # Create /domains directory if it doesn't exist (first domain)
    domains_root = target_root / "domains"
    if not domains_root.exists():
      domains_root.mkdir(parents=True, exist_ok=True)
      package_name = target_info['package'].replace('-', '_')
      (domains_root / "__init__.py").write_text(f"# {package_name} domains")
      
    domain_root = domains_root / name
    classes_dir = domain_root / "classes"
    verbs_dir = domain_root / "verbs"
    classes_dir.mkdir(parents=True, exist_ok=True)
    verbs_dir.mkdir(parents=True, exist_ok=True)
    (domain_root / "__init__.py").write_text("") if not (domain_root / "__init__.py").exists() else None
    (classes_dir / "__init__.py").write_text("") if not (classes_dir / "__init__.py").exists() else None
    (verbs_dir / "__init__.py").write_text("") if not (verbs_dir / "__init__.py").exists() else None
    
    # Create commands.py file for Typer integration
    commands_file = domain_root / "commands.py"
    if not commands_file.exists():
      templates_root = self.resolver.get_templates_root(target)
      template_file = templates_root / "domain_commands_template.py"
      if template_file.exists():
        template_content = template_file.read_text()
        commands_content = template_content.replace("{DOMAIN_NAME}", name)
        commands_file.write_text(commands_content)
      else:
        # Fallback if template doesn't exist
        commands_content = f'''#!/usr/bin/env python3
"""
{name} domain commands for spec CLI
"""
import typer

# Create {name} command group  
{name}_app = typer.Typer(name="{name}", help="{name} management commands")

# Domain commands will be added here as verbs are registered
'''
        commands_file.write_text(commands_content)
    
    print(f"✅ Registered domain '{name}' in {target_info['package']} -> {domain_root}")
    return 0

  def _register_cli(self, args):
    # Parse target flags
    target, remaining_args = self.resolver.parse_target_from_args(args)
    
    if not remaining_args:
      print("Usage: spec register cli <name> [--target <package>] [--self]")
      return 1
      
    cli_name = remaining_args[0]
    target_info = self.resolver.get_target_info(target)
    
    # Map CLI names to template files
    cli_templates = {
      'life': 'life_cli_template.py',
      'spec': 'spec_cli_template.py'
    }
    
    if cli_name not in cli_templates:
      print(f"❌ Unknown CLI '{cli_name}'. Supported: {list(cli_templates.keys())}")
      return 1
      
    # Find template and target files
    templates_root = self.resolver.get_templates_root(target)
    template_file = templates_root / "clis" / cli_templates[cli_name]
    target_file = target_info['root'] / "cli.py"
    
    if not template_file.exists():
      print(f"❌ CLI template not found: {template_file}")
      return 1
    
    if target_file.exists():
      print(f"⚠️  CLI '{cli_name}' already exists in {target_info['package']}, not overwriting: {target_file}")
      return 0
      
    # Copy template to target
    target_file.write_text(template_file.read_text())
    print(f"✅ Registered CLI '{cli_name}' in {target_info['package']} -> {target_file}")
    return 0

  def _register_verb(self, args):
    # Parse target flags
    target, remaining_args = self.resolver.parse_target_from_args(args)
    
    if not remaining_args:
      print("Usage: spec register verb <name>|<domain.verb> [--target <package>] [--self] [<inline code>]")
      return 1
      
    try:
      from dogfold.bootstrap.register_verb import RegisterVerb
      handler = RegisterVerb(target_resolver=self.resolver, explicit_target=target)
      result = handler.execute(remaining_args)
      print(result)
      return 0 if result.startswith("✅") or result.startswith("⚠️") else 1
    except Exception as e:
      print(f"Error: {e}")
      return 1


