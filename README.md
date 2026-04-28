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

### A note on statistical power

All aggregate regressions in this project operate at the country level (EU-27
member states, ~120–160 observations). With 27 clusters, cluster-robust
standard errors are noisy and wild cluster bootstrap is essential. The null
targeting result and weak plausibility result may reflect thin variation as
much as a true zero effect. Against this concern, descriptive patterns that
align with basic theory provide face-validity reassurance that the data are not
nonsensical. These patterns are highlighted below.

### Phase 1 — Targeting consistency and plausibility

**Descriptive patterns (correlational, not causal).**

The geographic distribution of financing constraints (Figure 1) aligns with
textbook market-failure geography: Southern and Eastern Europe (Cyprus, Greece,
Croatia, Bulgaria, Romania, Hungary, Portugal) report the highest shares of
SMEs ranking access to finance as their main obstacle, while Northern and
Western Europe (Denmark, Netherlands, Germany, Austria, Luxembourg, Sweden,
Finland) report the lowest. This validates the constraint measure as a
plausible indicator of financing-gap severity.

Time-series trends (Figure 3) show two notable patterns. First, a pre-COVID
inverse relationship: mean EIB intensity rose steadily from 2015 to 2019
(peaking around InvestEU preparation) while mean constraint severity fell
steadily over the same period (ECB quantitative easing, low interest rates).
This inverse trend is consistent with the null targeting regression — EIB
lending grew even as financing gaps narrowed, suggesting EIB responds to
factors other than constraint severity. Second, the 2020 co-movement (both
EIB intensity and constraints spiked) illustrates the confounding role of
COVID-19, which the fixed-effects specification absorbs only imperfectly.

The year-on-year scatter of changes in EIB intensity versus changes in
constraints (Figure 2) shows a weak positive correlation (+0.215). Outliers
are dominated by small-country volatility: Slovenia 2016, for example, saw
EIB per SME collapse by EUR 96,000 following an anomalously large 2015
commitment (likely a single project), while constraints fell independently.
Conversely, Italy 2020 and Germany 2020 show constraints spiking while EIB
rose only modestly — the COVID credit crunch overwhelmed EIB's
counter-cyclical role. The scatter cannot discriminate between targeting,
growth confounds, and pandemic shocks; that is the purpose of the regression
specification.

**Targeting regression (Specification 1a/1b).**

The pre-registered contemporaneous specification tests whether EIB lending
per SME co-varies with the severity of financing constraints within
country-year cells, controlling for GDP per capita, country fixed effects,
year fixed effects, and a COVID-19 indicator:

    log(EIB_volume_per_SME) = β · constraint_share + γ · log(GDP_pc)
                              + country_FE + year_FE + COVID_2020 + ε

| Specification | β | SE | p-value | N | Finding |
|---|---|---|---|---|---|
| 1a — Contemporaneous | +3.48 | 3.41 | 0.316 | 160 | Null |
| 1b — Lagged (t−1) | −0.19 | 2.25 | 0.933 | 133 | Null |

Both coefficients are positive in the contemporaneous case and near-zero
negative in the lagged case, but neither is statistically significant. The
null is robust across four first-order robustness checks: alternative
constraint intensity measure (Q0b mean score, p = 0.79), excluding 2020
(p = 0.43), high-income subsample (p = 0.42), and low-income subsample
(p = 0.23). Additional heterogeneity checks (euro vs. non-euro; high vs. low
constraint countries) are logged for future work.

**Interpretation:** There is no evidence that EIB lending per SME is higher
where financing constraints are worse at the country level. This is a genuine
finding, not a measurement artifact. Possible explanations include: (a)
targeting occurs within countries (regional, sectoral, or project-level) and
is washed out in aggregate; (b) EIB's mandate prioritises other dimensions
(green investment, infrastructure, innovation) over financing-gap severity;
(c) the country-level constraint measure is too coarse to detect targeting
that responds to within-country variation.

**Plausibility check (Specification 2).**

A correlational test asks whether lagged EIB intensity predicts subsequent
SME outcomes, conditioning on lagged constraints, GDP per capita, and fixed
effects. Panel: 25 countries, 2016–2020 outcome years.

| Outcome | β (EIB intensity, t−1) | SE | p-value | Finding |
|---|---|---|---|---|
| Industry investment rate | −0.0004 | 0.0018 | 0.829 | Null |
| Firm entry rate | +0.0020 | 0.0014 | 0.170 | Weak positive, not significant |

The industry investment rate outcome is limited to NACE B+C+D+E (all firm
sizes) because Eurostat does not report gross investment (V15110) at the SME
size class. The firm entry rate uses size class GE10 (≥10 employees) because
Eurostat does not provide a 0–249 size class in the business demography table.
Both outcomes are winsorised at the 1st and 99th percentile. Cross-region
placebo regressions (substituting leave-one-out average EIB intensity) yield
null results, suggesting the weak entry-rate co-movement is country-specific
rather than driven by a common eurozone factor.

**Interpretation:** No strong correlational evidence for a plausibility
channel from EIB intensity to SME outcomes. The absence of a clear link is
consistent with severe omitted-variable bias (EIB selects regions on
unobservables), a true small effect, or coarse outcome measurement.

### Phase 2b — Bartik IV (aggregate causal claim)

**Construction.** The Bartik instrument is constructed exactly as
pre-registered:

    Bartik_rt = Σ_j (employment_share_jr,2015 × EIB_sectoral_lending_jt)

Employment shares are from Eurostat SBS V16110 (persons employed), size
classes 10–249 aggregated, base year 2015. EIB sectoral shifts are
EU-aggregate signed amounts by NACE section and year from the EIB Projects
Financed CSV, mapped via a manual crosswalk (`data/raw/eib_nace_crosswalk.csv`).
Eleven NACE sections are common to both datasets (C, D, E, F, G, H, I, J, L,
M, N).

**First stage.**

    log(EIB_per_SME) = π · Bartik + controls + country_FE + year_FE + u

| Coefficient | Estimate | SE | t | p | F-statistic |
|---|---|---|---|---|---|
| Bartik | 1.72×10⁻⁹ | 1.10×10⁻⁹ | 1.56 | 0.130 | **2.45** |

**Critical finding: F = 2.45, far below the conventional F > 10 threshold.**
The instrument is too weak at the country level to support a causal claim.
This is a structural feature of analysis with only 27 geographic units — the
Bartik shift-share design requires more granular variation (NUTS-2 regions or
firm-level bins) to generate sufficient first-stage power. The EIB Projects
Financed public dataset contains no NUTS-2 codes, so Fix A (NUTS-2 level) is
not available. Fix B (firm-level variation via EIBIS microdata) requires data
access not yet secured.

**Decision:** Accept the weak instrument. The 2SLS second stage is not
reported as causal. Phase 2b is documented (instrument saved, code committed,
results logged) but does not produce a pre-registered causal estimate. The
fallback is to rely on Phase 1 (descriptive targeting evidence) and Phase 2
(firm-level Callaway-Sant'Anna) for causal inference.

**For future work:** Do not tweak instrument construction to chase a higher
F-statistic — that would be specification searching. Instead, add more
geographic units (NUTS-2 from ORBIS/EIBIS microdata) or more granular
dimensions (firm size bins within countries). Both require data not currently
available.

## Phases

- **Phase 1** (public data): Market failure geography and EIB targeting consistency — descriptives, targeting regression, plausibility checks.
- **Phase 2b** (public data): Bartik IV on ECB SAFE financing constraints — aggregate causal claim using only publicly available data.
- **Phase 2** (EIBIS microdata): Callaway-Sant'Anna staggered DiD on firm-level green investment — the core behavioral additionality test.
- **Phase 3** (ORBIS, aspirational): Robustness with firm financial controls.

## License

TBD
