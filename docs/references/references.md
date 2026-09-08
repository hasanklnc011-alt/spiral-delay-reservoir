# References

The DOI is the authoritative identifier for each entry. Author lists and titles
come from the project literature review
([`literature_review.md`](literature_review.md)) and DOI landing metadata; they
were **not independently re-verified** here. BibTeX: [`references.bib`](references.bib).

## A. Delay / feedback reservoirs

### Donati et al. (2024) — [10.1364/OE.514617](https://doi.org/10.1364/OE.514617)
Add-drop silicon microring with a through-port-to-add-port fiber feedback loop.
Memory is the combination of free-carrier / thermal inertia and an ~88 ns fiber
echo; masked input samples become virtual nodes; only a linear readout is
trained. Feedback is needed for 3-bit delayed-Boolean tasks.
**Used in this project for:** the delay-loop + linear-readout methodology and the
principle that a controllable *external* delay can supply memory that a bare
resonator cannot. Silicon carrier/thermal memory is explicitly **not** carried
over.

### Ren et al. (2024) — [10.1364/OE.518063](https://doi.org/10.1364/OE.518063)
A single nonlinear microring combined with a linear high-Q microring array to
raise memory capacity without a long fiber delay; evaluated on NARMA-10,
Mackey-Glass and Santa Fe, reporting fiber-feedback-like accuracy at ≥ 350×
smaller size. *Secondary reference* — full text was not obtained during the
project.
**Used in this project for:** context on compact on-chip memory; not a design
input.

## B. Single-ring limits and methodology

### Bazzanella et al. (2022) — [10.1109/JLT.2022.3183694](https://doi.org/10.1109/JLT.2022.3183694)
Feedback-free single silicon microring with time-multiplexed virtual nodes.
TPA-induced free-carrier dispersion and the thermo-optic effect give fading
memory and nonlinearity. Offline ridge regression. A single ring shows at most
~2 past bits of intrinsic linear memory. **Methodological rule:** the same
readout must also be applied to the input signal, or modulator/detector
artefacts can look like reservoir success.
**Used in this project for:** the control design — `same_delay_digital`,
`delayed_input`, and `no_photonic_core` all run through the identical readout —
and the expectation that a passive delay front end must *earn* its memory claim.

## C. Modelling precedent

### Giron Castro et al. (2024) — [10.1364/OE.509437](https://doi.org/10.1364/OE.509437)
Temporal coupled-mode theory for the cavity field `a(t)`, carrier density
`ΔN(t)` and temperature `ΔT(t)`, integrated with 4th-order Runge-Kutta; masked
1 GBd input, feedback waveguide, 50 virtual nodes; NARMA-10 with a ridge readout.
Identifies three regions in the power-detuning plane (linear/insufficient,
good coherent operation, self-pulsing/incoherent).
**Used in this project for:** the TCMT + RK4 modelling template and the
power/detuning operating-regime framing; the current line replaces carrier/thermal
terms with explicit delay + square-law detection.

## D. Recurrent photonic architectures (distinct)

### Tait et al. (2017) — [10.1038/s41598-017-07754-z](https://doi.org/10.1038/s41598-017-07754-z)
Broadcast-and-weight: WDM channels, programmable microring weight banks, balanced
photodetectors, MZM neurons; the physical circuit is shown to be dynamically
isomorphic to a continuous-time RNN `ds/dt = (W y − s)/τ + W_in u`. Here the
microring is a tunable weighting filter, not a nonlinear reservoir node.
**Used in this project for:** the explicit boundary statement — this is a
*trained physical RNN*, a different architecture, and this project does **not**
claim to have demonstrated one.

## E. Multi-ring / deep reservoirs (archived line)

### Dong et al. (2026) — [10.1016/j.optlastec.2025.114614](https://doi.org/10.1016/j.optlastec.2025.114614)
Three serial add-drop silicon microrings with inter-layer feedback; TCMT +
TPA/FCA/FCD/TO solved with RK4; all drop-port states combined in one linear
readout. NARMA-10 NMSE: 0.455 (1 ring), 0.103 (2 rings), 0.071 (3 rings).
**Used in this project for:** the closest architectural reference for the
**archived** three-ring NARMA work ([`../../archive/legacy_three_ring/`](../../archive/legacy_three_ring/));
not a current design input.

## Higher-level review (not present locally)

The project notes mention a 2026 review on *memory in integrated photonic neural
networks* (physical mechanisms → neuromorphic architectures) as a useful
high-level reference for photonic memory, volatile/fading memory, delay-based
memory, ring dynamics, and recurrent photonic architectures. **No copy is stored
in this repository**; it is cited by description only, and no copyrighted PDF is
redistributed here. If you have access, treat it as background reading for
Sections A–E above.
