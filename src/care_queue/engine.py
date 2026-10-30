"""Integer-time event engine with non-preemptive FIFO service."""
from collections import deque
from dataclasses import dataclass
import hashlib
import heapq
import json
import statistics

MAX_JOBS = 5000
MAX_HORIZON = 28 * 1440


class SimulationError(ValueError):
    pass


def integer(value, low, high, code):
    if type(value) is not int or not low <= value <= high:
        raise SimulationError(code)
    return value


@dataclass(frozen=True)
class Job:
    id: int
    arrival: int
    duration: int


def validate(jobs, windows, horizon):
    integer(horizon, 1, MAX_HORIZON, 'horizon_limit')
    if not isinstance(jobs, tuple) or len(jobs) > MAX_JOBS:
        raise SimulationError('jobs_limit_or_type')
    ids = set()
    for j in jobs:
        if not isinstance(j, Job):
            raise SimulationError('job_type')
        integer(j.id,1,MAX_JOBS,'job_id');integer(j.arrival,0,horizon-1,'arrival');integer(j.duration,1,240,'duration')
        if j.id in ids:
            raise SimulationError('duplicate_job_id')
        ids.add(j.id)
    if not isinstance(windows, tuple) or not 1 <= len(windows) <= 4:
        raise SimulationError('server_limit_or_type')
    for server in windows:
        if not isinstance(server,tuple) or len(server)>56:
            raise SimulationError('window_limit_or_type')
        previous = -1
        for pair in server:
            if not isinstance(pair,tuple) or len(pair)!=2:
                raise SimulationError('window_shape')
            start,end=pair
            integer(start,0,horizon+1440,'window_start');integer(end,1,horizon+1440,'window_end')
            if start>=end or start<previous:
                raise SimulationError('overlapping_or_unsorted_windows')
            if start == previous:
                raise SimulationError('adjacent_windows_must_be_merged')
            previous=end


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def mean(values):
    return statistics.fmean(values) if values else None


def simulate(jobs, windows, horizon, *, trace=False):
    validate(jobs,windows,horizon)
    if type(trace) is not bool:
        raise SimulationError('trace_flag')
    jobs=tuple(sorted(jobs,key=lambda j:(j.arrival,j.id)))
    cohort=[{'id':j.id,'arrival':j.arrival,'duration':j.duration} for j in jobs]
    result={j.id:{**r,'start':None,'scheduled_completion':None,'server':None} for j,r in zip(jobs,cohort)}
    events=[];sequence=0
    def schedule(at,priority,kind,payload):
        nonlocal sequence
        heapq.heappush(events,(at,priority,sequence,kind,payload));sequence+=1
    for j in jobs:
        schedule(j.arrival,2,'arrival',j.id)
    for s, intervals in enumerate(windows):
        for start,end in intervals:
            if start < horizon:
                schedule(start,1,'open',(s,end))
    waiting=deque();busy=[None]*len(windows);available_end=[-1]*len(windows)
    arrived=completed=0;last=0;wait_area=busy_area=0;max_queue=0;processed=0;log=[]
    while events and events[0][0]<=horizon:
        now=events[0][0]
        if now<last:
            raise SimulationError('clock_invariant')
        wait_area+=len(waiting)*(now-last)
        busy_area+=sum(j is not None for j in busy)*(now-last)
        batch=[]
        while events and events[0][0]==now:
            batch.append(heapq.heappop(events))
        for _,_,_,kind,payload in batch:
            processed+=1
            if kind=='complete':
                s,jid=payload
                if busy[s]!=jid:
                    raise SimulationError('server_invariant')
                busy[s]=None;completed+=1
            elif kind=='open':
                s,end=payload;available_end[s]=end
            else:
                waiting.append(payload);arrived+=1
        # All simultaneous arrivals are queued before dispatch. Completion ties
        # precede openings and arrivals; server IDs settle dispatch ties.
        if now<horizon:
            while waiting:
                jid=waiting[0];row=result[jid]
                eligible=[s for s in range(len(windows)) if busy[s] is None and now+row['duration']<=available_end[s]]
                if not eligible:
                    break  # never bypass an earlier FIFO job to fit a shorter one
                s=eligible[0]
                waiting.popleft();busy[s]=jid
                row.update(start=now,scheduled_completion=now+row['duration'],server=s)
                schedule(row['scheduled_completion'],0,'complete',(s,jid))
        max_queue=max(max_queue,len(waiting))
        if arrived!=completed+len(waiting)+sum(x is not None for x in busy):
            raise SimulationError('conservation_invariant')
        if trace:
            log.append({'minute':now,'arrived':arrived,'completed':completed,
                        'waiting':len(waiting),'in_service':sum(x is not None for x in busy)})
        last=now
    wait_area+=len(waiting)*(horizon-last)
    busy_area+=sum(j is not None for j in busy)*(horizon-last)
    rows=[];completed_waits=[];started_waits=[];waiting_ages=[];unfinished_ages=[]
    for j in jobs:
        r=result[j.id]
        status='waiting' if r['start'] is None else ('completed' if r['scheduled_completion']<=horizon else 'in_service')
        wait_observed=(r['start'] if r['start'] is not None else horizon)-j.arrival
        if r['start'] is not None:started_waits.append(wait_observed)
        if status=='completed':completed_waits.append(wait_observed)
        if status=='waiting':waiting_ages.append(horizon-j.arrival)
        if status!='completed':unfinished_ages.append(horizon-j.arrival)
        rows.append({**r,'status':status,'restricted_wait_minutes':wait_observed,
                     'wait_right_censored':status=='waiting',
                     'unfinished_age_minutes':horizon-j.arrival if status!='completed' else None})
    capacity=sum(max(0,min(end,horizon)-start) for server in windows for start,end in server if start<horizon)
    observed_busy=sum(max(0,min(r['scheduled_completion'],horizon)-r['start']) for r in rows if r['start'] is not None)
    if wait_area!=sum(r['restricted_wait_minutes'] for r in rows) or busy_area!=observed_busy or busy_area>capacity:
        raise SimulationError('area_or_capacity_invariant')
    if trace:
        final={'minute':horizon,'arrived':arrived,'completed':completed,'waiting':len(waiting),'in_service':len(started_waits)-completed}
        if not log or log[-1]!=final:log.append(final)
    return {'schema_version':1,'synthetic':True,'horizon_minutes':horizon,
            'cohort_sha256':digest(cohort),'calendar_sha256':digest(windows),
            'metrics':{'arrived':arrived,'completed':completed,'in_service':len(started_waits)-completed,
                       'waiting':len(waiting),'started':len(started_waits),
                       'completed_wait_mean':mean(completed_waits),'completed_wait_n':len(completed_waits),
                       'started_wait_mean':mean(started_waits),'started_wait_n':len(started_waits),
                       'waiting_age_mean':mean(waiting_ages),'waiting_age_n':len(waiting_ages),
                       'unfinished_age_mean':mean(unfinished_ages),'unfinished_n':len(unfinished_ages),
                       'restricted_wait_total':wait_area,'restricted_wait_mean':wait_area/arrived if arrived else None,
                       'restricted_wait_n':arrived,'queue_area_minutes':wait_area,
                       'busy_server_minutes':busy_area,'available_server_minutes':capacity,
                       'utilization':busy_area/capacity if capacity else None,
                       'unused_server_minutes':capacity-busy_area,'max_waiting_at_event':max_queue,
                       'events_processed':processed},
            'jobs':rows,'trace':log}
