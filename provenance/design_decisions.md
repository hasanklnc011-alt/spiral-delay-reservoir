# Design decisions

## ADR-001 — Preserve the P5/P6 separation

**Context:** a benchmark result and component physical evidence are different claims.  
**Alternatives:** tune the architecture using blind outcomes; keep the blind result locked.  
**Reason:** prevent benchmark leakage.  
**Evidence:** P5 result and P6 status records.  
**Consequences:** P6 may remain physically unaccepted while P5 remains reported.  
**Status:** accepted.

## ADR-002 — Archive the Blender file as a conceptual model

**Context:** the copied scene contains labelled architectural elements but no verified fabrication provenance.  
**Alternatives:** label it as a PIC layout; retain conceptual status.  
**Reason:** scientific honesty.  
**Evidence:** Blender inspection and absence of verified layout evidence.  
**Consequences:** colours and geometry are not presented as measured design parameters.  
**Status:** accepted.
