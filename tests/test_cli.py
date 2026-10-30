import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from care_queue.io import write
from care_queue.engine import SimulationError


class CliTests(unittest.TestCase):
    def test_installed_cli_generates_synthetic_case_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result.json'
            args=[sys.executable,'-m','care_queue.cli','--scenario','late_burst','--seed','17','--days','2','--requests','30','--trace','--out',str(out)]
            run=subprocess.run(args,capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            data=json.loads(out.read_text())
            self.assertTrue(data['synthetic'])
            self.assertEqual(data['metrics']['arrived'],30)
            m=data['metrics'];self.assertEqual(m['arrived'],m['completed']+m['in_service']+m['waiting'])
            self.assertTrue(data['trace'])
            before=out.read_bytes()
            self.assertEqual(subprocess.run(args,capture_output=True).returncode,2)
            self.assertEqual(out.read_bytes(),before)

    def test_caps_and_symlink_outputs_without_file_creation(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result'
            run=subprocess.run([sys.executable,'-m','care_queue.cli','--requests','5001','--out',str(out)],capture_output=True)
            self.assertEqual(run.returncode,2);self.assertFalse(out.exists())
            target=Path(d)/'keep';target.write_text('keep')
            out.symlink_to(target)
            with self.assertRaises(FileExistsError):write(out,{})
            self.assertEqual(target.read_text(),'keep')

    def test_serialization_and_cap_precede_output_creation(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result'
            for value in ({'x':float('nan')},{'x':'x'*(2*1024*1024)}):
                with self.assertRaises(ValueError):write(out,value)
                self.assertFalse(out.exists())
