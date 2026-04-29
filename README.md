# EIB SME Lending and Financing Constraints: Country-Level Evidence

EIB intermediated SME lending is premised on correcting financing market failures. Regions where SMEs face more severe financing obstacles should attract more EIB support, and that support should ease constraints. This project tests both claims using country-level panel data from the public EIB Projects dataset against a set of pre-registered analysis. Targeting regressions ask whether EIB per-SME lending is systematically higher where constraints are most acute. We find null results that survive several robustness checks and heterogeneity analysis. Employing a shift-share instrument, we ask whether exogenous variation in EIB sectoral exposure causally reduces those constraints but find the instrument to be weak at the country-level, and so we put little credence in these results. We caveat our findings by noting that because the EIB Projects data has no sub-national geographic codes, analysis is limited to 27 countries and statistical power low. We see a contribution in our use of Git's content-addressing as a lightweight but cryptographically verifiable pre-registration mechanism before data was accessed. All primary specifications, expected coefficient signs, and the primary/secondary designation for every estimating equation were committed at a fixed, publicly visible hash that cannot be altered retroactively. Planned extensions outlined towards the end (working with EIB-internal regional data or EIBIS microdata) would resolve these limitations. The extended analysis pipeline has already been set up and pre-registered.

## Results

> **Pre-registered design.** All results below were specified before data access.
> Pre-analysis plan: [`f0313ba8ae0a293c36e2efbb581512e5c69cfbcd`](https://github.com/ruschenpohler/eib-seclending/blob/f0313ba8ae0a293c36e2efbb581512e5c69cfbcd/prespec-plan.md)
> · [Commit timestamp](https://github.com/ruschenpohler/eib-seclending/commit/f0313ba8ae0a293c36e2efbb581512e5c69cfbcd)

### A note on statistical power

All regressions operate at the country level (EU-27 member states, roughly 120 to 160 observations). With 27 clusters, cluster-robust standard errors are noisy and wild cluster bootstrap is essential. The null targeting result and weak plausibility result may reflect thin variation as much as a true zero effect. Against this concern, descriptive patterns that align with basic theory provide face-validity reassurance that the data are not nonsensical. These patterns are highlighted below.

### Descriptive patterns

The geographic distribution of financing constraints (`outputs/figures/constraint_map.png`) aligns with textbook market-failure geography. Southern and Eastern Europe (Cyprus, Greece, Croatia, Bulgaria, Romania, Hungary, Portugal) report the highest shares of SMEs ranking access to finance as their main obstacle, while Northern and Western Europe (Denmark, Netherlands, Germany, Austria, Luxembourg, Sweden, Finland) report the lowest. This validates the constraint measure as a plausible indicator of financing-gap severity.

Time-series trends (`outputs/figures/timeseries.png`) show two notable patterns. First, a pre-COVID inverse relationship: mean EIB intensity rose steadily from 2015 to 2019 (peaking around InvestEU preparation) while mean constraint severity fell steadily over the same period (ECB quantitative easing, low interest rates). This inverse trend is consistent with the null targeting regression; EIB lending grew even as financing gaps narrowed, suggesting EIB responds to factors other than constraint severity. Second, the 2020 co-movement (both EIB intensity and constraints spiked) illustrates the confounding role of COVID-19, which the fixed-effects specification absorbs only imperfectly. Country-level facets (`outputs/figures/timeseries_byCountry.png`) show the same patterns for selected member states.

The year-on-year scatter of changes in EIB intensity versus changes in constraints (`outputs/figures/delta_scatter.png`) shows a weak positive correlation (+0.215). Outliers are dominated by small-country volatility. Slovenia 2016, for example, saw EIB per SME collapse by EUR 96,000 following an anomalously large 2015 commitment (likely a single project), while constraints fell independently. Conversely, Italy 2020 and Germany 2020 show constraints spiking while EIB rose only modestly; the COVID credit crunch overwhelmed EIB's counter-cyclical role. The scatter cannot discriminate between targeting, growth confounds, and pandemic shocks; that is the purpose of the regression specification.

As a supplementary descriptive, NUTS-2 region eligibility for EU cohesion funds was reconstructed from Eurostat GDP per capita in purchasing power standards using the official DG REGIO thresholds: less developed (below 75% of the EU-27 average), transition (75% to 90%), and more developed (above 90%). The reconstruction covers 258 NUTS-2 regions across all 27 member states for three programming periods. 248 reclassification events occurred across periods, confirming that the EU cohesion map is dynamic and that regional income convergence is an active process. The public EIB Projects dataset lacks NUTS-2 codes, so this variation is not exploited in the current analysis.

| Period | Less developed | Transition | More developed |
|---|---|---|---|
| 2007–2013 | 18 | 61 | 179 |
| 2014–2020 | 2 | 61 | 195 |
| 2021–2027 | 32 | 61 | 165 |

Data: `data/raw/cohesion_eligibility.csv`. Method: `src/ingest/cohesion_from_eurostat.py`.

### Does EIB lending target regions with worse financing constraints?

The pre-registered contemporaneous specification tests whether EIB lending per SME co-varies with the severity of financing constraints within country-year cells, controlling for GDP per capita, country fixed effects, year fixed effects, and a COVID-19 indicator:

$$\log(E_{rt}) = \beta \cdot C_{rt} + \gamma \cdot \log(G_{rt}) + \delta_r + \theta_t + D_{2020} + \varepsilon_{rt}$$

where $E_{rt}$ is EIB volume per SME, $C_{rt}$ is the constraint share, $G_{rt}$ is GDP per capita, and $D_{2020}$ is a COVID-19 indicator.

| Timing | β | SE | p-value | N | Finding |
|---|---|---|---|---|---|
| Contemporaneous | +3.48 | 3.41 | 0.316 | 160 | Null |
| Lagged (t−1) | −0.19 | 2.25 | 0.933 | 133 | Null |

Both coefficients are positive in the contemporaneous case and near-zero negative in the lagged case, but neither is statistically significant. Wild cluster bootstrap p-values (999 reps, Rademacher weights) confirm the null: contemporaneous p = 0.328, lagged p = 0.901. The null is robust across four first-order robustness checks: an alternative constraint intensity measure (Q0b mean score, p = 0.79), excluding 2020 (p = 0.43), a high-income subsample (p = 0.42), and a low-income subsample (p = 0.23).

#### Heterogeneity across market integration and constraint severity

Two additional splits test whether the null masks heterogeneity across financially integrated versus less integrated markets, or across high versus low constraint severity.

| Split | Sample | β | SE | p-value | N | Interpretation |
|---|---|---|---|---|---|---|
| Euro area | 19 countries | +2.58 | 4.15 | 0.543 | 112 | Null |
| Non-euro | 8 countries | +7.73 | 4.83 | 0.153 | 48 | Directionally larger, not significant |
| Interaction | Pooled | +6.74 | 5.38 | 0.221 | 160 | Euro vs. non-euro slope difference |
| High constraint | 14 countries | +4.00 | 3.07 | 0.215 | 83 | Null |
| Low constraint | 13 countries | +5.96 | 8.77 | 0.510 | 77 | Null, noisier |
| Interaction | Pooled | −2.12 | 7.90 | 0.791 | 160 | High vs. low slope difference |

The non-euro subsample coefficient is larger (+7.73 versus +2.58 in the euro area) and approaches significance (p = 0.15), consistent with the hypothesis that EIB has a stronger targeting rationale where financial markets are less integrated. However, the interaction term is not significant (p = 0.22), and with only 8 non-euro countries the estimate is noisy. The constraint-level split shows no meaningful difference; high-constraint and low-constraint countries both yield null results. Overall, the null targeting result is robust to all six tested robustness and heterogeneity checks.

There is no evidence that EIB lending per SME is higher where financing constraints are worse at the country level. This is a genuine finding, not a measurement artifact. Possible explanations include: (a) targeting occurs within countries (regional, sectoral, or project-level) and is washed out in aggregate; (b) EIB's mandate prioritises other dimensions (green investment, infrastructure, innovation) over financing-gap severity; (c) the country-level constraint measure is too coarse to detect targeting that responds to within-country variation.

### Do lagged EIB intensities predict subsequent SME outcomes?

A correlational test asks whether lagged EIB intensity predicts subsequent SME outcomes, conditioning on lagged constraints, GDP per capita, and fixed effects. Panel: 25 countries, 2016–2020 outcome years.

| Outcome | β (EIB intensity, t−1) | SE | p-value | Finding |
|---|---|---|---|---|
| Industry investment rate | −0.0004 | 0.0018 | 0.829 | Null |
| Firm entry rate | +0.0020 | 0.0014 | 0.170 | Weak positive, not significant |

The industry investment rate outcome is limited to NACE B+C+D+E (all firm sizes) because Eurostat does not report gross investment (V15110) at the SME size class. The firm entry rate uses size class GE10 (10 or more employees) because Eurostat does not provide a 0–249 size class in the business demography table. Both outcomes are winsorised at the 1st and 99th percentile. Cross-region placebo regressions (substituting leave-one-out average EIB intensity) yield null results, suggesting the weak entry-rate co-movement is country-specific rather than driven by a common eurozone factor. Wild cluster bootstrap p-values confirm the null: investment rate p = 0.600, entry rate p = 0.402.

We find no strong correlational evidence for a plausibility channel from EIB intensity to SME outcomes. The absence of a clear link is consistent with severe omitted-variable bias (EIB selects regions on unobservables), a true small effect, or coarse outcome measurement.

### Can the Bartik instrument identify aggregate causal effects?

#### Construction

The Bartik instrument is constructed exactly as pre-registered:

$$B_{rt} = \sum_j s_{jr,2015} \cdot L_{jt}$$

where $s_{jr,2015}$ is the employment share of country $r$ in sector $j$ (base year 2015) and $L_{jt}$ is EU-aggregate EIB lending in sector $j$ at time $t$.

Employment shares are from Eurostat SBS V16110 (persons employed), size classes 10–249 aggregated, base year 2015. EIB sectoral shifts are EU-aggregate signed amounts by NACE section and year from the EIB Projects Financed CSV, mapped via a manual crosswalk (`data/raw/eib_nace_crosswalk.csv`). Eleven NACE sections are common to both datasets (C, D, E, F, G, H, I, J, L, M, N).

#### First stage

$$\log(E_{rt}) = \pi \cdot B_{rt} + \gamma \cdot \log(G_{rt}) + \delta_r + \theta_t + D_{2020} + u_{rt}$$

| Coefficient | Estimate | SE | t | p | F-statistic |
|---|---|---|---|---|---|
| Bartik | 1.72×10⁻⁹ | 1.10×10⁻⁹ | 1.56 | 0.130 | **2.45** |

#### The instrument is too weak at the country level to support a causal claim

The first-stage Kleibergen-Paap F-statistic is 2.45, far below the conventional threshold of 10. This is a structural feature of working with only 27 geographic units; the Bartik shift-share design requires more granular variation to generate sufficient first-stage power. The public EIB Projects dataset contains no NUTS-2 codes, so regional-level analysis is not feasible with public data alone. Per the pre-registered protocol, the 2SLS second stage is not reported as causal. The instrument and code are documented and saved for use once regional-level data become available.

---

## Extensions and next steps

The null targeting result and the weak Bartik instrument share a common root: the public EIB dataset resolves only to the country level. Both limitations would be substantially addressed with either EIB-internal regional data or EIBIS microdata — and the analysis pipeline is already built for both. The extensions below represent the natural continuation of this work, not speculative additions.

#### EIB-internal data with NUTS-2 granularity

EIB-internal systems contain NUTS-2 or NUTS-3 region codes for each project, enabling analysis across roughly 200 regions rather than 27 countries. With that variation, the Bartik first stage would very likely clear the F > 10 threshold; NUTS-2 employment shares and project-level intermediated-operation flags would also align the numerator (EIB volume) with the SME denominator more precisely. Regional-level targeting regressions would test whether the null country-level result masks within-country variation — the most substantively important open question from the current analysis. Access would require an EIB collaboration agreement or secondment.

#### EIBIS microdata for firm-level causal inference

The pre-registered primary causal test is the Callaway-Sant'Anna staggered difference-in-differences on EIBIS firm-level panel data. EIBIS contains roughly 12,000 firms across EU-27 with survey waves 2016–2025, including indicators for EIB-supported financing, green investment share, and firm characteristics (size, sector, export status). Access requires a formal application to the EIB Economics Department (typical timeline: two to six months). If approved, the analysis pipeline is already stubbed in `src/analysis/cs_estimation.py` and can be executed immediately. This would be the first pre-registered, staggered-adoption DiD test of EIB green investment additionality.

#### Bayesian hierarchical models with partial pooling

A known limitation of country-level analysis is that small countries (Luxembourg, Malta, Slovenia) have extreme per-SME volatility driven by one or two projects. A Bayesian hierarchical model with partial pooling would shrink small-country estimates toward the EU mean in proportion to their uncertainty, producing more reliable descriptive rankings and potentially tightening targeting regression estimates by borrowing strength across countries (see Gelman and Hill, 2007).

#### Sectoral green-investment shift shares

An alternative Bartik construction would use EU-level green investment growth by sector (from Eurostat or the IEA) as the shift variable, rather than EIB sectoral lending volumes. This would test whether regions with industrial structures tilted toward fast-growing green sectors receive more EIB support. Because green sector growth also affects firm green investment directly through industrial composition, this is a descriptive exercise rather than a causal instrument — but it would be informative about EIB's thematic alignment with the green transition.

---

## Contribution relative to existing literature

Amamou et al. (2020) use propensity-score matching with difference-in-differences and find positive employment effects of EIB lending, but cannot address staggered adoption or test the green investment mechanism. Barbera et al. (2022) use a generalized propensity score for continuous treatment intensity but rely on the same matching identification. This project contributes in three respects: a pre-registered design that cannot be adjusted post-hoc (a methodological novelty for EIB evaluation work); a transparent diagnosis of why country-level public data cannot resolve targeting or causal identification (data literacy with an actionable remedy); and a ready-to-execute pipeline for the Callaway-Sant'Anna firm-level test that would be the first pre-registered causal estimate of EIB green investment additionality.

---

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
uv run jupy
