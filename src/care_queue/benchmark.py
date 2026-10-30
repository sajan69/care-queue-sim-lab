"""Fixed bounded workload, with actual timing and correctness checks."""
from datetime import datetime,timezone
import os
import statistics
from time import perf_counter
from .engine import integer
from .experiment import experiment,environment


def benchmark(repeats=3):
    integer(repeats,1,5,'benchmark_repeats_1_to_5')
    samples=[];expected=None
    for i in range(repeats):
        start=perf_counter()
        result=experiment('late_burst',42,5,200,2,20)
        elapsed=(perf_counter()-start)*1000
        score=result['summaries']['restricted_wait_mean']['mean_difference']
        fingerprint=(result['workload_sha256'],score)
        if expected is None:expected=fingerprint
        if fingerprint!=expected:raise ValueError('benchmark_result_changed')
        samples.append({'repeat':i+1,'milliseconds':elapsed,'restricted_wait_difference':score})
    return {'completed':True,'created_at':datetime.now(timezone.utc).isoformat(),
            'environment':environment(),'logical_cpus':os.cpu_count(),'workload_sha256':expected[0],
            'workload':{'scenario':'late_burst','master_seed':42,'days':5,'requests':200,'servers':2,'replications':20,
                        'policy_runs':40,'request_policy_visits':8000,'bootstrap_resamples_per_metric':1000,'metrics':4},
            'samples':samples,'median_milliseconds':statistics.median(x['milliseconds'] for x in samples),
            'method':{'included':'generation, hashing, both event simulations, invariant checks, metrics and bootstrap summaries',
                      'excluded':'CLI/import time, serialization/file writes, browser and post-timer repeat consistency assertion',
                      'warmup':'no explicit warmup or cache clearing; preceding tests may affect timings',
                      'limits':'shared host, single client; no production capacity or performance-improvement baseline'}}
