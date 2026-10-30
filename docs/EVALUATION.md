# Synthetic evaluation and compute workload

These results concern generated abstract requests, not patients or observed Australian service performance. [Semantics](SEMANTICS.md) define FIFO dispatch, resource calendars, known service durations, observation cutoff and cohort denominators. The [research assessment](RESEARCH_SCOPE.md) retains Australian governance boundaries and the current source-retrieval limitation.

## Reproduction and evidence

Recorded results were executed locally using an installed wheel, not an editable installation, from code [d9f3bcc](https://github.com/sajan69/care-queue-sim-lab/commit/d9f3bcc0e9a03233e3a7e58572fc701412ae12fa). [Experiment records](experiments.json) retain all 60 replication seeds, cohort hashes, policy metrics used in interpretation, raw paired differences and interval summaries. Additional single-policy metrics are reproducible through the CLI. [Benchmark records](benchmark.json) retain every raw timing repeat and environment. Later CI runs validate the implementation independently and are not the source of the recorded local timings.

```sh
care-queue experiment --scenario late_burst --seed 42 --days 5 --requests 200 --servers 2 --replications 20 --out NEW_EXPERIMENT.json
care-queue experiment --scenario late_burst --seed 42 --days 5 --requests 200 --servers 2 --replications 20 --format html --out NEW_REPORT.html
care-queue benchmark --repeats 3 --out NEW_BENCHMARK.json
```

The [standalone report example](../examples/report.html) needs no server or remote assets. The [three-request cutoff example](../examples/censored-demo.json) is hand-computable: at minute 10, one request has completed, one is in service and one is waiting. Completed wait mean is zero, while restricted queue exposure is 13 minutes in total and 13/3 per arrival. Reporting only the completed mean would omit five minutes waited by the in-service request and eight observed minutes for the still-waiting request.

## Paired comparisons

All three scenarios use master seed 42, five generated days, 200 arrivals per replication, two resources and 20 replication pairs. Each calendar has 4,800 available resource minutes per replication. A pair shares the exact request arrivals and durations; cross-scenario workloads are different and are not paired with each other.

The direction below is **late capacity minus early capacity**. Restricted waiting exposure includes all arrivals but stops observing unstarted requests at the cutoff; it is not estimated ultimate mean wait. Intervals are approximate 95% percentile bootstrap intervals from 1,000 paired resamples. The same bootstrap index stream is used across metrics to preserve algebraic relationships. Small samples and fixed artificial distributions limit inference.

| Scenario | Mean restricted-wait difference, minutes per arrival | Approximate 95% interval | Mean difference in requests still waiting |
| --- | ---: | ---: | ---: |
| Uniform arrivals, 5–60 minute service | -11.260 | -45.831 to +25.427 | -2.75 |
| Late-burst arrivals, 5–60 minute service | -343.393 | -369.417 to -318.732 | -12.20 |
| Uniform arrivals, 60–120 minute service (`overload`) | +55.934 | +43.839 to +66.937 | +0.80 |

There is no universal winner in these scenarios. Later capacity aligns with the artificially late arrivals in the burst workload. The uniform interval spanning zero does not establish equivalence. Longer services and window-fit restrictions change how fragmented capacity is used in the overload scenario. These are observations inside the stated simulation, not causal estimates for a hospital, clinical recommendations or evidence of real savings.

Late-burst workload SHA-256: `a4d5fb80e87404aeed7df408e750a50426e22f6d8aaf7940cdc031df737cf5f8`. Uniform: `b1ebab2ac805164a2dc6f4e61bf3def155259ecc1f116dc0f1a53225e42a4454`. Overload: `698ea1b2abde2fa6ddd6284a970fd7bea9a43362a9100a2013b9052bfe0f4616`. Hashes bind the seed/cohort-hash lists; each replication also records its policy-calendar hashes. They identify generated workloads, not an authenticated clinical dataset.

## Correctness and browser verification

The 19 distinct Python tests cover hand-calculated cutoff cohorts and queue area, completion exactly at cutoff, simultaneous-arrival ordering, global FIFO resource selection, non-preemption, head-of-line blocking, empty/no-capacity nulls, no double booking, invalid inputs, matching budgets, CLI bounds/overwrite guards, bootstrap sign reversal and output escaping. Forty small randomized cases are compared with an independent minute-by-minute oracle; that is one differential test, not a claim of exhaustive coverage or a real-world accuracy percentage.

The installed package passes these tests locally. CI installs the built wheel and runs them on Python 3.11, 3.12 and 3.13. The Python 3.12 job also runs actual experiment exports and the bounded benchmark, and uses Chromium for four checks: rendered cohort/difference values and synthetic-use warning; expandable provenance; 390px body fit with table scrolling; and inert IMG/SCRIPT text without network requests, dialogs or page errors. Screenshots and machine check results are artifacts. Local Chromium 143 checks and desktop/mobile visual inspection passed; CI uses its downloaded browser, whose version need not match.

## Actual compute measurement

Each timing repeat generates 20 late-burst workloads of 200 requests, runs both policies and computes four metrics with 1,000 bootstrap resamples each. That is 40 policy runs and 8,000 request-policy visits per repeat. Every repeat verifies an identical workload hash and restricted-wait difference. The invariant checks inside the engine are included in the timer.

| Repeat | Wall milliseconds |
| --- | ---: |
| 1 | 55.372 |
| 2 | 55.287 |
| 3 | 56.188 |
| Median | 55.372 |

Recorded 31 October 2026 (Brisbane), timestamp `2026-10-30T19:12:05.547254+00:00`. Environment: Python 3.12.14, package 0.1.0, Linux 6.18.57 x86-64/glibc 2.39, nine reported logical CPUs. The standard-library runtime uses a single Python execution thread. `perf_counter` includes generation, hashing, event simulation, invariant checks, metrics and bootstrap summaries; it excludes CLI/import time, serialization/file writes, browser rendering and the post-timer repeat-consistency assertion. No explicit warmup or cache clearing was performed; preceding tests can affect measurements. Shared host scheduling and filesystem characteristics are not controlled. No production-capacity, concurrency or speed-improvement baseline is claimed.

## Interpretation limits

The model excludes real uncertainty in service durations, skills, clinical urgency, cancellations, holidays, staff conditions and patient outcomes. Durations are known in advance for deciding whether service fits in a window. The cutoff censors unfinished waits, and calendar timing can change which requests complete. A conditional completed-only mean is therefore not a valid substitute for all-cohort exposure. No steady-state or survival extrapolation is performed. Bootstrap intervals concern generated replication variability, not uncertainty about a real population. No result supports staffing cuts, funding decisions, individual prioritisation, clinical deployment or government endorsement.
