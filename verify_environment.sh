#!/bin/bash
# verify_environment.sh — run before every FYP demo/eval, and ideally in CI
set -e
python3 -c "
from hexstrike_server import load_tool_manifest, build_tools_status, preflight_check
import sys
try:
    manifest = load_tool_manifest()
    status = build_tools_status()
    preflight_check(status)
    missing = [t for t, ok in status.items() if not ok]
    print(f'{sum(status.values())}/{len(status)} tools available.')
    if missing:
        print(f'Missing: {missing}')
        sys.exit(1)
    print('Environment OK.')
except SystemExit as e:
    sys.exit(e.code)
except Exception as e:
    print(f'Error verifying environment: {e}')
    sys.exit(1)
"
