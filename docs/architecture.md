# Architecture

Dogfold's three-layer architecture and design principles.

## Core Principle: Push to the Left

Code evolves from raw execution toward built-in primitives:

```
CODE → FLAGS → PROFILES → COMPOUNDS → DOMAIN VERBS → KERNEL VERBS
```

This isn't just organization - it's a philosophy. Start with working code, promote patterns as they prove valuable.

## Three-Layer Architecture

### Kernel Layer (`kernel/`)

Hand-written primitives that form the foundation:

```
kernel/
├── target_resolver.py    # Package resolution logic
└── (future expansion)
```

**Characteristics:**
- Hand-coded, not generated
- Stable, rarely changes
- No domain knowledge
- Pure utilities

**Status**: ~80% complete

### Templates Layer (`templates/`)

Code generation templates:

```
templates/
├── verbs/              # Verb implementation templates
│   ├── define.py
│   ├── register.py
│   └── verb_template.py
├── clis/               # CLI command templates
└── class_template.py   # Domain object templates
```

**Characteristics:**
- Jinja2 templates (or Python templates)
- Generate domain code
- Self-documenting
- Versioned

**Status**: ~40% complete

### Manual Layer (`manual/`)

Generated code that hasn't been templated yet:

```
manual/
├── domains/         # Domain implementations (future)
└── utils/          # Utility functions (future)
```

**Characteristics:**
- Temporary
- Being migrated to templates
- Should shrink to 0%

**Status**: ~20% complete, **target: 0%**

## Class-Led Design

Rich domain objects with behavior, not anemic data structures:

```python
# Good: Rich domain object
class ProjectScaffold:
    def __init__(self, name: str, template: str):
        self.name = name
        self.template = template

    def generate_structure(self) -> dict:
        # Domain logic here
        pass

    def validate(self) -> ValidationResult:
        # Validation logic here
        pass

# Avoid: Anemic dict passing
def generate_scaffold(config_dict: dict) -> dict:
    # All logic in functions
    pass
```

## Data Flow

### Template → Code

```
Template + Context → Render → Code Generation → File Write
```

Example:
```
verb_template.py + {name: "scaffold", domain: "tools"} → scaffold.py
```

## The Promotion Chain

Code naturally promotes leftward through stages:

### Verb Scaffolding Layers

1. **CODE** (Raw Intent)
   ```bash
   dog 'print("Hello World")'
   ```

2. **FLAGS** (Promoted Patterns)
   ```bash
   dog --debug 'print("Hello World")'
   ```

3. **PROFILES** (Behavior Postures - future)
   ```bash
   dog --profile=production 'ProjectScaffold.create("my-app")'
   # Implies: --validate --audit --no-debug
   ```

4. **COMPOUNDS** (Composed Sequences - future)
   ```bash
   dog scaffold full-stack --profile=production
   # Runs: create + configure + register
   ```

5. **DOMAIN VERBS** (Organized Capabilities)
   ```bash
   dog register verb scaffold
   # Register a new verb in the system
   ```

6. **KERNEL VERBS** (Essential Operations)
   ```bash
   dog init my-tool
   # So common it's built into kernel
   ```

Each step reduces cognitive load and pushes patterns leftward in the command syntax.

**Also see the vertical push:** `manual/ → templates/ → kernel/`

## Extension vs Plugin Architecture (Future)

### The Key Distinction

**Extensions modify the SUBSTRATE** (what all code sees)
**Plugins provide the SURFACE** (what users interact with)

### Extensions (Down & In)

Extensions change the kernel baseline that everyone inherits:

```python
class TelemetryExtension(Extension):
    def apply_to_kernel(self, kernel):
        # Wrap ALL verb execution
        # Now every verb gets telemetry
```

Examples:
- Policy planes (audit, compliance)
- Capability packs (storage, messaging)
- Global guarantees (idempotency, validation)

### Plugins (Down & Out)

Plugins add domain behaviors without affecting peers:

```python
class ToolsPlugin(Plugin):
    def register_verbs(self):
        return {
            'tool.install': InstallVerb,
            'tool.configure': ConfigureVerb
        }
```

Examples:
- Domain verbs (tool.*, data.*, deploy.*)
- Business workflows
- Integration adapters

### Thinning vs Expanding

**Thinning** (Pull Common Patterns Up):
```
Multiple plugins implement retry logic
→ Create RetryExtension
→ All plugins inherit retry capability
→ Plugin code gets thinner
```

**Expanding** (Push Guarantees Down):
```
Need audit trails everywhere
→ Add AuditExtension
→ All verbs automatically audited
→ Plugins don't implement audit
```

## Implementation Patterns

### Handlers & Templates Everywhere

Wherever there are verbs, you have:
- **Template**: Source of truth for implementation
- **Handler**: Generated imperative implementation

This applies at every level:
- Kernel verbs (init, define, register)
- Plugin verbs (tool.install, data.store - future)
- Domain verbs (project.scaffold - future)

## Error Handling

Structured error hierarchy:

```python
DogfoldError              # Base
├── ValidationError       # Invalid input
├── GenerationError       # Generation failed
├── FileSystemError       # I/O problems
└── TemplateError        # Template rendering issues
```

All errors include context for debugging.

## Testing Strategy

1. **Kernel Tests**: Unit tests for primitives
2. **Template Tests**: Validate template rendering
3. **Verb Tests**: Test verb logic
4. **Integration Tests**: End-to-end workflows
5. **Scaffold Tests**: Verify generated projects

## Future Architecture

As the system matures:

1. **Manual → 0%**: All code templated
2. **Contract-driven**: Kernel verbs define contracts, domains implement
3. **Plugin system**: External domains without core changes
4. **Multi-language**: Templates for languages beyond Python
5. **Self-regeneration**: Dogfold rebuilds itself from templates

## Design Principles

1. **Think in Verbs**: Every feature starts as a command
2. **Plan Forward, Work Backward**: Design the command you want, then build toward it
3. **Don't Build Until You Need It**: Start with working code, promote patterns when they repeat
4. **Structure Suggests Itself**: Let patterns emerge from usage, don't impose architecture
5. **The Design Teaches Itself**: System reveals its own optimal form through usage
6. **Build-Time DSL**: dogfold is like a compiler, not a runtime dependency
7. **Progressive Enhancement**: Push useful patterns left

## Summary

Dogfold grows from a single command (`dog {code}`) into a full meta-scaffolding system by:

1. **Following user intent** (think in verbs)
2. **Working backward** from desired commands
3. **Letting structure emerge** from patterns
4. **Continuously thinning** the core

The architecture naturally evolves through the promotion chain, keeping complexity at the edges while the kernel remains minimal.

Remember: **The system builds itself, documents itself, and suggests its own improvements.**

---

## Context: Relationship to Specwright

While Dogfold focuses on Python project scaffolding, it works alongside [Specwright](https://github.com/yourusername/specwright) in a complementary way:

- **Specwright** (`spec`): Defines AIPs (Agentic Implementation Plans), enforces governance, orchestrates workflows
- **Dogfold** (`dog`): Scaffolds Python projects, generates code from templates
- **Integration**: Specwright AIPs can call `dog` commands to scaffold projects during implementation

This separation keeps concerns clean: governance in Specwright, scaffolding in Dogfold.
