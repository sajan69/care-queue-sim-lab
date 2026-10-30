"""Run a bounded generated queue, without importing real requests."""
import argparse
import json
from pathlib import Path
import os
from . import __version__
from .engine import SimulationError,simulate
from .io import write
from .workload import generate,calendar,SCENARIOS,POLICIES,DAY


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',action='version',version=__version__)
    p.add_argument('--scenario',choices=SCENARIOS,default='uniform')
    p.add_argument('--policy',choices=POLICIES,default='early_capacity')
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--days',type=int,default=5)
    p.add_argument('--requests',type=int,default=200)
    p.add_argument('--servers',type=int,default=2)
    p.add_argument('--trace',action='store_true')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:
        if os.path.lexists(a.out):raise SimulationError('output_already_exists')
        jobs=generate(a.scenario,a.seed,a.days,a.requests)
        result=simulate(jobs,calendar(a.policy,a.days,a.servers),a.days*DAY,trace=a.trace)
        result['configuration']={'scenario':a.scenario,'seed':a.seed,'days':a.days,'requests':a.requests,'servers':a.servers,'policy':a.policy}
        write(a.out,result)
        print(json.dumps(result['metrics'],allow_nan=False))
    except (SimulationError,OSError) as e:
        print(json.dumps({'error':str(e) if isinstance(e,SimulationError) else 'output_access_failed'}))
        raise SystemExit(2) from None


if __name__=='__main__':main()
