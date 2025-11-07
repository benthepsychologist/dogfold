#!/usr/bin/env python3
"""
DefineSpecVerb - Define classes via templates
"""
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class DefineSpecVerb:
  def execute(self, args):
    if not args:
      print("Usage: spec define class <ClassName> [--domain <name>] [<inline>]")
      return 1
    # Support optional leading 'class'
    if args and args[0] == "class":
      args = args[1:]
      if not args:
        print("Usage: spec define class <ClassName> [--domain <name>] [<inline>]")
        return 1
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
      from src.define_class import DefineClass
      handler = DefineClass()
      result = handler.execute(args)
      print(result)
      return 0 if result.startswith("✅") or result.startswith("⚠️") else 1
    except Exception as e:
      print(f"Error: {e}")
      return 1


