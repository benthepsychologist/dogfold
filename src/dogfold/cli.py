#!/usr/bin/env python3
import os
import sys
import importlib.util
from pathlib import Path
import typer
from typing import Optional
import textwrap

try:  # Optional legacy collision warning (if abandoned 'spec' distribution is present)
    import importlib.metadata as _im
    if any(d.metadata['Name'].lower() == 'spec' and d.metadata['Name'] != 'spec-core' for d in _im.distributions()):
        import warnings as _warnings
        _warnings.warn("Another distribution named 'spec' detected; 'spec-core' is supplying the 'spec' CLI.")
except Exception:
    pass
app = typer.Typer(name="dog", help="Dogfold: Recursive meta-scaffolding for Python projects")

# Dynamically load domain command groups
def _load_domain_apps():
    """Load domain command groups from dogfold.domains"""
    domains_path = Path(__file__).parent / "domains"
    if not domains_path.exists():
        return
    
    for domain_dir in domains_path.iterdir():
        if not domain_dir.is_dir() or domain_dir.name.startswith('_'):
            continue
        
        commands_file = domain_dir / "commands.py"
        if commands_file.exists():
            try:
                # Import the domain's command app
                module_name = f"dogfold.domains.{domain_dir.name}.commands"
                module = importlib.util.spec_from_file_location(module_name, commands_file)
                if module and module.loader:
                    domain_module = importlib.util.module_from_spec(module)
                    module.loader.exec_module(domain_module)
                    
                    # Look for the domain app (conventionally named {domain}_app)
                    app_name = f"{domain_dir.name}_app"
                    if hasattr(domain_module, app_name):
                        domain_app = getattr(domain_module, app_name)
                        app.add_typer(domain_app, name=domain_dir.name)
            except Exception as e:
                print(f"Warning: Could not load domain '{domain_dir.name}': {e}")

# Load domains at startup
_load_domain_apps()


def main():
    """Entry point for dog command"""
    # Handle stdin for backward compatibility
    if len(sys.argv) == 1 and not sys.stdin.isatty():
        stdin_code = sys.stdin.read().strip()
        if stdin_code:
            return _exec_code(stdin_code)

    try:
        app()
    except SystemExit as e:
        return e.code
    return 0


class SpecCLI:
    def __init__(self):
        # No more sys.path manipulation - use clean package imports
        pass

    def _load_verbs(self):
        verbs = {}
        # Load verbs from dogfold.verbs package
        try:
            from dogfold import verbs as verbs_package
            verbs_dir = Path(verbs_package.__file__).parent
            if verbs_dir.exists():
                for verb_file in verbs_dir.glob("*.py"):
                    if verb_file.name == "__init__.py":
                        continue
                    verb_name = verb_file.stem
                    handler = self._load_handler(verb_file, f"{verb_name.title()}SpecVerb")
                    if handler:
                        verbs[verb_name] = handler
        except ImportError:
            # verbs package doesn't exist yet, that's fine
            pass
        return verbs

    def _load_handler(self, verb_file: Path, class_name: str):
        try:
            spec = importlib.util.spec_from_file_location(verb_file.stem, verb_file)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                # Handle classes that need constructor arguments
                if class_name in ['RegisterSpecVerb', 'DefineSpecVerb']:
                    return cls()  # These classes now handle their own TargetResolver
                else:
                    return cls()
        except Exception as e:
            print(f"Warning: Could not load dogfold verb '{verb_file}': {e}")
        return None

    def run_verb(self, verb_name: str, args: list[str]) -> int:
        """Run a registered verb with arguments"""
        verbs = self._load_verbs()
        if verb_name in verbs:
            try:
                return verbs[verb_name].execute(args)
            except Exception as e:
                print(f"Error executing dogfold {verb_name}: {e}")
                return 1
        return self._missing(verb_name)

    def exec_code(self, code: str) -> int:
        """Execute Python code"""
        try:
            exec(code, globals())
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def _missing(self, name: str) -> int:
        print(f"Error: dogfold verb '{name}' not available")
        return 1

    class _noop:
        def execute(self, args):
            return 1


def _exec_code(code: str) -> int:
    """Execute Python code (module-level function)"""
    cli = SpecCLI()
    return cli.exec_code(code)


# Create register subapp with proper subcommands
register_app = typer.Typer(help="Register resources")

@register_app.command("domain")
def register_domain(
    name: str = typer.Argument(..., help="Domain name"),
    target: str = typer.Option(None, "--target", help="Target package (dogfold, life-cli)"),
    self_target: bool = typer.Option(False, "--self", help="Target dogfold package")
):
    """Register a new domain"""
    # Build args list for the verb
    args = ["domain", name]
    if target:
        args.extend(["--target", target])
    if self_target:
        args.append("--self")
    
    cli = SpecCLI()
    result = cli.run_verb("register", args)
    if result != 0:
        raise typer.Exit(result)

@register_app.command("verb")
def register_verb(
    name: str = typer.Argument(..., help="Verb name (can include domain.verb)"),
    target: str = typer.Option(None, "--target", help="Target package (dogfold, life-cli)"),
    self_target: bool = typer.Option(False, "--self", help="Target dogfold package"),
    inline_code: str = typer.Option(None, "--code", help="Inline code for verb")
):
    """Register a new verb"""
    # Build args list for the verb
    args = ["verb", name]
    if target:
        args.extend(["--target", target])
    if self_target:
        args.append("--self")
    if inline_code:
        args.append(inline_code)
    
    cli = SpecCLI()
    result = cli.run_verb("register", args)
    if result != 0:
        raise typer.Exit(result)

@register_app.command("cli")
def register_cli(
    name: str = typer.Argument(..., help="CLI name"),
    target: str = typer.Option(None, "--target", help="Target package (dogfold, life-cli)"),
    self_target: bool = typer.Option(False, "--self", help="Target dogfold package")
):
    """Register a new CLI"""
    # Build args list for the verb
    args = ["cli", name]
    if target:
        args.extend(["--target", target])
    if self_target:
        args.append("--self")
    
    cli = SpecCLI()
    result = cli.run_verb("register", args)
    if result != 0:
        raise typer.Exit(result)

# Add the register subapp to main app
app.add_typer(register_app, name="register")


@app.command("define", context_settings={"allow_extra_args": True, "allow_interspersed_args": False})
def define_cmd(
    ctx: typer.Context,
    define_type: str = typer.Argument(help="Type to define (contract, class)")
):
    """Define a new component or structure"""
    # Pass all arguments directly to the define verb
    args = [define_type] + ctx.args

    cli = SpecCLI()
    result = cli.run_verb("define", args)
    if result != 0:
        raise typer.Exit(result)


@app.command(context_settings={"allow_extra_args": True, "allow_interspersed_args": False})
def execute(
    ctx: typer.Context,
    code: str = typer.Argument(help="Python code to execute")
):
    """Execute Python code directly"""
    # Handle case where code and extra args should be joined
    full_code = code
    if ctx.args:
        full_code = " ".join([code] + ctx.args)
    
    result = _exec_code(full_code)
    if result != 0:
        raise typer.Exit(result)


@app.callback()
def main_callback(ctx: typer.Context):
    """Dogfold: Recursive meta-scaffolding for Python projects"""
    # This callback only handles setup - no argument processing
    # Arguments are handled by individual commands
    pass


# -----------------------------
# Scaffolding (dog init)
# -----------------------------

@app.command("init")
def init_command(
    name: str = typer.Argument(..., help="New tool / package name (kebab or snake)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files if present"),
):
    """Scaffold a minimal dogfold-powered CLI project."""
    root = Path(name)
    pkg = name.replace('-', '_')
    src_pkg = root / "src" / pkg
    files = {
        root / "README.md": f"# {name}\n\nGenerated with dogfold.\n",
        root / "pyproject.toml": textwrap.dedent(f"""
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "{name} CLI (scaffolded by dogfold)"
readme = "README.md"
license = {{text = "MIT"}}
requires-python = ">=3.11"
dependencies = ["dogfold>=0.1.0,<0.2.0", "typer>=0.12.0"]

[project.scripts]
{name.split('-')[0]} = "{pkg}.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["{pkg}*"]
"""),
        root / "Makefile": textwrap.dedent("""
dev: ## install editable
	pip install -e .

build: ## placeholder build/regeneration hook
	@echo "(Add dog build verbs when implemented)"
"""),
        src_pkg / "__init__.py": f"# {pkg} package\n",
        src_pkg / "cli.py": textwrap.dedent(f"""
import typer
app = typer.Typer(help=\"{name} CLI\")

@app.command()
def hello():
    \"\"\"Example command.\"\"\"
    typer.echo(\"Hello from {name}!\")

def main():
    app()

if __name__ == '__main__':
    main()
"""),
    }

    # Create directories
    if not src_pkg.exists():
        src_pkg.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []
    for path, content in files.items():
        if path.exists() and not force:
            skipped.append(path)
            continue
        path.write_text(content)
        created.append(path)

    if created:
        typer.echo("Created:")
        for p in created:
            typer.echo(f"  - {p}")
    if skipped:
        typer.echo("Skipped (exists, use --force to overwrite):")
        for p in skipped:
            typer.echo(f"  - {p}")
    typer.echo("Done.")


if __name__ == "__main__":
    exit(main())