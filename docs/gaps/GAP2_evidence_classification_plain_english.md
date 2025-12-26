Plain-English Record — GAP 2

Evidence Classification Schema



Protocol Qv Rev 7.1



1\. What was attempted



The objective was to prevent uncertainty from being quietly converted into “facts.”

Specifically, to ensure that all evidence used in an incident is clearly labeled as observed, inferred, or unknown.



2\. What was actually built



A deterministic Evidence Classification artifact was created.



For each piece of in-scope evidence, the artifact records:



A unique evidence identifier (hash-based).



The source file.



An evidence type:



Observed fact (directly recorded).



Inferred relation (derived by analysis).



Unknown (missing or ambiguous).



A short rationale for the classification.



An explicit tamper-risk assessment.



All evidence defaults to unknown unless explicitly justified otherwise.



3\. Why this matters in the real world



In regulatory disputes, the most dangerous move is implicit certainty:



Assumptions are presented as observations.



Analytical conclusions are treated as raw facts.



Missing data is ignored rather than acknowledged.



This artifact forces uncertainty to remain visible.

A regulator can immediately see what is known, inferred, or not known at all.



4\. What went wrong or was unclear



The classification is conservative by design.

As a result, early classifications may appear unhelpful because many items remain marked as “unknown.”



This is intentional.

Reclassification requires explicit justification and leaves an audit trail.



5\. What I can now explain out loud



The difference between an observed fact and an inference.



Why “unknown” is a protected state, not a failure.



How evidence can be reclassified without rewriting history.



Why absence of certainty is safer than false precision.



6\. What remained unresolved at the end of the day



No automated confidence scoring exists yet.



No standardized thresholds for reclassification are enforced.



Evidence classification does not yet drive escalation decisions.



End-of-Day Synthesis (GAP 2)



What does Protocol Qv actually do?

It prevents uncertainty from being silently erased in post-incident explanations.



What can already be audited today?

That every piece of evidence is explicitly typed and defaults to uncertainty unless proven otherwise.



What is still aspirational?

Automated reclassification rules and confidence-weighted aggregation.

