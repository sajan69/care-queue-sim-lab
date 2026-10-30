# Synthetic queue research boundary

Assessment date: 31 October 2026. This is a scope-specific design assessment, not legal advice, research-ethics approval or a regulatory determination. The governance sources below were last verified on 30 October 2026. Changes since that review could not be independently verified on 31 October. This assessment therefore does not certify the current policy text or operational compliance; any adopter must verify current requirements before use.

## Purpose and data

The software compares abstract service-capacity calendars using generated synthetic requests. It measures how changing the timing of a fixed resource budget affects waiting and unfinished work in finite experiments. Intended readers are analysts inspecting algorithms and simulation assumptions. It is not calibrated to a hospital, clinician, patient population or government program.

The CLI generates workloads from bounded scenarios and seeds. It has no patient-data import, record linkage, clinical urgency scores, protected-attribute modelling, eligibility assessment, live scheduling or automatic allocation endpoint. Internal request IDs are generated sequence numbers. No participants are recruited and no observations about real individuals are collected. Source publications provide context only; their aggregate statistics are not converted into patient distributions or used as calibration data.

## Australian applicability assessment

| Source | Relevance to this design | Boundary for changed use |
| --- | --- | --- |
| [OAIC Australian Privacy Principles](https://www.oaic.gov.au/privacy/australian-privacy-principles) | Privacy Act obligations depend on covered entities and personal-information handling. This design does not require personal data. Synthetic generation is a data boundary, not a statutory exemption or proof that arbitrary user data is anonymous. | Real requests, linkage, logs or adopted agency systems require entity/jurisdiction-specific privacy and security assessment. |
| [Queensland Privacy Principles](https://www.oic.qld.gov.au/government/privacy/queensland-privacy-principles) | Agency and contractor obligations under Queensland privacy law depend on context. This repository is not an agency scheduling system. | An adopter must establish applicability, privacy-impact requirements and controls. Other states have their own requirements. |
| [Australian Government AI policy](https://www.digital.gov.au/ai/ai-in-government-policy) and [use-case impact assessment](https://www.digital.gov.au/ai/ai-in-government-policy/ai-use-case-impact-assessment) | Agency governance is not a private-repository compliance certificate. This simulator is a fixed algorithmic experiment, not a trained AI decision system. Whether an adopting use is in scope needs actual assessment. | Covered agencies must apply their current policy, risk assessment and monitoring requirements. No agency determination is asserted here. |
| [Australian AI Ethics Principles](https://www.industry.gov.au/publications/australias-ai-ethics-principles) | These voluntary principles inform transparency, testing, human oversight, contestability and harm assessment. They are not presented as mandatory private-project law. | Real-world adoption needs context-specific evidence and the current implementation guidance, not a claim that synthetic accuracy certifies fairness. |
| [TGA population-based analytics guidance](https://www.tga.gov.au/resources/guidance/understanding-population-based-analytics-software-exclusion) | Actual intended purpose and features determine regulatory treatment. This design makes no individual disease predictions, triage decisions or treatment recommendations. | No TGA approval or software-exclusion ruling is claimed. Clinical functionality or supply for a changed purpose requires fresh regulatory assessment. |
| [NHMRC National Statement](https://www.nhmrc.gov.au/research-policy/ethics/national-statement-ethical-conduct-human-research) | No participants or real individual records are involved in this mathematical simulation. This is not an institutional exemption determination. | Institutional/funded research, people, real data or changed context require appropriate research-governance screening. |

Government, clinical and operational deployment are outside this prototype. Current source availability and any unresolved adopter-specific determinations must be addressed before such a use, rather than inferred from this assessment.

## Interpretation and residual harms

A strategy that improves an artificial average can still leave some requests waiting longer. Completed-only means can exclude the backlog and conceal unfinished work. Reports therefore keep waiting, in-service and completed cohorts separate, and label observation-horizon censoring explicitly. Simulated waiting exposure is not an estimate of unmet clinical need.

Equal scheduled resource minutes do not make calendars clinically interchangeable. Real services have skills, urgency, continuity, breaks, overtime rules, cancellations and constraints absent from this model. No simulated result justifies staff reductions, a funding decision, benefit denial or individual prioritisation. There are no demographic or Indigenous-community fairness claims. Any future community-specific work needs appropriate engagement and data governance.

## Source context

[AIHW elective surgery reporting](https://www.aihw.gov.au/hospitals/topics/elective-surgery) explains that completed-procedure waiting-time data do not describe all people currently waiting. The [2026 Report on Government Services, Public hospitals](https://www.pc.gov.au/ongoing/report-on-government-services/health/public-hospitals/) distinguishes additions, removals and waiting-time interpretation, with jurisdictional comparability caveats. These sources motivate honest denominators; this simulator does not reproduce their clinical measures or infer a real queue from published medians.
