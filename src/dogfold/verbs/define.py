#!/usr/bin/env python3
"""
DefineSpecVerb - Define new classes with registries
"""
import json
import yaml
from pathlib import Path
from datetime import datetime
from dogfold.kernel.target_resolver import TargetResolver


class DefineSpecVerb:
    """Define classes of any name with their registries"""

    def __init__(self):
        self.resolver = TargetResolver()

    def execute(self, args):
        """Execute define command

        Usage:
            spec define <ClassName> [--target <package>] [--self] [--version x.y.z] [--reverse]
        """
        if not args:
            print("Usage: spec define <ClassName> [--target <package>] [--self] [--version x.y.z] [--reverse]")
            return 1

        class_name = args[0]

        # Parse arguments
        target, version, reverse = self._parse_args(args[1:])

        try:
            # Resolve target paths
            target_info = self.resolver.get_target_info(target)
            target_root = target_info['root']

            # Convert ClassName to snake_case for directory
            dir_name = self._to_snake_case(class_name)
            class_dir = target_root / dir_name

            # Handle reverse operation
            if reverse:
                return self._reverse_class(class_dir, class_name, target_info)

            # Create class directory and files
            return self._create_class(class_dir, class_name, version, target_info)

        except Exception as e:
            print(f"❌ Error defining class: {str(e)}")
            return 1

    def _parse_args(self, args):
        """Parse arguments"""
        target = None
        version = "1.0.0"
        reverse = False

        i = 0
        while i < len(args):
            if args[i] == '--target' and i + 1 < len(args):
                target = args[i + 1]
                i += 2
            elif args[i] == '--self':
                target = 'spec-core'
                i += 1
            elif args[i] == '--version' and i + 1 < len(args):
                version = args[i + 1]
                i += 2
            elif args[i] == '--reverse':
                reverse = True
                i += 1
            else:
                i += 1

        return target, version, reverse

    def _reverse_class(self, class_dir, class_name, target_info):
        """Remove class directory and all files"""
        try:
            if not class_dir.exists():
                print(f"⚠️  Class directory does not exist: {class_dir}")
                return 0

            # Remove the entire class directory
            import shutil
            shutil.rmtree(class_dir)

            print(f"✅ Removed {class_name} from {target_info['package']} -> {class_dir}")
            return 0

        except Exception as e:
            print(f"❌ Error removing class: {str(e)}")
            return 1

    def _create_class(self, class_dir, class_name, version, target_info):
        """Create class directory and files"""
        try:
            # Create class directory
            class_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py
            init_file = class_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f"# {class_name} module")

            # Create class file
            class_result = self._create_class_file(class_dir, class_name, version)
            if class_result != 0:
                return class_result

            # Create registry file
            registry_result = self._create_registry_file(class_dir, class_name, version, target_info)
            if registry_result != 0:
                return registry_result

            print(f"✅ Defined {class_name} in {target_info['package']} -> {class_dir}")
            print(f"📁 Created: {self._to_snake_case(class_name)}_class.py, {self._to_snake_case(class_name)}_registry.yml")
            print(f"🔢 Version: {version}")

            return 0

        except Exception as e:
            print(f"❌ Error creating class: {str(e)}")
            return 1

    def _create_class_file(self, class_dir, class_name, version):
        """Create the class file"""
        try:
            snake_name = self._to_snake_case(class_name)
            created_at = datetime.now().isoformat()

            class_content = f'''#!/usr/bin/env python3
"""
{class_name} class and registry
"""
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class {class_name}:
    """Individual {class_name.lower()} definition"""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.version = "{version}"
        self.created_at = datetime.fromisoformat("{created_at}")
        self.updated_at = self.created_at

        # Store additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {{
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }}

        # Add dynamic attributes
        for key, value in self.__dict__.items():
            if key not in ["name", "version", "created_at", "updated_at"]:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{class_name}':
        """Create from dictionary"""
        name = data.pop("name")
        version = data.pop("version", "1.0.0")
        created_at = data.pop("created_at", None)
        updated_at = data.pop("updated_at", None)

        instance = cls(name, **data)
        instance.version = version

        if created_at:
            instance.created_at = datetime.fromisoformat(created_at)
        if updated_at:
            instance.updated_at = datetime.fromisoformat(updated_at)

        return instance


class {class_name}Registry:
    """Registry holding {class_name} instances"""

    def __init__(self, storage_path: str = None):
        self.items = {{}}
        self.storage_path = storage_path or "{snake_name}_registry.yml"
        self.version = "{version}"
        self.created_at = datetime.fromisoformat("{created_at}")

    def add(self, item: {class_name}) -> bool:
        """Add an item to the registry"""
        if item.name in self.items:
            print(f"⚠️  {{item.name}} already exists in registry")
            return False

        self.items[item.name] = item
        return True

    def get(self, name: str) -> {class_name}:
        """Get an item by name"""
        return self.items.get(name)

    def list(self) -> List[str]:
        """List all item names"""
        return list(self.items.keys())

    def remove(self, name: str) -> bool:
        """Remove an item from registry"""
        if name in self.items:
            del self.items[name]
            return True
        return False

    def save(self):
        """Save registry to YAML file"""
        registry_data = {{
            "registry_version": self.version,
            "registry_type": "{class_name.lower()}",
            "created_at": self.created_at.isoformat(),
            "updated_at": datetime.now().isoformat(),
            "items": {{name: item.to_dict() for name, item in self.items.items()}}
        }}

        with open(self.storage_path, 'w') as f:
            yaml.dump(registry_data, f, default_flow_style=False, sort_keys=False)

    def load(self):
        """Load registry from YAML file"""
        try:
            with open(self.storage_path) as f:
                data = yaml.safe_load(f)

            self.version = data.get("registry_version", "1.0.0")
            if "created_at" in data:
                self.created_at = datetime.fromisoformat(data["created_at"])

            for name, item_data in data.get("items", {{}}).items():
                item = {class_name}.from_dict(item_data)
                self.items[name] = item

        except FileNotFoundError:
            # Registry doesn't exist yet, that's fine
            pass
'''

            # Write class file
            class_file = class_dir / f"{snake_name}_class.py"
            class_file.write_text(class_content)

            return 0

        except Exception as e:
            print(f"❌ Error creating class file: {str(e)}")
            return 1

    def _create_registry_file(self, class_dir, class_name, version, target_info):
        """Create registry YAML file"""
        try:
            snake_name = self._to_snake_case(class_name)

            registry_data = {
                "registry_version": version,
                "registry_type": class_name.lower(),
                "target": target_info['package'],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "items": {},
                "metadata": {
                    "description": f"Registry for {class_name} instances",
                    "class_name": class_name,
                    "auto_backup": True
                }
            }

            registry_file = class_dir / f"{snake_name}_registry.yml"
            with open(registry_file, 'w') as f:
                yaml.dump(registry_data, f, default_flow_style=False, sort_keys=False)

            return 0

        except Exception as e:
            print(f"❌ Error creating registry file: {str(e)}")
            return 1

    def _to_snake_case(self, name):
        """Convert CamelCase to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()