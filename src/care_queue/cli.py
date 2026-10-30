"""Bounded offline commands; no external-data import."""
import argparse
import json
from pathlib import Path
import os
from . import __version__
from .engine import SimulationError,simulate
from .io import write,write_bytes
from .workload import generate,calendar,SCENARIOS,POLICIES,DAY


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',action='version',version=__version__)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('simulate','experiment'):
        s=sub.add_parser(name)
        s.add_argument('--scenario',choices=SCENARIOS,default='uniform')
        s.add_argument('--seed',type=int,default=42)
        s.add_argument('--days',type=int,default=5)
        s.add_argument('--requests',type=int,default=200)
        s.add_argument('--servers',type=int,default=2)
        s.add_argument('--out',type=Path,required=True)
        if name=='simulate':
            s.add_argument('--policy',choices=POLICIES,default='early_capacity')
            s.add_argument('--trace',action='store_true')
        else:
            s.add_argument('--replications',type=int,default=20)
            s.add_argument('--format',choices=('json','html','csv'),default='json')
    b=sub.add_parser('benchmark')
    b.add_argument('--repeats',type=int,default=3)
    b.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:
        if os.path.lexists(a.out):raise SimulationError('output_already_exists')
        if a.command=='benchmark':
            from .benchmark import benchmark
            result=benchmark(a.repeats);write(a.out,result)
            print(json.dumps({'completed':result['completed'],'median_milliseconds':result['median_milliseconds']}))
        elif a.command=='experiment':
            from .experiment import experiment
            result=experiment(a.scenario,a.seed,a.days,a.requests,a.servers,a.replications)
            if a.format=='json':write(a.out,result)
            else:
                from .reports import html_report,csv_report
                value=html_report(result) if a.format=='html' else csv_report(result)
                write_bytes(a.out,value.encode())
            print(json.dumps({'completed':True,'summaries':result['summaries'],'workload_sha256':result['workload_sha256']}))
        else:
            jobs=generate(a.scenario,a.seed,a.days,a.requests)
            result=simulate(jobs,calendar(a.policy,a.days,a.servers),a.days*DAY,trace=a.trace)
            result['configuration']={'scenario':a.scenario,'seed':a.seed,'days':a.days,'requests':a.requests,'servers':a.servers,'policy':a.policy}
            write(a.out,result);print(json.dumps(result['metrics'],allow_nan=False))
    except (SimulationError,OSError) as e:
        print(json.dumps({'error':str(e) if isinstance(e,SimulationError) else 'output_access_failed'}))
        raise SystemExit(2) from None


if __name__=='__main__':main()
