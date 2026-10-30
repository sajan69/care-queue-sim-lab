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
care-queue simulate --scenario late_burst --seed 17 --days 5 --requests 200 --policy early_capacity --trace --out NEW_QUEUE.json
python -m unittest discover -s tests -v
```

Use a new output path under a trusted directory. The JSON result includes generated requests, scheduled service times, cohort hashes, optional event trace and explicit waiting/completion denominators. [Semantics and bounds](docs/SEMANTICS.md) define the two equal-budget capacity calendars, FIFO ties, cutoff behaviour and finite-horizon metrics. [Research-scope assessment](docs/RESEARCH_SCOPE.md) records the Australian governance boundary and source-verification limits.

## Paired experiments

```sh
care-queue experiment --scenario late_burst --seed 42 --replications 20 --out NEW_EXPERIMENT.json
care-queue experiment --scenario late_burst --seed 42 --replications 20 --format html --out NEW_REPORT.html
care-queue experiment --scenario late_burst --seed 42 --replications 20 --format csv --out NEW_METRICS.csv
care-queue benchmark --repeats 3 --out NEW_BENCHMARK.json
```

Open the HTML locally: it needs no scripts, server or remote assets. Experiment JSON preserves every replication's seed, cohort hash, policy metrics and signed differences. Both calendars receive identical generated requests and equal observed capacity. The primary metric includes all arrivals; completed-only averages remain separate. Bootstrap intervals describe simulation variability under fixed assumptions, not uncertainty about actual health services.

[Recorded evaluation](docs/EVALUATION.md) gives exact synthetic outcomes, measured compute workload and limitations. The CLI has no patient-data import. Outputs are capped and refuse overwrites; large traces may be refused rather than truncated.

## Reference material

- [AIHW elective surgery statistics and interpretation](https://www.aihw.gov.au/hospitals/topics/elective-surgery)
- [Productivity Commission: Public hospitals, Report on Government Services 2026](https://www.pc.gov.au/ongoing/report-on-government-services/health/public-hospitals/)
- [Python heap queue algorithms](https://docs.python.org/3/library/heapq.html)

## Architecture and verification

The standard-library runtime generates requests, validates finite calendars, processes a stable-priority event heap, verifies conservation/area identities, then summarizes paired replications and serializes bounded local outputs. No database or network service is needed. The report keeps the unfinished queue visible alongside completed work.

There are 19 distinct Python tests, including 40 small oracle comparisons. CI installs the built package on Python 3.11–3.13; Chromium checks the generated report at desktop/mobile widths and tests inert HTML payloads. [Security controls](docs/SECURITY.md) describe input limits, trusted local execution and exclusive output files.
