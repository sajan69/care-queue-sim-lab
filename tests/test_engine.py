import random
import unittest
from care_queue.engine import Job,SimulationError,simulate
from care_queue.workload import calendar,generate


def minute_oracle(jobs,windows,horizon):
    """Small independent time-step oracle, not the heap/event implementation."""
    records={j.id:{'start':None,'server':None} for j in jobs}
    remaining=sorted(jobs,key=lambda j:(j.arrival,j.id));queue=[];occupied={}
    for t in range(horizon+1):
        occupied={s:end for s,end in occupied.items() if end>t}
        queue.extend(j for j in remaining if j.arrival==t)
        if t==horizon:break
        while queue:
            head=queue[0]
            feasible=[]
            for s,intervals in enumerate(windows):
                if s not in occupied and any(a<=t and t+head.duration<=b for a,b in intervals):
                    feasible.append(s)
            if not feasible:break
            server=min(feasible);queue.pop(0)
            records[head.id]={'start':t,'server':server}
            occupied[server]=t+head.duration
    return records


class EngineTests(unittest.TestCase):
    def test_handcomputed_completed_in_service_waiting_and_censored_area(self):
        r=simulate((Job(1,0,6),Job(2,1,6),Job(3,2,2)),(((0,12),),),10,trace=True)
        m=r['metrics']
        self.assertEqual((m['completed'],m['in_service'],m['waiting']),(1,1,1))
        self.assertEqual(m['completed_wait_mean'],0)
        self.assertEqual(m['started_wait_mean'],2.5)
        self.assertEqual(m['waiting_age_mean'],8)
        self.assertEqual(m['restricted_wait_total'],13)
        self.assertAlmostEqual(m['restricted_wait_mean'],13/3)
        self.assertEqual(m['busy_server_minutes'],10)
        self.assertEqual(m['available_server_minutes'],10)
        self.assertTrue(r['jobs'][2]['wait_right_censored'])
        self.assertFalse(r['jobs'][1]['wait_right_censored'])
        self.assertEqual(r['jobs'][1]['scheduled_completion'],12)

    def test_completion_at_cutoff_counted_no_new_start_at_cutoff(self):
        r=simulate((Job(1,0,10),Job(2,0,1)),(((0,20),),),10)
        self.assertEqual(r['metrics']['completed'],1)
        self.assertIsNone(r['jobs'][1]['start'])
        self.assertEqual(r['metrics']['restricted_wait_total'],10)

    def test_simultaneous_arrivals_order_by_id_not_input_order(self):
        jobs=(Job(3,0,2),Job(1,0,2),Job(2,0,2))
        a=simulate(jobs,(((0,10),),),10)
        b=simulate(tuple(reversed(jobs)),(((0,10),),),10)
        self.assertEqual(a,b)
        self.assertEqual([r['start'] for r in a['jobs']],[0,2,4])

    def test_global_fifo_revisits_idle_server_after_head_assigns_elsewhere(self):
        r=simulate((Job(1,0,6),Job(2,0,2)),(((0,5),),((0,10),)),10)
        self.assertEqual([(x['start'],x['server']) for x in r['jobs']],[(0,1),(0,0)])

    def test_nonpreemption_and_head_of_line_blocking(self):
        r=simulate((Job(1,3,6),Job(2,4,1)),(((0,5),(8,15)),),15)
        self.assertEqual([x['start'] for x in r['jobs']],[8,14])
        self.assertEqual(r['metrics']['busy_server_minutes'],7)

    def test_empty_cohort_and_zero_capacity_have_null_means(self):
        empty=simulate((),((),),10)['metrics']
        self.assertIsNone(empty['completed_wait_mean']);self.assertIsNone(empty['restricted_wait_mean'])
        self.assertIsNone(empty['utilization'])
        pending=simulate((Job(1,0,5),),((),),10)['metrics']
        self.assertEqual(pending['restricted_wait_mean'],10)
        self.assertEqual(pending['waiting'],1)
        self.assertIsNone(pending['completed_wait_mean'])

    def test_small_random_cases_match_independent_minute_oracle(self):
        for seed in range(40):
            rng=random.Random(seed);h=30
            jobs=tuple(Job(i+1,rng.randrange(0,h),rng.randrange(1,9)) for i in range(15))
            windows=(((0,10),(15,35)),((3,13),(17,35)))
            r=simulate(jobs,windows,h,trace=True)
            oracle=minute_oracle(jobs,windows,h)
            with self.subTest(seed=seed):
                self.assertEqual({x['id']:{'start':x['start'],'server':x['server']} for x in r['jobs']},oracle)
                for x in r['trace']:
                    self.assertEqual(x['arrived'],x['completed']+x['waiting']+x['in_service'])
                self.assertEqual(sorted(t['minute'] for t in r['trace']),[t['minute'] for t in r['trace']])

    def test_no_double_booking_and_service_within_window(self):
        jobs=generate('overload',42,3,200)
        windows=calendar('late_capacity',3,2)
        r=simulate(jobs,windows,3*1440)
        for s in range(2):
            started=sorted((x for x in r['jobs'] if x['server']==s),key=lambda x:x['start'])
            self.assertTrue(all(a['scheduled_completion']<=b['start'] for a,b in zip(started,started[1:])))
            self.assertTrue(all(any(lo<=x['start'] and x['scheduled_completion']<=hi for lo,hi in windows[s]) for x in started))

    def test_invalid_types_limits_duplicates_and_windows_refused(self):
        good=(Job(1,0,1),)
        for jobs,windows,h in [(good,(((0,10),(9,20)),),20),(good,(((0,10),(10,20)),),20),
                               ((Job(True,0,1),),(((0,10),),),10),((Job(1,10,1),),(((0,10),),),10),
                               (good+good,(((0,10),),),10),(good,(((0,10),),),True),
                               ((Job(1,0,0),),(((0,10),),),10),(good,(),10)]:
            with self.subTest(case=(jobs,windows,h)),self.assertRaises(SimulationError):simulate(jobs,windows,h)

    def test_generated_pairs_have_same_cohort_and_equal_effective_capacity(self):
        jobs=generate('late_burst',17,5,200)
        a=simulate(jobs,calendar('early_capacity',5,2),5*1440)
        b=simulate(jobs,calendar('late_capacity',5,2),5*1440)
        self.assertEqual(a['cohort_sha256'],b['cohort_sha256'])
        self.assertEqual(a['metrics']['available_server_minutes'],4800)
        self.assertEqual(a['metrics']['available_server_minutes'],b['metrics']['available_server_minutes'])
        self.assertEqual(jobs,generate('late_burst',17,5,200))

    def test_generator_caps_before_allocation(self):
        for value in (True,0,5001):
            with self.subTest(value=value),self.assertRaises(SimulationError):generate(requests=value)
        with self.assertRaises(SimulationError):generate(scenario='real_patients')
