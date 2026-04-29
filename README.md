# EIB SME Lending and Financing Constraints: Country-Level Evidence

## Abstract

EIB intermediated SME lending is premised on correcting financing market failures. Regions where SMEs face more severe financing obstacles should attract more EIB support, and that support should ease constraints. This project tests both claims using country-level panel data from the public EIB Projects dataset against pre-registered specifications. Targeting regressions ask whether EIB per-SME lending is systematically higher where constraints are most acute. We find null results that survive several robustness checks and heterogeneity analysis. Employing a shift-share instrument, we ask whether exogenous variation in EIB sectoral exposure causally reduces those constraints but find the instrument to be weak at the country-level, and so we put little credence in these results. We caveat our findings by noting that because the EIB Projects data has no sub-national geographic codes, analysis is limited to 27 countries and hence statistical power low. Planned extensions outlined towards the end (working with EIB-internal regional data or EIBIS microdata) would resolve these limitations, and the needed analysis pipeline has already been set up and pre-registered. A further contribution is our use of Git's content-addressing as a lightweight but cryptographically verifiable pre-registration mechanism before data access. All primary specifications, expected coefficient signs, and the primary/secondary designation for every estimating equation, including analysis extensions, were committed at a fixed, publicly visible hash that cannot be altered retroactively.

## Results

> **Pre-registered design.** All results below were specified before data access.
> Pre-analysis plan: [`f0313ba8ae0a293c36e2efbb581512e5c69cfbcd`](https://github.com/ruschenpohler/eib-seclending/blob/f0313ba8ae0a293c36e2efbb581512e5c69cfbcd/prespec-plan.md)
> · [Commit timestamp](https://github.com/ruschenpohler/eib-seclending/commit/f0313ba8ae0a293c36e2efbb581512e5c69cfbcd)

### Constraint geography and macro co-movement

With regressions confined to 27 EU member state clusters, the raw patterns in the data carry extra weight as a face-validity check.

![](outputs/figures/constraint_map.png)
*Figure 1: Financing constraint severity by country, 2015–2021 mean (ECB SAFE). Constraint shares are highest in Southern and Eastern Europe and lowest in Northern and Western Europe — consistent with well-documented differences in financial market development.*

The geographic distribution of financing constraints aligns with textbook market-failure geography: Southern and Eastern Europe (Cyprus, Greece, Croatia, Bulgaria, Romania, Hungary, Portugal) report the highest shares of SMEs ranking access to finance as their main obstacle, while Northern and Western Europe (Denmark, Netherlands, Germany, Austria, Luxembourg, Sweden, Finland) report the lowest. This validates the constraint measure as a plausible indicator of financing-gap severity.

![](outputs/figures/timeseries.png)
*Figure 2: Mean EIB lending intensity and financing constraint share, EU-27 averages 2015–2021. Both series decline in parallel through 2018 then co-spike in 2020, consistent with a shared macro driver rather than EIB responding specifically to constraint severity.*

Time-series trends show two notable patterns. First, a parallel pre-COVID decline: both mean EIB intensity and mean constraint severity fell from 2015 to 2018, then partly recovered into 2019. The co-movement is consistent with both series responding to the same macroeconomic driver — falling interest rates and ECB quantitative easing reduced financing constraints while also compressing demand for intermediated EIB credit — rather than EIB responding specifically to constraint severity. This shared macro sensitivity is consistent with the null targeting result. Second, the 2020 co-movement (both EIB intensity and constraints spiked) illustrates the confounding role of COVID-19, which the fixed-effects specification absorbs only imperfectly. Country-level facets show the same patterns for selected member states.

![](outputs/figures/delta_scatter.png)
*Figure 3: Year-on-year changes in EIB lending intensity versus financing constraints, 131 country-year observations 2016–2021 (r = +0.215). Outliers reflect single-project small-country volatility; the 2020 COVID shock drives the upper-half cluster.*

The year-on-year scatter of changes in EIB intensity versus changes in constraints shows a weak positive correlation (r = +0.215). Outliers are dominated by small-country volatility: Slovenia 2016 saw EIB per SME collapse by EUR 96,000 following an anomalously large 2015 commitment (likely a single project), while constraints fell independently. Italy 2020 and Germany 2020 show constraints spiking while EIB rose only modestly; the COVID credit crunch overwhelmed EIB's counter-cyclical role. The scatter cannot discriminate between targeting, growth confounds, and pandemic shocks; that is the purpose of the regression specification.

### Does EIB lending target regions with worse financing constraints?

All regressions operate on at most 160 country-year observations across 27 EU member state clusters. With so few clusters, cluster-robust standard errors are unreliable; wild cluster bootstrap (WCB — 999 reps, Rademacher weights) is used throughout.

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

Overall, there is no evidence that EIB lending per SME is higher where financing constraints are worse at the country level. Several robustness checks and heterogeneity analyses suggest, this may be a genuine finding, and not merely a measurement artifact. However, there are a number of alternative explanations this analysis cannot distinguish, including:

1. Targeting occurs within countries (regional, sectoral, or project-level) and is washed out in aggregate
2. EIB's mandate prioritises other dimensions (green investment, infrastructure, innovation) over financing-gap severity
3. The country-level constraint measure is too coarse to detect targeting
4. With only 27 clusters, limited statistical power cannot be excluded as a partial explanation; the NUTS-2 extension would directly address this.

### Do lagged EIB intensities predict subsequent SME outcomes?

A correlational test asks whether lagged EIB intensity predicts subsequent SME outcomes, conditioning on lagged constraints, GDP per capita, and fixed effects. Panel: 25 countries, 2016–2020 outcome years.

| Outcome | β (EIB intensity, t−1) | SE | p-value | Finding |
|---|---|---|---|---|
| Industry investment rate | −0.0004 | 0.0018 | 0.829 | Null |
| Firm entry rate | +0.0020 | 0.0014 | 0.170 | Weak positive, not significant |

The industry investment rate outcome is limited to NACE B+C+D+E (all firm sizes) because Eurostat does not report gross investment (V15110) at the SME size class. The firm entry rate uses size class GE10 (10 or more employees) because Eurostat does not provide a 0–249 size class in the business demography table. Both outcomes are winsorised at the 1st and 99th percentile. Cross-region placebo regressions (substituting leave-one-out average EIB intensity) yield null results, suggesting the weak entry-rate co-movement is country-specific rather than driven by a common eurozone factor. Wild cluster bootstrap p-values confirm the null: investment rate p = 0.600, entry rate p = 0.402.

We find no strong correlational evidence for a plausibility channel from EIB intensity to SME outcomes. The absence of a clear link is consistent with severe omitted-variable bias (EIB selects regions on unobservables), a true small effect, or coarse outcome measurement.

### Can we exploit exogeneity in shifts to identify aggregate causal effects?

The targeting regressions show no within-country-year association between EIB intensity and constraint severity. But OLS is uninformative on the causal question of whether EIB lending reduces financing constraints because reverse causality and common macroeconomic shocks both confound the estimate. We therefore turn to a shift-share instrument, following Borusyak, Hull, and Jaravel (2022). We posit that EU-aggregate EIB commitments are set by EIB-board portfolio decisions *at the level of a sector* (i.e., energy transition, infrastructure, innovation priorities) and *across the EU as a whole* and are hence plausibly exogenous to any individual country's financing conditions. Countries inherit differential EIB exposure depending on whether their pre-existing industrial structure happened to be concentrated in sectors that subsequently received large EU-level commitments.

#### Construction

The shift-share instrument is constructed exactly as pre-registered:

$$B_{rt} = \sum_j s_{jr,2015} \cdot L_{jt}$$

where $s_{jr,2015}$ is the employment share of country $r$ in sector $j$ (base year 2015) and $L_{jt}$ is EU-aggregate EIB lending in sector $j$ at time $t$.

Employment shares are from Eurostat SBS V16110 (persons employed), size classes 10–249 aggregated, base year 2015. EIB sectoral shifts are EU-aggregate signed amounts by NACE section and year from the EIB Projects Financed CSV, mapped via a manual crosswalk (`data/raw/eib_nace_crosswalk.csv`). Eleven NACE sections are common to both datasets (C, D, E, F, G, H, I, J, L, M, N).

#### First stage

$$\log(E_{rt}) = \pi \cdot B_{rt} + \gamma \cdot \log(G_{rt}) + \delta_r + \theta_t + D_{2020} + u_{rt}$$

| Coefficient | Estimate | SE | t | p | F-statistic |
|---|---|---|---|---|---|
| Shift-share | 1.72×10⁻⁹ | 1.10×10⁻⁹ | 1.56 | 0.130 | **2.45** |

#### The instrument is too weak at the country level to support a causal claim

The first-stage Kleibergen-Paap F-statistic is 2.45, far below the conventional threshold of 10. This is a structural feature of working with only 27 geographic units as a shift-share design requires more granular variation to generate sufficient first-stage power. The public EIB Projects dataset contains no NUTS-2 codes, so regional-level analysis is not feasible with public data alone. Per the pre-registered protocol, the 2SLS second stage is not reported as causal. The instrument and code are documented and saved for use once regional-level data become available.

---

## Extensions and next steps

The null targeting result and the weak shift-share instrument share a common root: the public EIB dataset resolves only to the country level. Both limitations would be substantially addressed with either EIB-internal regional data or EIBIS microdata — and the analysis pipeline is already built for both. The extensions below represent the natural continuation of this work, not speculative additions.

#### EIB-internal data with NUTS-2 granularity

EIB-internal systems contain NUTS-2 or NUTS-3 region codes for each project, enabling analysis across roughly 200 regions rather than 27 countries. With that variation, the shift-share first stage could plausibly clear the F > 10 threshold. NUTS-2 employment shares and project-level intermediated-operation flags would also align the numerator (EIB volume) with the SME denominator more precisely. Regional-level targeting regressions would test whether the null country-level result masks within-country variation — the most substantively important open question from the current analysis. Access would require an EIB collaboration agreement or secondment.

#### EIBIS microdata for firm-level causal inference

The pre-registered primary causal test is the Callaway-Sant'Anna staggered difference-in-differences on EIBIS firm-level panel data. EIBIS contains roughly 12,000 firms across EU-27 with survey waves 2016–2025, including indicators for EIB-supported financing, green investment share, and firm characteristics (size, sector, export status). Access requires a formal application to the EIB Economics Department (typical timeline: two to six months). If approved, the analysis pipeline is already stubbed in `src/analysis/cs_estimation.py` and can be executed immediately. This would be the first pre-registered, staggered-adoption DiD test of EIB green investment additionality.

#### Bayesian hierarchical models with partial pooling

A known limitation of country-level analysis is that small countries (Luxembourg, Malta, Slovenia) have extreme per-SME volatility driven by one or two projects. A Bayesian hierarchical model with partial pooling would shrink small-country estimates toward the EU mean in proportion to their uncertainty, producing more reliable descriptive rankings and potentially tightening targeting regression estimates by borrowing strength across countries (see Gelman and Hill, 2007).

#### Sectoral green-investment shift shares

An alternative shift-share construction would use EU-level green investment growth by sector (from Eurostat or the IEA) as the shifter, rather than EIB sectoral lending volumes. This would test whether regions with industrial structures tilted toward fast-growing green sectors receive more EIB support. Because green sector growth also affects firm green investment directly through industrial composition, this is a more descriptive exercise rather than a causal instrument, but it would be informative about EIB's thematic alignment with the green transition.

---

## Contribution relative to existing literature

Amamou, Gereben, and Wolski (2020) use propensity-score matching with difference-in-differences and find positive employment and investment effects of EIB intermediated lending, but cannot address staggered adoption or test the green investment mechanism. Barbera, Gereben, and Wolski (2022) estimate heterogeneous treatment effects using a generalized propensity score for continuous treatment intensity, again finding positive employment and investment effects, but rely on the same matching identification strategy. This project contributes in three respects: a pre-registered design that cannot be adjusted post-hoc (a methodological novelty for EIB evaluation work); a transparent diagnosis of why country-level public data cannot resolve targeting or causal identification (data literacy with an actionable remedy); and a ready-to-execute pipeline for the Callaway and Sant'Anna (2021) staggered difference-in-differences estimator that, once EIBIS access is granted, would yield the first pre-registered causal estimate of EIB green investment additionality.

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

Managed with `uv`. Reproduce with:

```bash
uv sync
uv run python src/analysis/<script>.py
```

---

## References

Amamou, R., Gereben, Á., & Wolski, M. (2020). Making a difference: Assessing the impact of the EIB's funding to SMEs. *EIB Working Paper 2020/04*, European Investment Bank.

Barbera, A., Gereben, Á., & Wolski, M. (2022). Estimating conditional treatment effects of EIB lending to SMEs in Europe. *EIB Working Paper 2022/03*, European Investment Bank. Also published as *BIS Working Papers* 1006.

Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. *The Review of Economic Studies*, 89(1), 181–213.

Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.

Gelman, A., & Hill, J. (2007). *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge University Press.
