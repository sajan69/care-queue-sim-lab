# Care Queue Simulation Lab

Research prototype for comparing service-queue scheduling strategies using reproducible synthetic workloads. The focus is event-driven algorithms, paired experiments and explicit accounting for requests still waiting when an experiment ends.

Completed-request waiting times do not describe the entire queue. Reports distinguish completed waits, unfinished-request ages, backlog and resource use, with assumptions and experimental uncertainty stated alongside results.

## Research boundary

Workloads are synthetic and are not calibrated to a real hospital or patient population. No patient records, personal identifiers, clinical priority scores or individual eligibility decisions are within scope. Outputs are not staffing, funding, triage or treatment recommendations. Government or clinical adoption requires context-specific validation and appropriate governance review; no regulatory approval or deployment compliance is claimed.

## Local simulation

Python 3.11 or later is required. There are no runtime dependencies, accounts or network calls.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install .
care-queue --scenario late_burst --seed 17 --days 5 --requests 200 --policy early_capacity --trace --out NEW_QUEUE.json
python -m unittest discover -s tests -v
```

Use a new output path under a trusted directory. The JSON result includes generated requests, scheduled service times, cohort hashes, optional event trace and explicit waiting/completion denominators. [Semantics and bounds](docs/SEMANTICS.md) define the two equal-budget capacity calendars, FIFO ties, cutoff behaviour and finite-horizon metrics. [Research-scope assessment](docs/RESEARCH_SCOPE.md) records the Australian governance boundary and source-verification limits.

The event engine and generated scenarios are implemented; no real-world calibration, paired-policy outcome study or performance benchmark is claimed by a single simulation.

## Reference material

- [AIHW elective surgery statistics and interpretation](https://www.aihw.gov.au/hospitals/topics/elective-surgery)
- [Productivity Commission: Public hospitals, Report on Government Services 2026](https://www.pc.gov.au/ongoing/report-on-government-services/health/public-hospitals/)
- [Python heap queue algorithms](https://docs.python.org/3/library/heapq.html)
