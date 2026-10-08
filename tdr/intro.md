# Targeted Detectability Range

This tutorial develops the **Targeted Detectability Range (TDR)** from first
principles, then follows the method in Ronchini et al. and walks through the
public [`gw_tdr` pipeline](https://github.com/samueleronchini/gw_tdr).

The TDR answers a conditional question:

> Given what an electromagnetic or other external messenger tells us about a
> possible compact-binary source, how far away could that source be and still
> be detectable by the gravitational-wave detector network?

It is a rapid, source-informed sensitivity estimate—not a replacement for a
coherent gravitational-wave search, a search ranking statistic, a false-alarm
rate, or a formal exclusion analysis.

## Learning path

1. [GW signals, detection, and the paper](01_gw_and_paper.ipynb): compact
   binaries, waveforms, noise and PSDs, matched filtering, SNR, significance,
   template banks, and the paper's definition and validation of TDR.
2. [From the repository to source-informed TDR](02_tdr_priors.ipynb): follow
   the pipeline, explore sky localization and inclination/mass dependence,
   compare source-prior choices, and complete coding exercises.

The first notebook develops the concepts and uses PyCBC for its antenna
response example. The second notebook runs the **production `gw_tdr` code**
for GRB 200228A (`bn200228291`) using the real Fermi/GBM HEALPix localization
and public GWOSC O3b strain. The paper identifies this as the O3 GRB with the
largest \(D_{90}^{\rm TDR}\) and uses it for the TDR-map example. It needs a
Python 3.11+ kernel with the GW-analysis dependencies **and the local
`gw_tdr` repository installed editably in that same environment**, plus
internet access to the Fermi/HEASARC and GWOSC archives.

## Paper and implementation

- Ronchini et al., “Gravitational-wave detectability range informed by
  external messengers,” *Astronomy & Astrophysics* (2026):
  [arXiv:2605.21578](https://arxiv.org/abs/2605.21578). Figure 6 identifies
  GRB 200228291 as the sample's highest-\(D_{90}^{\rm TDR}\) event; its
  localization is provided by
  [Fermi/GBM GCN 27247](https://gcn.nasa.gov/circulars/27247).
- Source code: [`samueleronchini/gw_tdr`](https://github.com/samueleronchini/gw_tdr).
- To run the production pipeline, follow the repository's installation guide
  and install it in editable mode (`python -m pip install -e /path/to/gw_tdr`)
  using the notebook kernel's environment. In VS Code, explicitly select the
  Python 3.11+ TDR environment and restart the kernel before running cells.
  `ModuleNotFoundError: gwosc` means the active environment lacks a dependency;
  `ModuleNotFoundError: targ_ac_git` means the local repository is not installed
  in that environment. The second
  notebook documents the full run, public-data access, generated output files,
  and the real functions behind each analysis step.

## Scope of priors in the current public code

The command-line pipeline accepts either a fixed sky position or a HEALPix
sky-probability map. Its inclination option is an **isotropic prior truncated
to a chosen interval**. It evaluates a small, fixed grid of BNS and NSBH
masses. It does not currently accept an arbitrary source-posterior file or an
arbitrary mass posterior. The notebook compares inclination intervals using
the production range function, demonstrates its sky-map interface, and
identifies the production functions that would need extending for correlated
source-posterior samples.

For the isotropic truncated inclination prior, sample uniformly in
\(\cos\iota\), not uniformly in \(\iota\). If external data constrain
inclination, use the conditional posterior (or a physically justified
truncation); do not silently treat a jet opening angle as an exact viewing
angle.
