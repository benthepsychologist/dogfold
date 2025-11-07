# Dogfold

**Recursive meta-scaffolding for Python projects**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is Dogfold?

**Dogfold** is a self-building Python scaffolding tool that generates project structures from templates—including its own code.

Think of it as **cookiecutter that can regenerate itself**: templates are the source of truth, and the tool continuously evolves by rebuilding from those templates.

> **Part of the tool family:** [Specwright](https://github.com/yourusername/specwright) defines governance, **Dogfold** builds projects, [Gorch](https://github.com/yourusername/gorch) orchestrates infrastructure.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dogfold.git
cd dogfold

# Install in development mode
pip install -e .

# Verify installation
dog --help
```

### Scaffold Your First Project

```bash
# Create a new Python CLI project
dog init my-tool

# Navigate to the new project
cd my-tool

# Install and test
pip install -e .
my-tool --help
```

---

## Core Concepts

### Self-Building Meta-Scaffolder

Dogfold has three layers that work together:

1. **`kernel/`** - Hand-written primitives (stable foundation)
2. **`templates/`** - Jinja2 templates (source of truth)
3. **`manual/`** - Generated code (shrinking toward 0%)

The goal: **Everything becomes templated.** `manual/` disappears as patterns migrate to `templates/`.

### "Push to the Left" Philosophy

Code evolves from raw execution toward built-in primitives:

```
CODE → FLAGS → PROFILES → COMPOUNDS → DOMAIN VERBS → KERNEL VERBS
```

Start with working code, promote patterns leftward as they prove valuable.

### Horizontal (Command Syntax)

```bash
# Stage 1: Raw CODE (rightmost)
dog 'print("Hello World")'

# Stage 2: FLAGS
dog --debug 'print("Hello World")'

# Stage 3: PROFILES (future)
dog --profile=dev 'print("Hello World")'

# Stage 4: COMPOUNDS (future)
dog scaffold project --profile=dev

# Stage 5: Domain VERBS
dog scaffold cli

# Stage 6: KERNEL (leftmost)
dog init my-tool
```

### Vertical (Across Layers)

```
manual/ → templates/ → kernel/
(generated) → (templates) → (hand-written, stable)
```

**The endgame:** `manual/` shrinks to zero as everything moves to `templates/` or `kernel/`.

---

## CLI Commands

### `dog init`

Scaffold a new Python CLI project from templates.

```bash
dog init my-tool

# Creates:
# my-tool/
# ├── src/my_tool/
# │   ├── __init__.py
# │   └── cli.py
# ├── pyproject.toml
# ├── README.md
# └── Makefile
```

**Generated projects are standalone** - no dogfold runtime dependency required.

### `dog define`

Define new classes with registries.

```bash
# Define a new class type
dog define ClassName

# With version
dog define ClassName --version 1.0.0

# Target a specific package
dog define ClassName --target my-package
```

### `dog register`

Register new resources (domains, verbs, CLIs).

```bash
# Register a new domain
dog register domain tools

# Register a new verb
dog register verb scaffold

# Register a new CLI
dog register cli my-tool
```

### `dog execute`

Execute Python code directly (for rapid prototyping).

```bash
dog execute 'print("Hello from dogfold!")'

# Or via stdin
echo 'print("Testing")' | dog
```

---

## Architecture

### Three-Layer System

#### 1. Kernel Layer (`src/spec/kernel/`)

Hand-written primitives that form the stable foundation:

- **Characteristics:**
  - Hand-coded, not generated
  - Stable, rarely changes
  - No domain knowledge
  - Pure utilities

**Status:** ~80% complete

#### 2. Templates Layer (`src/spec/templates/`)

Jinja2 templates that generate code:

```
templates/
├── verbs/           # Verb implementation templates
├── clis/            # CLI command templates
└── class_template.py # Domain object templates
```

- **Characteristics:**
  - Jinja2 templates
  - Generate domain code
  - Self-documenting
  - Versioned

**Status:** ~40% complete

#### 3. Manual Layer (`src/spec/manual/` - not yet created)

Generated code that hasn't been templated yet:

- **Characteristics:**
  - Temporary
  - Being migrated to templates
  - **Target: 0%**

**Status:** ~20% complete, **shrinking to 0%**

---

## Design Principles

1. **Think in Verbs** – Every feature starts as a command.
2. **Plan Forward, Work Backward** – Design the command you want, then build toward it.
3. **Don't Build Until You Need It** – Start with working code, promote patterns when they repeat.
4. **Structure Suggests Itself** – Let patterns emerge from usage, don't impose architecture.
5. **The Design Teaches Itself** – System reveals its own optimal form through usage.
6. **Build-Time DSL** – dogfold is like a compiler, not a runtime dependency.

**See [docs/architecture.md](docs/architecture.md) for detailed principles.**

---

## Project Structure

```
dogfold/
├── docs/                      # Documentation
│   └── architecture.md        # System design & principles
├── src/spec/                  # dogfold package
│   ├── kernel/                # Hand-written primitives (DO edit)
│   │   └── target_resolver.py
│   ├── templates/             # Templates (DO edit)
│   │   ├── verbs/
│   │   ├── clis/
│   │   └── class_template.py
│   ├── bootstrap/             # Self-build logic
│   ├── verbs/                 # Core verbs (define, register)
│   └── cli.py                 # Entry point
├── pyproject.toml             # Package definition
└── README.md                  # This file
```

---

## How It Works (Self-Building)

1. **Dogfold has a kernel**: Hand-written primitives (Entity, Verb, Handler)
2. **Dogfold has templates**: `templates/` contains Jinja2 templates
3. **Dogfold generates code**: Bootstrap regenerates from templates
4. **Dogfold scaffolds tools**: `dog init <name>` creates new CLI projects
5. **Generated CLIs are standalone**: No dogfold runtime dependency

**Templates are the source of truth. Generated code is output.**

---

## Integration with Specwright

Dogfold is called by [Specwright](https://github.com/yourusername/specwright) when implementing AIPs (Agentic Implementation Plans) that require Python scaffolding:

```yaml
# In a Specwright AIP:
steps:
  - role: agent
    prompt: "Scaffold new Python microservice"
    commands:
      - dog init user-service
      - dog register domain auth
```

**Separation of concerns:**
- **Specwright** (`spec`): Defines governance, validates plans, orchestrates execution
- **Dogfold** (`dog`): Scaffolds Python projects, generates code from templates
- **Gorch** (`gorch`): Orchestrates Google Cloud infrastructure (future)

---

## The Game Plan

### Today's Reality

```
kernel/     ████████████████░░░░  80% complete (hand-written)
templates/  ████████░░░░░░░░░░░░  40% complete (Jinja2)
manual/     ████░░░░░░░░░░░░░░░░  20% complete (generated, shrinking)
```

### Goal State

```
kernel/     ████████████████████  100% stable (minimal growth)
templates/  ████████████████████  100% complete (all patterns templated)
manual/     ░░░░░░░░░░░░░░░░░░░░  0% (everything moved to templates)
```

**The endgame:** `manual/` disappears as everything becomes templated or moves to `kernel/`.

---

## For AI Assistants / New Sessions

- **Dogfold is a meta-scaffolder** - builds Python CLIs including itself
- **CLI command: `dog`** (not `spec`, which is Specwright)
- **kernel/ is hand-written** - DO edit this
- **templates/ are source of truth** - DO edit this
- **manual/ is generated** - DO NOT edit this (target: eliminate entirely)
- **Bootstrap = regenerate** - not "build from nothing"
- Use `dog init <tool>` to scaffold new Python CLI projects
- Generated CLIs have no dogfold runtime dependency

---

## Common Tasks

- **Scaffold a Python CLI**: `dog init my-tool`
- **Add a verb**: Create template, run `dog register verb <name>`
- **Test changes**: `pip install -e .` then `dog --help`
- **Understand flow**: Templates → dog commands → generated Python

---

## Roadmap

- [ ] Complete kernel primitives (reach 100%)
- [ ] Migrate all manual patterns to templates
- [ ] Template overlay resolution (project-specific overrides)
- [ ] Registry-driven domain generation
- [ ] Full bootstrap self-regeneration
- [ ] Multi-language template support (beyond Python)
- [ ] Publish to PyPI as `dogfold`

---

## Contributing

Contributions welcome! Please:

1. Check [open issues](https://github.com/yourusername/dogfold/issues)
2. Submit PRs against `main` branch
3. Ensure tests pass: `pytest tests/` (when tests exist)
4. Follow the three-layer architecture

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/dogfold/issues)
- **Documentation:** [docs/](docs/)

---

**Dogfold: Self-building scaffolding for the meta-engineering era** 🐕

_Part of the tool family: Specwright defines. Dogfold builds. Gorch orchestrates._
