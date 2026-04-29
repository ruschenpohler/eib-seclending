# Appendix: Pre-registered downstream outcome regressions

This appendix reports the pre-registered plausibility checks on downstream SME outcomes (Specification 2 in `prespec-plan.md`). These regressions test whether lagged EIB lending intensity predicts subsequent industry investment rates and firm entry rates, conditioning on lagged constraints, GDP per capita, country fixed effects, year fixed effects, and a COVID-19 indicator. They are included here to satisfy the pre-registration commitment, but are not emphasized in the main results for two reasons.

First, the outcome measures suffer from denominator mismatches. The industry investment rate uses Eurostat SBS table `sbs_na_ind_r2` for NACE sections B, C, D, and E (industry aggregate) and covers all firm sizes, not only SMEs, because gross investment (variable V15110) is unavailable at the SME size class. The firm entry rate uses Eurostat business demography table `bd_9bd_sz_cl_r2` for size class GE10 (10 or more employees), because Eurostat does not provide a 0–249 size class in this table. Both outcomes are therefore only loosely aligned with the SME universe that EIB intermediated lending targets.

Second, the panel is short: 25 countries over 5 outcome years (2016–2020). With country and year fixed effects absorbing much of the variation, there is limited residual variation to detect realistic dynamic effects. The regressions are therefore uninformative rather than evidence of absence.

## Results

| Outcome | β (EIB intensity, t−1) | SE | p-value | WCB p | N | Interpretation |
|---|---|---|---|---|---|---|
| Industry investment rate | −0.0004 | 0.0018 | 0.829 | 0.600 | 120 | Not distinguishable from zero |
| Firm entry rate | +0.0020 | 0.0014 | 0.170 | 0.402 | 120 | Weak positive, not significant |

Both outcomes are winsorised at the 1st and 99th percentile. Cross-region placebo regressions (substituting leave-one-out average EIB intensity of all other countries) yield coefficients of similar magnitude but opposite sign for the firm entry rate (−0.052, p = 0.166), suggesting the weak entry-rate co-movement is not robust to placebo substitution. Wild cluster bootstrap p-values (999 reps, Rademacher weights) confirm that neither estimate is statistically distinguishable from zero.

**Conclusion.** No strong correlational evidence exists for a plausibility channel from EIB intensity to these SME outcomes. The absence of a clear link is consistent with severe omitted-variable bias (EIB selects regions on unobservables), a true small effect, coarse outcome measurement, or thin residual variation after absorbing fixed effects. These results do not speak to whether EIB lending affects SME outcomes; they merely show that the public country-level panel is too coarse and too short to detect such effects.

---

*Method:* `src/analysis/plausibility_check.py`. *Data:* `data/processed/eib_analysis_panel.csv`.
