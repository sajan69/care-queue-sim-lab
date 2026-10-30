# Simulation semantics

Time is an integer count of experiment minutes, not a dated Australian roster or a timezone-aware clinical clock. A synthetic day has 1,440 minutes. The two resource-availability patterns repeat every day, without weekends, holidays, staff skills, statutory breaks or workplace rules. They are abstract capacity calendars, not compliant employee rosters.

## Cohort and service

Every generated request arrives in `[0, horizon)` and has a positive, pre-generated service duration. IDs are sequence integers, not patient identifiers. A request is queued once and served at most once. Service is non-preemptive: a request starts only if its entire duration fits within a single resource window. No service overrun is permitted. A long head request can leave capacity idle; a shorter later request cannot bypass it.

At each event minute, completions are applied first, then openings, then all arrivals. Simultaneous arrivals are ordered by request ID. Dispatch takes the FIFO head and the lowest-numbered free resource whose current window can fit it, then repeats. A previously skipped idle resource is reconsidered for the next head. No new service starts at the observation horizon; completion exactly at the horizon is counted as completed.

A scheduled completion after the observation horizon is not an observed completion. Such a request is `in_service`. A request without a start is `waiting`. These cohorts plus `completed` partition all arrivals. The engine integrates queue length and busy resource count between events, and checks conservation and area identities. Event traces record post-dispatch state; `max_waiting_at_event` is not a transient queue count before simultaneous dispatch.

## Generated scenarios and equal budgets

The generator uses a local seeded `random.Random`, preserving the actual generated request projection and its SHA-256 in each result. It does not fit distributions to public statistics. `uniform` draws arrival minutes uniformly between 08:00 and 20:00 on a generated day; `late_burst` restricts them to 14:00–20:00. Their durations are integer uniform 5–60 minutes inclusive. `overload` uses the uniform arrival window and 60–120 minute durations. Days are sampled uniformly. These names describe assumptions, not real demand estimates.

`early_capacity` has windows 08:00–14:00 and 18:00–20:00. `late_capacity` has windows 08:00–10:00 and 14:00–20:00. Each provides 480 minutes per resource per generated day. Comparisons retain the same request arrivals and durations; only window timing changes. There is no clinical priority or hidden extra resource budget. Experiment results must verify both cohort hashes and effective capacity equality.

## Denominators and censoring

- Completed wait mean: wait from arrival to start, for requests completed by the horizon only.
- Started wait mean: wait from arrival to start for all started requests, including those still in service.
- Waiting age: time since arrival for requests that have not started. Their ultimate wait is right-censored at the observation horizon.
- Unfinished age: time since arrival for both waiting and in-service requests. It is not entirely queue waiting for in-service requests.
- Restricted waiting exposure: sum of observed queue waiting for the entire arrival cohort, divided by all arrivals. For a waiting request, observed waiting stops at the horizon. This is a finite-horizon, censored measure, not estimated ultimate mean wait.
- Utilization: busy resource minutes observed within the horizon divided by available resource minutes within the horizon. No capacity gives null, not zero utilization.

Empty cohorts have null means. Completed-only means can improve while the backlog worsens; they must not be compared without the other cohorts and denominators. There is no survival-model extrapolation, steady-state claim or automatic policy recommendation.

## Bounds

The Python engine accepts up to 5,000 generated requests, four resources, 56 windows per resource and a 28-day observation horizon. Adjacent windows must be merged explicitly; overlapping or unordered windows are refused. A window may extend at most one day past the observation horizon, supporting explicit in-service censoring cases. The CLI only generates predefined synthetic workloads and does not import files or personal data.

JSON outputs are capped at 2 MiB before exclusive creation. Trace-heavy large workloads can be refused instead of truncated. New POSIX files use mode 0600 and existing paths, including symlinks, are not overwritten. Parent directories must be trusted; physical write failure can leave an incomplete output. Windows ACLs remain the user's responsibility.
