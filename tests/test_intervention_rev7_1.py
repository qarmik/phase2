import subprocess
import sys

def test_intervention_valid():
    subprocess.check_call([
        sys.executable,
        "tools/validate_intervention_rev7_1.py",
        "logs/intervention_event_rev7_1.json"
    ])
