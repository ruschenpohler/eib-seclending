# EIB SME Intermediated Lending — Green Investment Additionality Evaluation

> "The EIB tags approximately 80% of its intermediated SME support as 'climate-aligned,' but the SME evaluation finds weak incentives for intermediaries to shift firm behavior. This project tests whether EIB climate-tagged lending actually changes firm green investment — or whether it merely relabels existing financial flows."

The empirical design was pre-registered before any data was downloaded, using Git's content-addressing as a lightweight but cryptographically verifiable pre-registration mechanism. All primary specifications, expected coefficient signs, and the primary/secondary designation for every estimating equation are committed at a fixed, publicly visible hash that cannot be altered retroactively.

This repository evaluates the behavioral additionality of EIB climate-tagged SME lending through three phases of increasing causal credibility: targeting consistency (Phase 1), aggregate reduced-form effects (Phase 2b), and firm-level causal effects (Phase 2). Phase 3 (firm financial controls via ORBIS) is aspirational and contingent on data access.

## Contribution relative to existing literature

Amamou et al. (2020) use propensity-score matching with difference-in-differences and find positive employment effects of EIB lending, but cannot address staggered adoption or test the green investment mechanism. Barbera et al. (2022) use a generalized propensity score for continuous treatment intensity but rely on the same matching identification. This project improves on both by (a) using the Callaway-Sant'Anna estimator to address the negative-weight problem under staggered treatment adoption, (b) using a Bartik instrument that exploits exogenous EU-level sectoral variation rather than firm-level matching on observables, and (c) testing the green investment additionality question — whether EIB climate-tagged lending changes firm behaviour or merely relabels existing flows — that neither paper examines.

## Repository structure

```
eib-seclending/
├── src/
│   ├── ingest/          # one file per data source
│   ├── analysis/        # one file per analysis step
│   └── viz/             # figure generation
├── outputs/
│   ├── figures/         # versioned deliverables
│   └── tables/          # versioned deliverables
├── data/                # gitignored — raw, interim, processed
├── notebooks/           # exploratory only
├── prespec-plan.md      # pre-registered specifications (write-once)
└── README.md            # this file
```

## Environment

This project uses `uv` for Python environment management.

```bash
# Setup (run once)
uv sync

# Run a script
uv run python src/ingest/eib_projects.py

# Run a notebook
uv run jupyter notebook
```

## Results

> **Pre-registered design.** All results below were specified before data access.
> Pre-analysis plan: [`f0313ba8ae0a293c36e2efbb581512e5c69cfbcd`](https://github.com/ruschenpohler/eib-seclending/blob/f0313ba8ae0a293c36e2efbb581512e5c69cfbcd/prespec-plan.md)
> · [Commit timestamp](https://github.com/ruschenpohler/eib-seclending/commit/f0313ba8ae0a293c36e2efbb581512e5c69cfbcd)

*Results will be populated as each phase completes. See `prespec-plan.md` for the full pre-registered specification of all four estimating equations.*

## Phases

- **Phase 1** (public data): Market failure geography and EIB targeting consistency — descriptives, targeting regression, plausibility checks.
- **Phase 2b** (public data): Bartik IV on ECB SAFE financing constraints — aggregate causal claim using only publicly available data.
- **Phase 2** (EIBIS microdata): Callaway-Sant'Anna staggered DiD on firm-level green investment — the core behavioral additionality test.
- **Phase 3** (ORBIS, aspirational): Robustness with firm financial controls.

## License

TBD
