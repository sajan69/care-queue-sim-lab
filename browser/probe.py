"""Internal adversarial render fixture, not a data import endpoint."""
import json
from pathlib import Path
from care_queue.reports import html_report
from care_queue.io import write_bytes
root=Path(__file__).resolve().parents[1]
r=json.loads((root/'artifacts/experiment.json').read_text())
r['warnings'].append('<img src=x onerror=alert(1)><script>alert(1)</script>')
write_bytes(root/'artifacts/probe.html',html_report(r).encode())
