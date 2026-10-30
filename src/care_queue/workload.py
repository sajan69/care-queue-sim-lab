"""Generated scenarios are assumptions, not estimates of hospital demand."""
import random
from .engine import Job, SimulationError, integer

DAY=1440
POLICIES=('early_capacity','late_capacity')
SCENARIOS=('uniform','late_burst','overload')


def calendar(policy,days,servers):
    if policy not in POLICIES:raise SimulationError('unknown_policy')
    integer(days,1,28,'days_1_to_28');integer(servers,1,4,'servers_1_to_4')
    pattern=((480,840),(1080,1200)) if policy=='early_capacity' else ((480,600),(840,1200))
    return tuple(tuple((d*DAY+a,d*DAY+b) for d in range(days) for a,b in pattern) for _ in range(servers))


def generate(scenario='uniform',seed=42,days=5,requests=200):
    if scenario not in SCENARIOS:raise SimulationError('unknown_scenario')
    integer(seed,0,2**32-1,'seed_32bit');integer(days,1,28,'days_1_to_28');integer(requests,1,5000,'requests_1_to_5000')
    rng=random.Random(seed)
    jobs=[]
    for i in range(requests):
        day=rng.randrange(days)
        # Overload is a distinct longer-service workload, not extra hidden staff.
        minute=rng.randrange(480,1200) if scenario!='late_burst' else rng.randrange(840,1200)
        duration=rng.randrange(5,61) if scenario!='overload' else rng.randrange(60,121)
        jobs.append(Job(i+1,day*DAY+minute,duration))
    return tuple(sorted(jobs,key=lambda j:(j.arrival,j.id)))
