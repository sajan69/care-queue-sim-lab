import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from care_queue.engine import SimulationError
from care_queue.experiment import experiment,paired_summary
from care_queue.benchmark import benchmark
from care_queue.reports import html_report,csv_report


class ExperimentTests(unittest.TestCase):
    def test_pairs_reuse_workload_budget_and_raw_differences(self):
        r=experiment('uniform',17,2,30,2,10)
        self.assertEqual(len(r['pairs']),10)
        self.assertEqual(len({p['seed'] for p in r['pairs']}),10)
        for p in r['pairs']:
            a,b=(p['policies'][n]['metrics'] for n in r['policy_order'])
            self.assertEqual(a['available_server_minutes'],b['available_server_minutes'])
            self.assertEqual(a['arrived'],b['arrived'])
            self.assertAlmostEqual(p['differences']['restricted_wait_mean'],b['restricted_wait_mean']-a['restricted_wait_mean'])
            for m in (a,b):self.assertEqual(m['arrived'],m['completed']+m['waiting']+m['in_service'])
        self.assertAlmostEqual(r['summaries']['restricted_wait_mean']['mean_difference'],sum(p['differences']['restricted_wait_mean'] for p in r['pairs'])/10)
        self.assertEqual(r['workload_sha256'],experiment('uniform',17,2,30,2,10)['workload_sha256'])

    def test_bootstrap_sign_reversal_and_zero_difference(self):
        a=paired_summary([1,2,3,4],42);b=paired_summary([-1,-2,-3,-4],42)
        self.assertEqual(a['mean_difference'],-b['mean_difference'])
        self.assertAlmostEqual(a['bootstrap_95_percentile'][0],-b['bootstrap_95_percentile'][1])
        z=paired_summary([0]*10,42)
        self.assertEqual(z['bootstrap_95_percentile'],[0,0])
        self.assertEqual(z['replication_difference_sd'],0)

    def test_budget_guards_before_generation_and_benchmark_bounds(self):
        with patch('care_queue.experiment.generate') as generate:
            for kwargs in ({'replications':True},{'replications':101},{'replications':100,'requests':501}):
                with self.assertRaises(SimulationError):experiment(**kwargs)
            generate.assert_not_called()
        for n in (True,0,6):
            with self.assertRaises(SimulationError):benchmark(n)

    def test_static_report_escaping_and_csv_signed_numbers(self):
        import csv,io
        from html.parser import HTMLParser
        r=experiment('late_burst',42,2,30,2,10)
        r['warnings'].append('<img src=x onerror=alert(1)><script>alert(1)</script>')
        body=html_report(r)
        class Parser(HTMLParser):
            def __init__(self):super().__init__();self.tags=[]
            def handle_starttag(self,tag,attrs):self.tags.append(tag)
        p=Parser();p.feed(body)
        self.assertNotIn('script',p.tags);self.assertNotIn('img',p.tags)
        self.assertIn('&lt;img',body);self.assertIn("default-src 'none'",body)
        rows=list(csv.reader(io.StringIO(csv_report(r))))
        self.assertEqual(len(rows),5)
        self.assertEqual(float(rows[1][2]),r['summaries']['restricted_wait_mean']['mean_difference'])

    def test_installed_cli_experiment_and_benchmark(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'result.json'
            run=subprocess.run([sys.executable,'-m','care_queue.cli','experiment','--replications','2','--requests','10','--days','1','--out',str(out)],capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertTrue(json.loads(out.read_text())['completed'])
            bench=Path(td)/'benchmark.json'
            run=subprocess.run([sys.executable,'-m','care_queue.cli','benchmark','--repeats','1','--out',str(bench)],capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            b=json.loads(bench.read_text());self.assertTrue(b['completed']);self.assertEqual(len(b['samples']),1)
