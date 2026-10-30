# Care Queue Simulation Lab

Research prototype for comparing service-queue scheduling strategies using reproducible synthetic workloads. The focus is event-driven algorithms, paired experiments and explicit accounting for requests still waiting when an experiment ends.

Completed-request waiting times do not describe the entire queue. Reports distinguish completed waits, unfinished-request ages, backlog and resource use, with assumptions and experimental uncertainty stated alongside results.

## Research boundary

Workloads are synthetic and are not calibrated to a real hospital or patient population. No patient records, personal identifiers, clinical priority scores or individual eligibility decisions are within scope. Outputs are not staffing, funding, triage or treatment recommendations. Government or clinical adoption requires context-specific validation and appropriate governance review; no regulatory approval or deployment compliance is claimed.

No simulator implementation or measured results are included yet.

## Reference material

- [AIHW elective surgery statistics and interpretation](https://www.aihw.gov.au/hospitals/topics/elective-surgery)
- [Productivity Commission: Public hospitals, Report on Government Services 2026](https://www.pc.gov.au/ongoing/report-on-government-services/health/public-hospitals/)
- [Python heap queue algorithms](https://docs.python.org/3/library/heapq.html)
