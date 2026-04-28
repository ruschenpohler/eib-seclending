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

The geographic distribution of financing constraints
(`outputs/figures/constraint_map.png`) aligns with textbook market-failure
geography: Southern and Eastern Europe (Cyprus, Greece, Croatia, Bulgaria,
Romania, Hungary, Portugal) report the highest shares of SMEs ranking access
to finance as their main obstacle, while Northern and Western Europe
(Denmark, Netherlands, Germany, Austria, Luxembourg, Sweden, Finland) report
the lowest. This validates the constraint measure as a plausible indicator of
financing-gap severity.

Time-series trends (`outputs/figures/timeseries.png`) show two notable
patterns. First, a pre-COVID inverse relationship: mean EIB intensity rose
steadily from 2015 to 2019 (peaking around InvestEU preparation) while mean
constraint severity fell steadily over the same period (ECB quantitative
easing, low interest rates). This inverse trend is consistent with the null
targeting regression — EIB lending grew even as financing gaps narrowed,
suggesting EIB responds to factors other than constraint severity. Second,
the 2020 co-movement (both EIB intensity and constraints spiked) illustrates
the confounding role of COVID-19, which the fixed-effects specification
absorbs only imperfectly. Country-level facets
(`outputs/figures/timeseries_byCountry.png`) show the same patterns for
selected member states.

The year-on-year scatter of changes in EIB intensity versus changes in
constraints (`outputs/figures/delta_scatter.png`) shows a weak positive
correlation (+0.215). Outliers are dominated by small-country volatility:
Slovenia 2016, for example, saw EIB per SME collapse by EUR 96,000 following
an anomalously large 2015 commitment (likely a single project), while
constraints fell independently. Conversely, Italy 2020 and Germany 2020 show
constraints spiking while EIB rose only modestly — the COVID credit crunch
overwhelmed EIB's counter-cyclical role. The scatter cannot discriminate
between targeting, growth confounds, and pandemic shocks; that is the purpose
of the regression specification.

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
null is robust across four first-order robustness checks (A1–C1): alternative
constraint intensity measure (Q0b mean score, p = 0.79), excluding 2020
(p = 0.43), high-income subsample (p = 0.42), and low-income subsample
(p = 0.23).

**Heterogeneity checks (B3 and B4).** Two additional splits test whether the
null masks heterogeneity across financially integrated vs. less integrated
markets, or across high vs. low constraint severity.

| Check | Sample | β | SE | p-value | N | Interpretation |
|---|---|---|---|---|---|---|
| B3 — Euro area | 19 countries | +2.58 | 4.15 | 0.543 | 112 | Null |
| B3 — Non-euro | 8 countries | +7.73 | 4.83 | 0.153 | 48 | Directionally larger, not significant |
| B3 — Interaction | Pooled | +6.74 | 5.38 | 0.221 | 160 | Euro vs. non-euro slope difference |
| B4 — High constraint | 14 countries | +4.00 | 3.07 | 0.215 | 83 | Null |
| B4 — Low constraint | 13 countries | +5.96 | 8.77 | 0.510 | 77 | Null, noisier |
| B4 — Interaction | Pooled | −2.12 | 7.90 | 0.791 | 160 | High vs. low slope difference |

The non-euro subsample coefficient is larger (+7.73 vs. +2.58 in the euro
area) and approaches significance (p = 0.15), consistent with the hypothesis
that EIB has a stronger targeting rationale where financial markets are less
integrated. However, the interaction term is not significant (p = 0.22), and
with only 8 non-euro countries the estimate is noisy. The constraint-level
split (B4) shows no meaningful difference: high-constraint and low-constraint
countries both yield null results. Overall, the null targeting result is
**robust to all six tested robustness and heterogeneity checks**.

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

### Potential extensions

The following extensions are discussed as promising directions for future
work. None is required for the current paper, but each addresses a limitation
identified during the analysis.

**1. Bayesian hierarchical models with partial pooling.**

A well-known limitation of country-level analysis is that small countries
(Luxembourg, Malta, Slovenia) have extreme per-SME volatility driven by one
or two projects, while large countries (Germany, France, Italy) have stable
estimates. A Bayesian hierarchical model with partial pooling would shrink
small-country estimates toward the EU mean in proportion to their uncertainty,
producing more reliable descriptive rankings and potentially tightening
regression estimates by borrowing strength across countries.

This methodology is well-suited to **firm-level analysis (Phase 2)** where
thousands of firms are nested in countries. In the aggregate country-level
analysis, the binding constraint is identification (Bartik IV) rather than
estimation noise, so partial pooling would improve prediction but not address
causal inference. See Gelman & Hill (2007) and the `bayesian-segmentation`
project for implementation patterns.

**2. EIB-internal data with finer geographic and sectoral granularity.**

Both the null targeting result and the weak Bartik instrument share a common
root cause: the public EIB Projects Financed dataset lacks sub-national
location (NUTS-2 coverage = 0%) and does not distinguish between direct and
intermediated operations at the project level beyond a coarse sector flag.
EIB-internal systems (e.g., the EIB Group Client Portal, project management
 databases) contain:

- **NUTS-2 or NUTS-3 region codes** for each project, enabling regional-level
  analysis with ~200+ regions rather than 27 countries;
- **Financing modality detail** (direct vs. intermediated vs. equity vs.
  guarantee), enabling a cleaner SME-specific lending intensity measure;
- **Beneficiary-level identifiers** (e.g., BvD ID, LEI) that would allow
  direct merge with EIBIS microdata or ORBIS without name-matching;
- **Pipeline data** (`projects to be financed`) that could test whether EIB
  targeting is forward-looking rather than contemporaneous.

Access to these internal data sources would require an EIB collaboration
agreement or secondment. The marginal return is high: NUTS-2 variation would
likely rescue the Bartik first-stage power (Fix A in Check 7), and
intermediated-operation filtering would align the numerator with the SME
denominator more precisely.

**3. EIBIS microdata for firm-level causal inference.**

The pre-registered core causal test is the Callaway-Sant'Anna staggered DiD
on EIBIS firm-level panel data (Spec 4). EIBIS contains ~12,000 firms across
EU-27 with survey waves 2016–2025, including indicators for EIB-supported
financing, green investment share, and firm characteristics (size, sector,
export status). Access requires a formal application to the EIB Economics
Department (typical timeline: 2–6 months). If approved, the analysis pipeline
is already stubbed in `src/analysis/cs_estimation.py` and can be executed
immediately. If denied, the current Phase 1 + Phase 2b results stand as a
complete paper on their own.

**4. Sectoral green-investment shift shares.**

An alternative Bartik shift construction would use EU-level green investment
growth by sector (from Eurostat or the IEA) as the shift variable, rather than
EIB sectoral lending. This would test whether regions with industrial
structures tilted toward fast-growing green sectors receive more EIB support.
However, this violates the exclusion restriction if green sector growth
affects firm green investment directly through industrial composition rather
than through the EIB lending channel. It is therefore a descriptive exercise,
not a causal instrument, but could be informative about EIB's thematic
alignment with the green transition.

## Phases

- **Phase 1** (public data): Market failure geography and EIB targeting consistency — descriptives, targeting regression, plausibility checks.
- **Phase 2b** (public data): Bartik IV on ECB SAFE financing constraints — aggregate causal claim using only publicly available data.
- **Phase 2** (EIBIS microdata): Callaway-Sant'Anna staggered DiD on firm-level green investment — the core behavioral additionality test.
- **Phase 3** (ORBIS, aspirational): Robustness with firm financial controls.

## License

TBD
