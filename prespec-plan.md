# Pre-Analysis Plan
## EIB SME Intermediated Lending — Green Investment Additionality Evaluation

Committed prior to any data download or inspection.
Verification: see commit hash linked in README.

---

## Research question

The European Investment Bank (EIB) classifies approximately 80% of its
intermediated SME support as climate-aligned. Whether this tagging reflects
genuine behavioral change at the firm level — or merely relabels financial
flows that would have occurred anyway — is an open empirical question.

This plan pre-registers four specifications that test the question at
increasing levels of causal credibility. The four form a logical chain,
not parallel checks of the same estimand:

**Specifications 1 and 2** are descriptive and correlational. They ask
whether EIB lending is directed at regions where market failures are worst
(targeting consistency) and whether aggregate EIB exposure co-moves with
subsequent SME outcomes. Neither carries a causal claim.

**Specification 3** makes a causal claim at the aggregate level. It asks
whether exogenous variation in regional EIB exposure — instrumented by
predetermined industrial structure interacted with EU-level EIB sectoral
allocation shifts — reduces aggregate SME financing constraints. This is
the market-failure mechanism test.

**Specification 4** makes a causal claim at the firm level. It asks whether
receiving EIB-supported financing causes an individual firm to invest a
larger share of its capital expenditure in green activities. This is the
behavioral additionality test.

**How results connect.** Genuine thematic additionality requires evidence at
all steps: EIB targets constrained regions (Specification 1), aggregate
exposure alleviates financing constraints (Specification 3), and supported
firms increase green investment (Specification 4). Gaps between steps carry
their own interpretation. A positive Specification 3 result without a
Specification 4 effect would suggest EIB reduces aggregate constraints but
supported firms do not redirect freed-up finance toward green investment —
consistent with financial but not thematic additionality. A positive
Specification 4 effect without a Specification 3 signal would suggest the
firm-level effect operates through channels other than aggregate constraint
relief (certification, signaling, or direct co-financing). A null targeting
result in Specification 1 does not preclude additionality: EIB could achieve
firm-level green investment effects even without directing more lending toward
the most constrained regions. A null Specification 1 paired with a positive
Specification 2 co-movement result would suggest EIB lending aligns with
growth opportunities rather than financing gaps — inefficient targeting but
a potentially active lending channel.

A null result in any specification does not by itself constitute evidence of
relabeling — it could also reflect low statistical power, effects operating
through channels not captured by the chosen outcome, or measurement
limitations. Interpretation of null results must weigh these alternatives
explicitly. All output tables must label results as "correlational" or
"causal" consistently with the identification strategy of the relevant
specification.

**Significance level and inference.** All pre-registered specifications are
tested at α = 0.05, two-sided. The four specifications test distinct estimands
at distinct levels of identification; no multiple testing correction is applied
because they are not repeated tests of the same hypothesis. Wild cluster
bootstrap p-values (Webb 6-point weights, 10,000 replications) are the
preferred basis for inference where cluster counts fall below 40; analytic
cluster-robust standard errors are reported alongside.

---

## Pre-registered specifications

### Specification 1 — Targeting consistency

**Question:** Does EIB lending volume per SME increase with the severity of
SME financing constraints at the regional level, after controlling for income
and fixed effects?

**Estimating equation:**

$$\log(\text{EIB\_volume\_per\_SME}_{rt}) = \alpha + \beta \cdot \text{constraint}_{rt} + \gamma \cdot \log(\text{GDP\_pc}_{rt}) + \delta_r + \theta_t + \varepsilon_{rt}$$

where $r$ = country or NUTS-2 region, $t$ = year, $\delta_r$ = region fixed
effects, $\theta_t$ = year fixed effects.

**Variables:**
- LHS: log EIB signed commitments per SME enterprise (EUR at contract date;
  enterprise count from Eurostat SBS V11110, size 10–249)
- $\text{constraint}_{rt}$: share of SMEs reporting access to finance as
  their main obstacle to investment, measured contemporaneously with EIB
  volume (constraint survey year = EIB signature year). A lagged
  specification ($\text{constraint}_{r,t-1}$) is a pre-designated robustness
  check.
- $\text{GDP\_pc}_{rt}$: GDP per capita at current prices, EUR (Eurostat
  `nama_10_pc`, variable CP\_EUR\_HAB)

**Inference:** SEs clustered at country level; wild cluster bootstrap
alongside analytic SEs.

**Expected sign:** $\beta > 0$.

**Pre-registered pass criterion:** $\beta$ positive and statistically
significant at α = 0.05. A negative or zero $\beta$ is a substantively
important finding requiring careful interpretation before outputs are written.

**Identification note:** Constraint and EIB volume are measured
contemporaneously. This specification cannot distinguish whether EIB
systematically targets regions with pre-existing constraint severity from
whether EIB lending responds to contemporaneous conditions in the same
year. The lagged constraint robustness check ($t-1$) partially addresses
this: if it produces a similar estimate, simultaneity is a less likely
explanation.

**Pre-designated robustness (secondary, not pre-registered):** Replace the
LHS with log(EIB\_total\_volume / GDP\_pc\_{rt}), where GDP\_pc is Eurostat
`nama_10_pc` CP\_EUR\_HAB at current prices. This checks whether the
per-SME enterprise denominator drives the result.

---

### Specification 2 — Aggregate co-movement (correlational)

**Question:** Does lagged regional EIB lending intensity co-move with
subsequent SME investment rates, after conditioning on constraint severity
and fixed effects?

**Estimating equation:**

$$\text{Outcome}_{rt} = \alpha + \beta \cdot \text{EIB\_intensity}_{r,t-1} + \gamma \cdot \text{constraint}_{r,t-1} + \phi \cdot \log(\text{GDP\_pc}_{rt}) + \delta_r + \theta_t + \varepsilon_{rt}$$

**Temporal alignment:** $t-1$ = EIB signature year and constraint survey
year; $t$ = outcome year. Example: 2019 EIB intensity and 2019 constraint
→ 2020 investment rate. GDP per capita enters at $t$ because it controls
for concurrent economic conditions affecting the outcome, not the treatment
channel.

**Primary outcome:** SME investment rate — gross investment in tangible
goods divided by value added at factor cost (Eurostat SBS V15110 / V12110,
size 10–249, country×year), winsorized at the 1st and 99th percentile.
Designated primary because it is the most direct aggregate analogue of
the green investment behavior at issue.

**Secondary outcome (exploratory, not pre-registered):** firm entry rate
(Eurostat business demography, size 0–249). Designated exploratory because
firm entry is a less direct proxy for the green investment channel.

**Inference:** same as Specification 1.

**Expected sign:** $\beta > 0$.

**Interpretation:** This is a correlational test only; omitted variable bias
is unresolved. Co-movement in the expected direction is consistent with the
EIB lending channel being active. A null result indicates that lagged EIB
intensity does not predict subsequent SME investment rates; this could
reflect no effect, insufficient power, or noise in the outcome measure.
All outputs labelled: "correlational — not causal."

---

### Specification 3 — Aggregate causal effect on financing constraints

**Question:** Does exogenous variation in regional EIB lending exposure
reduce aggregate SME financing constraints?

**Instrument construction:**

$$\text{Bartik}_{rt} = \sum_j \left( \text{employment\_share}_{jr,0} \times \text{EIB\_sectoral\_lending}_{jt} \right)$$

where $j$ = NACE 2-digit sector; employment shares are from Eurostat SBS
(V16110: persons employed, or V13110: employees) at NACE 2-digit × country,
size 10–249, fixed at base year $t_0 = 2015$ (or the earliest year with
≥80% sector coverage per country, logged as a deviation from this plan);
and $\text{EIB\_sectoral\_lending}_{jt}$ is EU-aggregate EIB signed volume
by sector and year — set at the institutional level by the EIB Board and
not determined by conditions in any single region. Shares and shifts enter
the instrument in levels.

**Pre-registered headline result:** 2SLS. The causal claim rests on the
instrument; OLS is reported as a secondary result only.

**Estimating equations:**

First stage:
$$\text{EIB\_volume\_per\_SME}_{rt} = \pi \cdot \text{Bartik}_{rt} + \gamma \cdot \log(\text{GDP\_pc}_{rt}) + \delta_r + \theta_t + u_{rt}$$

where EIB\_volume\_per\_SME\_{rt} is EIB signed commitments per SME
enterprise (EUR at contract date, levels).

Second stage:
$$\text{constraint}_{rt} = \beta \cdot \widehat{\text{EIB\_volume\_per\_SME}}_{rt} + \gamma \cdot \log(\text{GDP\_pc}_{rt}) + \delta_r + \theta_t + \varepsilon_{rt}$$

**Pass criterion for second stage:** Kleibergen-Paap rk Wald F-statistic
(cluster-robust) > 10. The standard non-clustered F is not reported because
it ignores within-country correlation. If F < 10, the second stage is not
reported and no causal claim is made for the market-failure mechanism.
The research question is then addressed by Specifications 1 and 4 alone.

**Expected sign:** $\beta < 0$ (higher EIB exposure reduces the financing
constraint share).

**Inference:** wild cluster bootstrap; analytic SEs reported alongside.

**Validity failure rule:** If the pre-registered Bartik exclusion restriction
test returns a significant residual correlation (p < 0.10), the instrument
is invalid. The 2SLS result is not reported as causal; OLS is reported
with an explicit note that the exclusion restriction is violated.

**Note on scope:** Specification 3 estimates the effect of regional EIB
sectoral exposure on aggregate financing constraints. Specification 4
estimates the effect of firm-level EIB receipt on green investment share.
These are different estimands, populations, and outcomes — their
coefficients cannot be directly compared. The outcome in Specification 3
(financing constraint share) reflects a reduction in the market failure
EIB aims to address; the outcome in Specification 4 (green investment
share) reflects whether firms redirect freed-up finance toward EIB's
thematic objective. A positive Specification 3 result without a positive
Specification 4 result would suggest financial additionality without
thematic additionality — the central concern about mere relabeling.

---

### Specification 4 — Firm-level causal effect on green investment

**Question:** Does receiving EIB-supported financing cause an individual
firm to invest a larger share of its capital expenditure in green
activities?

**Sample:** All EIBIS panel firms with at least two observed survey waves,
at least one pre-treatment wave, and non-missing values on `eib_support`,
`green_inv_share`, `country`, `nace2`, and `size_class`. Firms observed
in only one wave cannot contribute a pre-treatment period to the estimator
and are excluded; their number and characteristics are reported in the
sample balance table for reference.

**Treatment definition:** first survey wave in which firm $i$ reports
EIB-supported financing ($\text{eib\_support}_{it} = 1$). Treatment is
absorbing.

**Pre-registered primary specification:** Sun & Abraham (2021)
interaction-weighted estimator, not-yet-treated comparison group, overall
ATT aggregation. No covariates in the primary specification; identification
relies on parallel trends between treated and not-yet-treated firms. The
doubly-robust Callaway & Sant'Anna estimator is a pre-designated robustness
check, reported alongside if available.

**Primary outcome:** $\text{green\_inv\_share}_{it}$ — share of capital
expenditure directed at green activities (continuous).

**Expected sign:** ATT $> 0$.

**Pre-registered estimand:** overall ATT, aggregated across all cohorts
and post-treatment periods.

**Inference:** cluster-robust SEs at country level; wild cluster bootstrap
alongside analytic SEs.

**Validity failure rule:** If pre-treatment ATT(g,t) coefficients are
statistically significant at p < 0.05 for more than 50% of cohorts, the
parallel trends assumption is untenable. The C&S estimate is not reported
as a causal result. The aggregate ecological correlation (Bartik
supplementary at country×year level) serves as the primary causal result
instead, with an explicit note on the identification limitation.

**Secondary analyses (exploratory, not pre-registered):**
- Binary outcome: $\text{green\_inv\_any}_{it}$
- Event-study dynamics
- Aggregate-level Bartik IV on country×year mean green investment share
  (ecological correlation; different estimand — labelled explicitly)
- Heterogeneity by firm size, sector, and country

---

## What is not pre-specified and why

**Robustness checks.** Alternative clustering, functional form variations,
and sensitivity analyses evaluate whether results are robust to modeling
choices. They are pre-planned in the analysis plan but not pre-registered
here because they do not constitute primary results.

**Validity tests.** The Bartik exclusion restriction test and the
Callaway-Sant'Anna pre-trend test evaluate whether identification
assumptions hold. They are not pre-registered as specifications, but the
decision rules for failure — what is and is not claimed if they fail —
are stated in each specification above and are binding.

**Heterogeneity analyses.** The relevant variation in green investment
across firm size, sector, and country cannot be assessed without
microdata. All heterogeneity analyses are exploratory and labelled as
such in every output.

**Cohesion descriptive.** Purely descriptive; no causal estimand.

**Further robustness with firm financial data.** Pre-specification deferred
until data access is confirmed.

---

## Amendment procedure

Amendments to this document are permitted only for changes forced by data
availability — a variable does not exist under the assumed name, a
geographic coverage threshold is not met, or a survey indicator is coded
differently from what is assumed. Amendments to expected signs, estimands,
comparison groups, or identification strategies are not permitted after
data inspection. Any amendment is committed as a new file
(`prespec-plan-amendment-<date>.md`) and noted in the README alongside the
original hash link.

---

*This file must not be modified after its initial commit.*
