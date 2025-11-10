#!/usr/bin/env python3
# tools/ci_monitor_gate.py
import sys, subprocess
# run quick smoke tests relevant to monitor
r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_verify_monitorability.py", "-q"])
if r.returncode != 0:
    print("monitor gate: smoke tests failed")
    sys.exit(2)
print("monitor gate: OK")
sys.exit(0)
