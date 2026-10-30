"""Paired synthetic experiments; uncertainty concerns generated replications only."""
from datetime import datetime,timezone
import platform
import random
import statistics
import sys
from . import __version__
from .engine import SimulationError,integer,simulate,digest
from .workload import generate,calendar,DAY,POLICIES,SCENARIOS

METRICS=('restricted_wait_mean','waiting','completed','busy_server_minutes')
WARNINGS=[
 'Synthetic scenarios only; no hospital calibration or individual decisions.',
 'Finite-horizon restricted waiting exposure is censored, not ultimate mean wait.',
 'Completed-only means have different completed cohorts and must not hide the backlog.',
 'Service durations are known in advance for window-fit decisions; real uncertainty is absent.',
 'Equal resource minutes do not establish clinically interchangeable or compliant staff rosters.',
 'Bootstrap intervals describe Monte Carlo uncertainty within this scenario, not real-world predictions.',
 'No staffing, funding, triage, treatment or government deployment recommendation is provided.',
]


def quantile(values,p):
    ordered=sorted(values);position=(len(ordered)-1)*p
    lower=int(position);upper=min(lower+1,len(ordered)-1);fraction=position-lower
    return ordered[lower]*(1-fraction)+ordered[upper]*fraction


def paired_summary(differences,seed):
    rng=random.Random(seed)
    draws=[statistics.fmean(rng.choices(differences,k=len(differences))) for _ in range(1000)]
    return {'pairs':len(differences),'mean_difference':statistics.fmean(differences),
            'replication_difference_sd':statistics.stdev(differences),
            'bootstrap_95_percentile':[quantile(draws,.025),quantile(draws,.975)],
            'bootstrap_draws':1000}


def environment():
    return {'python':sys.version.split()[0],'platform':platform.platform(),'package_version':__version__}


def experiment(scenario='late_burst',seed=42,days=5,requests=200,servers=2,replications=20):
    if scenario not in SCENARIOS:raise SimulationError('unknown_scenario')
    integer(seed,0,2**32-1,'seed_32bit');integer(days,1,28,'days_1_to_28')
    integer(requests,1,5000,'requests_1_to_5000');integer(servers,1,4,'servers_1_to_4')
    integer(replications,2,100,'replications_2_to_100')
    if replications*requests>50000:raise SimulationError('experiment_job_budget')
    seeds=random.Random(seed).sample(range(2**32),replications)
    calendars={p:calendar(p,days,servers) for p in POLICIES}
    pairs=[]
    for child_seed in seeds:
        jobs=generate(scenario,child_seed,days,requests)
        results={p:simulate(jobs,calendars[p],days*DAY) for p in POLICIES}
        a,b=(results[p] for p in POLICIES)
        if a['cohort_sha256']!=b['cohort_sha256'] or a['metrics']['available_server_minutes']!=b['metrics']['available_server_minutes']:
            raise SimulationError('pairing_or_budget_invariant')
        pairs.append({'seed':child_seed,'cohort_sha256':a['cohort_sha256'],
                      'policies':{p:{'calendar_sha256':r['calendar_sha256'],'metrics':r['metrics']} for p,r in results.items()},
                      'differences':{k:b['metrics'][k]-a['metrics'][k] for k in METRICS}})
    summaries={k:paired_summary([p['differences'][k] for p in pairs],seed^104729) for k in METRICS}
    return {'schema_version':1,'synthetic':True,'completed':True,'created_at':datetime.now(timezone.utc).isoformat(),
            'configuration':{'scenario':scenario,'master_seed':seed,'days':days,'requests_per_replication':requests,
                             'servers':servers,'replications':replications},
            'policy_order':list(POLICIES),'difference_direction':'late_capacity minus early_capacity',
            'workload_sha256':digest([{'seed':p['seed'],'cohort_sha256':p['cohort_sha256']} for p in pairs]),
            'summaries':summaries,'pairs':pairs,'warnings':WARNINGS,'environment':environment(),
            'method':{'bootstrap':'1000 resamples of paired replication differences, percentile interval with linear interpolation',
                      'assumptions':'Independent generated workload seeds; fixed scenario and policies; no real-world uncertainty model',
                      'capacity':'480 minutes per resource per day; same jobs and budget within every pair',
                      'primary_metric':'restricted_wait_mean across all arrivals; lower is less observed queue exposure'}}
