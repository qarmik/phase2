\# Canonical Scope — Protocol Qv Rev 7.1



This file delineates which parts of this repository are considered

\*\*canonical, audit-relevant artifacts\*\* under Protocol Qv Rev 7.1,

and which parts are \*\*supporting or experimental tooling\*\*.



\## Canonical (Audit-Relevant)



The following paths contain artifacts that may be cited in audits,

regulatory review, or incident reconstruction:



\- docs/incidents/

\- logs/

\- snapshot\_logs/

\- keys/

\- verification\_annotations.json

\- audit\_manifest\_\*.json

\- public\_timestamp.\*



Artifacts in these locations are:

\- deterministic

\- integrity-anchored

\- non-aspirational

\- forward-only



\## Supporting Tooling (Non-Canonical)



The following paths contain tooling used to generate or validate

canonical artifacts, but are not themselves audit records:



\- tools/

\- schemas/

\- tests/



Changes here do not retroactively affect existing incident records.



\## Experimental / Exploratory



The following paths contain exploratory or developmental work.

They do not represent enforced Protocol Qv controls unless explicitly

referenced by a canonical artifact:



\- fraud/

\- compliance\_\*.py

\- artifacts/

\- dist/

\- output/



Presence of code in these locations does not imply regulatory readiness.



\## Rule of Interpretation



If an artifact is not located in a Canonical path, it is not

authoritative evidence under Protocol Qv Rev 7.1.



