#!/usr/bin/env python3
"""
RegisterVerb - Creates new verb files from templates
"""
import os
from pathlib import Path
from typing import Optional

class RegisterVerb:
    """Handler for registering new verbs"""
    
    def __init__(self, target_resolver=None, explicit_target: Optional[str] = None):
        if target_resolver is None:
            # Fallback for backward compatibility
            from dogfold.kernel.target_resolver import TargetResolver
            target_resolver = TargetResolver()
        
        self.resolver = target_resolver
        self.explicit_target = explicit_target
        self.repo_root = target_resolver.repo_root
    
    def execute(self, args):
        """Register a new verb

        Usage:
          spec register verb <verb_name>|<domain.verb> [<inline code>]
        If inline code is provided, show a warning and ignore for now.
        For domain verbs, write to src/domains/<domain>/verbs/<verb>.py using
        a domain-specific template if available; otherwise fall back to the
        generic template.
        """
        if not args:
            return "Usage: spec register verb <verb_name> [<inline code>]"

        full_name = args[0]
        inline_code = args[1] if len(args) > 1 else ""

        domain_name = None
        verb_name = full_name
        if "." in full_name:
            parts = full_name.split(".", 1)
            if len(parts) != 2 or not parts[0] or not parts[1]:
                return f"❌ Invalid domain.verb name: {full_name}"
            domain_name, verb_name = parts[0], parts[1]

        # Get target package root
        target_root = self.resolver.get_target_root(self.explicit_target)
        target_info = self.resolver.get_target_info(self.explicit_target)
        
        # Ensure target directory exists
        if domain_name:
            target_dir = target_root / "domains" / domain_name / "verbs"
        else:
            target_dir = target_root / "verbs"
        target_dir.mkdir(parents=True, exist_ok=True)
        init_file = target_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")

        # Get target-specific template paths
        target_info = self.resolver.get_target_info(self.explicit_target)
        templates_root = self.resolver.get_templates_root(self.explicit_target)

        # Prefer verb-specific template (domain-aware) if present
        if domain_name:
            specific_template = templates_root / "domains" / domain_name / "verbs" / f"{verb_name}.py"
        else:
            specific_template = templates_root / "verbs" / f"{verb_name}.py"

        # Fallback to generic template for target
        generic_template = templates_root / "verbs" / "verb_template.py"

        template_path = specific_template if specific_template.exists() else generic_template

        if not template_path.exists():
            return f"❌ Template file not found: {template_path}"

        with open(template_path, "r") as f:
            template_content = f.read()

        # Inline injection not supported yet (ignored)
        # Replace placeholders for class and verb name
        verb_content = template_content.replace("{VERB_NAME}", verb_name)
        verb_content = verb_content.replace("VerbNameVerb", f"{verb_name.title()}Verb")

        # Write verb file (skip if exists)
        verb_file = target_dir / f"{verb_name}.py"
        if verb_file.exists():
            if domain_name:
                return f"⚠️  Verb '{domain_name}.{verb_name}' already exists, not overwriting: {verb_file}"
            return f"⚠️  Verb '{verb_name}' already exists, not overwriting: {verb_file}"
        with open(verb_file, "w") as f:
            f.write(verb_content)

        if domain_name:
            return f"✅ Registered verb '{domain_name}.{verb_name}' in {target_info['package']} -> {verb_file}"
        return f"✅ Registered verb '{verb_name}' in {target_info['package']} -> {verb_file}"

    def _inject_inline_into_execute(self, content: str, indented_block: str) -> str:
        """Insert inline code as the body of execute, replacing the default body."""
        lines = content.splitlines()
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            out.append(line)
            if line.strip().startswith("def execute(self, args):"):
                # Consume any following docstring line(s)
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('"""'):
                    out.append(lines[j])
                    j += 1
                # Skip any existing simple body (e.g., print(...) and return 0)
                # Insert our block instead
                out.append(indented_block.rstrip("\n"))
                # Now skip until we see a line that is less-indented or class end
                # For simplicity, stop skipping after we've consumed at most 3 lines
                i = j
                # Try to skip up to two lines of existing simple body
                skip_count = 0
                while i < len(lines) and skip_count < 3 and lines[i].startswith("        "):
                    i += 1
                    skip_count += 1
                continue
            i += 1
        return "\n".join(out)
