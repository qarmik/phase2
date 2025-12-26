Plain-English Record — GAP 1

Incident Boundary Freezing Artifact



Protocol Qv Rev 7.1



1\. What was attempted



The objective was to prevent incidents from being redefined after the fact.

Specifically, to ensure that once an AI-related incident is identified, the scope of what evidence belongs to that incident cannot be quietly expanded, narrowed, or reinterpreted later.



2\. What was actually built



A machine-verifiable Incident Boundary Freeze artifact was created.



This artifact:



Assigns a unique incident identifier.



Records a precise freeze timestamp.



Explicitly lists which evidence files are in scope.



Explicitly states that any evidence generated after the freeze is out of scope.



Anchors the entire boundary with a cryptographic hash.



The output is a deterministic JSON file stored under docs/incidents/.



3\. Why this matters in the real world



In audits and investigations, the most common manipulation is scope drift:



Evidence is added later to justify decisions.



Inconvenient logs are excluded retroactively.



Responsibility is reframed by redefining “what the incident really was.”



This artifact makes such manipulation detectable.

An auditor can verify exactly what was considered part of the incident at the time it was frozen.



4\. What went wrong or was unclear



Nothing failed technically.



However, this artifact does not decide what an incident should include.

It only freezes whatever scope is declared at the time of creation.

If the initial scope declaration is poor, that limitation is preserved, not corrected.



5\. What I can now explain out loud



What an “incident boundary” is.



When and how an incident becomes frozen.



Why evidence added later cannot be silently included.



How an auditor can verify the freeze independently.



6\. What remained unresolved at the end of the day



No automated severity assessment exists.



No rule exists yet for multi-system or cascading incidents.



Boundary freezing does not assign responsibility.



End-of-Day Synthesis (GAP 1)



What does Protocol Qv actually do?

It enforces a point in time beyond which the story of an incident cannot change unnoticed.



What can already be audited today?

That the incident scope was frozen, when it was frozen, and which evidence was included.



What is still aspirational?

Automated boundary definition and cross-incident linkage.

