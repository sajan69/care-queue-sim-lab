# Local execution boundary

The CLI accepts bounded numeric parameters and three fixed generated scenarios. It has no file-import, URL, credentials, network-service or patient-record endpoint. Request IDs are generated integers. The internal Python engine is a trusted programming API; a `synthetic` result flag is a statement of intended use, not a detector or anonymisation guarantee for arbitrary caller-supplied values.

The runtime has no third-party dependencies and does not deserialize fitted objects, evaluate expressions, run SQL or load plugins. Counts, IDs, times, window ordering, resource limits and duplicate jobs are checked before event-heap allocation. Experiments are capped at 50,000 generated requests across replications. Benchmarks have a fixed workload and 1–5 repeats. Python's seeded random generator provides reproducibility, not cryptographic randomness or a privacy mechanism.

Every simulation checks arrival conservation and the identities between queue/busy time integrals and per-request observed exposure. Windows cannot overlap on a resource, service does not overrun a window, and cutoff cohorts remain distinct. These controls verify the stated model; they do not validate the model as a description of a real service.

All JSON/CSV/HTML outputs are serialized and capped at 2 MiB before exclusive creation. Existing paths and symlinks are refused; new POSIX files use mode 0600. Trusted parent directories are required. Filesystem race resistance, encryption, multi-user isolation, atomic replacement and crash/power-loss guarantees are not provided. A physical write failure can leave a partial file. Windows ACLs remain the user's responsibility.

Static HTML escapes displayed text and has a restrictive stylesheet-hash Content Security Policy, no scripts and no external assets. Browser tests include an internal adversarial text probe. CSV uses quoted cells and controlled scenario/metric names with generated numeric values; it is not a general exporter for arbitrary untrusted labels. No reports are uploaded automatically.

Scope and Australian governance applicability are documented in [RESEARCH_SCOPE](RESEARCH_SCOPE.md), including the source-retrieval limitation on 31 October 2026. No government deployment approval, legal certification, institutional research exemption or medical-device ruling is claimed. Any real data, individual prioritisation, staffing use or other operational adoption changes the assessment.
