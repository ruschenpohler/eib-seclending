# AGENTS.md — eib-seclending

This file governs all agent behaviour in this repository. Read it fully before
taking any action. It applies to all models (Claude Sonnet/Opus, MiniMax M1,
GLM 5.1, and others) working in this repo, whether sequentially or in parallel.

---

## Repository Purpose

Phased empirical evaluation of EIB SME intermediated lending. The project has
three phases, each self-contained:

- **Phase 1** (fully public data): Market failure geography and EIB targeting
  consistency. Fully executable now.
- **Phase 2** (EIBIS microdata required): Causal effect of EIB support on firm
  green investment. Primary strategy: Callaway-Sant'Anna staggered DiD
  (temporal variation in firm-level adoption). Supplementary: Bartik IV at
  country level (cross-regional variation in EIB sectoral exposure).
- **Phase 3** (ORBIS required, aspirational): Robustness with firm financials.

The full research design, data sources, feasibility checks, estimating equations,
and analysis steps are in `AGENTS.md` (this file). The human-readable motivation,
AIM framework context, and narrative framing are in `README.md`. Do not conflate
the two.

---

## Directory Structure

```
eib-seclending/
├── .git/
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml              # uv-managed; all dependencies declared here
├── AGENTS.md                   # this file — gitignored
├── impl-log.md                 # agent progress log — gitignored
├── prespec-plan.md             # pre-analysis plan — tracked, write-once
├── README.md                   # human-facing narrative — tracked
├── ideas/                      # project design docs — gitignored
├── data/                       # all data — gitignored
│   ├── raw/                    # source files, never modified after ingest
│   ├── interim/                # intermediate processing outputs
│   └── processed/              # analysis-ready datasets (DuckDB + CSVs)
├── src/
│   ├── ingest/                 # one file per data source
│   ├── analysis/               # one file per analysis step
│   └── viz/                    # figure generation
├── notebooks/                  # exploratory; not used in production pipeline
└── outputs/                    # tracked in git
    ├── figures/
    └── tables/
```

**File protection rules:**
- `data/raw/` is write-once. Once a file is written there by an ingest script,
  do not overwrite or delete it. If re-ingestion is needed, write to a new
  timestamped filename and flag in the implementation log.
- `data/interim/` and `data/processed/` may be overwritten by pipeline reruns.
- `outputs/` is tracked in git. Write final figures and tables here only when
  a step is complete and validated, not as intermediate scratch.
- Never write credentials, API keys, or personal data to any tracked file.

---

## Environment

This project uses `uv` for environment management. All dependencies are declared
in `pyproject.toml`. Never use `pip install` directly.

```bash
# Setup (run once)
uv sync

# Add a new dependency
uv add <package>

# Run a script
uv run python src/ingest/eib_projects.py

# Run a notebook
uv run jupyter notebook
```

**Required packages** (Cowork: initialise these in pyproject.toml on setup):
```
pandas, polars, duckdb, requests, beautifulsoup4, pdfplumber,
eurostat, geopandas, contextily, matplotlib, seaborn,
statsmodels, linearmodels, pyfixest, scipy, numpy, jupyter
```

**Optional — R interop for doubly-robust C&S estimator:**
If R ≥4.2 is available on the system, add `rpy2` to pyproject.toml. This
enables the full Callaway & Sant'Anna doubly-robust estimator via the `did`
CRAN package, which is more rigorous than the Sun & Abraham default. Check R
availability with `Rscript --version` before adding this dependency. If R is
not available, Sun & Abraham via `pyfixest` is the default (see Phase 2).

**Dev dependencies:**
```
pre-commit, ruff
```

---

## Pre-commit Hooks

Pre-commit runs automatically on every commit. Do not bypass with `--no-verify`.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Install once after cloning:
```bash
uv run pre-commit install
```

---

## Git Workflow

### Commit autonomously

Commit after completing each logical unit of work. Do not wait for human
approval before committing. Do not batch unrelated changes into one commit.

**What constitutes a logical unit (one commit per):**
- One data source fully ingested and saved to `data/raw/`
- One feasibility check run and result logged
- One analysis function written and tested
- One figure or table written to `outputs/`
- Any change to `pyproject.toml` or `.pre-commit-config.yaml`
- Bug fix to a single function

**Commit message format:**
```
<phase>/<step>: <what was done>

Examples:
phase1/ingest: download EIB Projects Financed to data/raw/
phase1/check1: feasibility check 1 — NUTS-2 coverage 23% → country-level main spec
phase1/analysis: targeting regression with country + year FE
phase1/viz: constraint map figure saved to outputs/figures/
phase2/ingest: EIBIS microdata loaded and validated
fix: correct NACE sector code alignment in Bartik shares
```

### What not to commit
- Anything in `data/`, `ideas/`, `AGENTS.md`, `impl-log.md`
  (all gitignored — git will not offer to stage them)
- Notebook outputs (cell outputs, kernel state) — always clear before committing
- Any file containing credentials or personal data

---

## .gitignore

**Cowork: create this file exactly as specified. Do not add or remove entries
without human instruction.**

```gitignore
# Agent and design documents
AGENTS.md
impl-log.md
ideas/

# Data (all subdirectories)
data/

# Python
__pycache__/
*.py[cod]
*.pyo
.ruff_cache/
.mypy_cache/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# Environment
.venv/
.env
*.env

# OS
.DS_Store
Thumbs.db

# uv
.python-version
```

**Note on `outputs/`:** This directory is intentionally NOT gitignored. Figures
and tables are deliverables and are versioned. Commit them when a step is complete.

**Note on `prespec-plan.md`:** This file is intentionally NOT gitignored. It is the
pre-analysis plan and must be publicly visible in the repository. Do not add it
to `.gitignore` under any circumstances. It must not be modified after its
initial commit (see Pre-Analysis Plan section below).

---

## Network and External Calls

**All external network requests go through the human.** Agents do not make
outbound HTTP calls autonomously. When a step requires downloading data:

1. Write the download function in `src/ingest/<source>.py`
2. Print the exact URL(s) that will be requested
3. Log in `impl-log.md`: "Awaiting human approval to fetch: <URL>"
4. Stop and wait for the human to confirm before executing the request

**Approved data sources** (Cowork: note these for later steps; human must still
confirm each individual fetch):
- https://www.eib.org/en/projects/loans/index.htm (EIB Projects Financed)
- https://www.eib.org/attachments/publications/annual_report_<year>_en.pdf
- https://data.eib.org/eibis/graph (EIBIS aggregates)
- https://data-api.ecb.europa.eu/service/data (ECB SAFE)
- https://ec.europa.eu/eurostat (Eurostat API via `eurostat` package)
- https://ec.europa.eu/regional_policy (DG REGIO cohesion eligibility)
- https://gisco-services.ec.europa.eu (Eurostat GISCO shapefiles for maps)

---

## Parallel Agent Rules

When multiple agents are active simultaneously:

- Each agent owns exactly one `src/` subdirectory or one named task. Declare
  ownership in `impl-log.md` at the start of each session.
- Agents do not modify files outside their declared scope without logging it.
- If two agents need to write to the same file, the second agent waits and
  logs: "Waiting for <task> to complete before modifying <file>."
- The DuckDB file (`data/processed/eib_analysis.duckdb`) is a shared resource.
  Only one agent writes to it at a time. Log when you open a write connection
  and when you close it.

---

## Implementation Log

Update `impl-log.md` continuously during work. Do not batch updates.
Write an entry every time you complete a step, encounter a problem, make a
decision, or are waiting for human input. Use the template below exactly.

### impl-log.md template

```markdown
# Implementation Log — eib-seclending

---

## Session: <YYYY-MM-DD> — <agent model> — <task scope>

### <HH:MM> | <phase>/<step> | STATUS: [STARTED / COMPLETE / BLOCKED / WAITING]

**What was done:**
<1–3 sentences. Be specific. Include filenames, row counts, parameter values.>

**Result / output:**
<What was produced. File written, check passed/failed, figure saved, etc.>

**Decision made (if any):**
<If a feasibility check triggered a decision rule, state which rule and what
was decided. E.g., "Check 1: NUTS-2 coverage 23% — applying country-level
fallback per decision rule in AGENTS.md.">

**Problem encountered (if any):**
<Exact error message or unexpected finding. What was tried. What is needed.>

**Waiting for (if blocked):**
<Exactly what human input or external action is needed before proceeding.>

**Next action:**
<The single next step this agent will take when unblocked.>

---
```

**Example entry:**

```markdown
## Session: 2026-04-15 — Claude Sonnet 4.6 — Phase 1 ingest

### 09:14 | phase1/check1 | STATUS: COMPLETE

**What was done:**
Downloaded EIB Projects Financed CSV (3,847 rows, 2000–2024). Inspected
geographic fields: columns found are `country`, `promoter_country`, `region`.
`region` field is populated for 891 rows (23.2% by count, 18.4% by signed amount).

**Result / output:**
Saved to data/raw/eib_projects_20260415.csv. Committed: "phase1/ingest: download
EIB Projects Financed to data/raw/"

**Decision made:**
Check 1 decision rule applied: NUTS-2 coverage 18.4% < 30% threshold.
Main analysis runs at country level. NUTS-2 used for robustness on the 891-row
subset only. Logged in README assumptions section.

**Problem encountered:**
None.

**Waiting for:**
Human confirmation to fetch ECB SAFE API endpoint.

**Next action:**
Proceed to Check 2 (sector coding consistency) while awaiting confirmation.
```

---

## Feasibility Checks — Decision Logic

**Standing rule — read the methodology before touching the data:**
For every data source, read the relevant codebook or methodology document before
writing any ingest or analysis code. The purpose is not box-ticking: it is to
understand what each variable actually measures, what its reference period and
unit are, and what institutional or survey context produced it. Agents that skip
this step routinely build analyses on variables they have misunderstood.

Specific documents to read, in order of encounter:

- **EIB Projects Financed CSV**: No published data dictionary exists. Before
  writing `src/ingest/eib_projects.py`, inspect the raw CSV headers and cross-
  reference column totals against the signed volumes reported in the most recent
  EIB Annual Report (available via the annual report URL pattern). The EU Open
  Data Portal landing page is the closest public reference:
  https://data.europa.eu/data/datasets/projects-financed-by-the-european-investment-bank
  Key questions to resolve from the data itself: Is `signed_amount` a commitment
  or a disbursement? Does the date column refer to signature year or financial
  close? Are MBILs included?

- **EIBIS methodology**: Read before writing any code that uses EIBIS aggregates
  or microdata. The 2019 methodology report covers survey design, sampling,
  questionnaire wording, wave structure, and the definition of "EIB-supported
  financing":
  https://www.eib.org/files/survey/eibis-methodology-report-2019-en.pdf
  Key questions: What is the investment reference period for survey responses —
  the prior fiscal year, the past 3 years? How do EIBIS waves map to calendar
  years? What exactly does the financing obstacle indicator measure?

- **ECB SAFE methodology**: Read before writing `src/ingest/ecb_safe.py`. The
  user guide covers the financing obstacle indicators, reference periods, and
  wave-to-year mapping:
  https://www.ecb.europa.eu/stats/pdf/surveys/sme/ecb.safemi.en.pdf

- **Eurostat SBS metadata (ESMS)**: Read before using any SBS variables. Covers
  variable definitions, reference units, and scope:
  https://ec.europa.eu/eurostat/cache/metadata/en/sbs_esms.htm
  Variable codes annex (V11110, V15110, V12110 definitions):
  https://ec.europa.eu/eurostat/cache/metadata/Annexes/sbs_esms_an_1.pdf

- **Eurostat business demography methodology**: Read before using `bd_9bd_sz_cl_r2`.
  Covers enterprise birth/death definitions and the active stock denominator:
  https://ec.europa.eu/eurostat/web/business-demography/methodology

- **Eurostat national accounts (ESMS)**: Read before using `nama_10_pc`. Covers
  GDP per capita concepts and ESA 2010 framework:
  https://ec.europa.eu/eurostat/cache/metadata/en/nama10_esms.htm

Log in impl-log.md for each source: "Read [document name] on [date].
Key findings relevant to this project: [2–4 sentences]." Do this before the
first commit for that source.

---

Run checks in this order. Each check has an explicit pass criterion and a fallback.
Log every check result in `impl-log.md` immediately. Do not proceed to
the next check until the current one is logged and committed.

| # | Check | Pass criterion | Fallback | Blocks |
|---|-------|---------------|----------|--------|
| 1 | EIB Projects — schema, coverage, and year range | See Check 1 sub-tasks below | Depends on sub-task | All Phase 1 analysis |
| 2 | EIB Projects — sector/PPG coding consistency | Stable categories pre/post-2021 | Restrict to 2021–2024 | Bartik sector alignment |
| 3 | Annual Report PDFs — table extractability | Tables extract for 2023; if 2015 fails, manual transcription of 2015–2018 only | Manual transcription 2015–2018 (~8–12hrs); automate 2019–2023 | Bartik shifts |
| 4 | EIBIS aggregates — country × year coverage | ≥24/27 countries, ≥7 years | Replace/supplement with ECB SAFE | Constraint measures |
| 5 | Eurostat SBS — NUTS-2 × sector coverage | ≥200 regions with >80% sector fill | Restrict to Western EU | Bartik shares |
| 6 | Cohesion reclassification events | ≥15 regions reclassified across periods | Drop event study; retain cohesion distribution descriptive only | Part C of Phase 1 |
| 7 | Bartik first-stage F-statistic | F > 10 | Report OLS; IV as future work | Phase 2 IV credibility |
| 8 | EIBIS microdata approval | Approved by EIB | Re-apply with affiliated collaborator | All of Phase 2 |

**On Check 1 — EIB Projects schema, year range, and NUTS-2 coverage:**
Check 1 has three sub-tasks. All must be logged before proceeding to Check 2.

Sub-task 1a — Schema and variable semantics (load-bearing; no published data dict):
Print the CSV column headers and first 5 rows. Identify and log the following,
inspecting the data directly since no official data dictionary exists:
- The amount column: confirm its name, confirm it is denominated in EUR (not
  local currency or millions), and determine whether it represents a signed
  commitment (the legal obligation at contract date) or a disbursement (actual
  cash transfer). Cross-reference: sum all rows for 2023 and compare to the
  total EIB signatures figure in the most recent EIB Annual Report. If the
  totals match, it is commitments/signatures. Log the finding explicitly.
  This matters because the targeting regression and Bartik shifts use this
  column as the measure of EIB lending intensity — a disbursement-based
  series would have a different temporal profile than a commitment-based one.
- The date column: confirm whether it is signature year, financial close year,
  or reporting year. This affects temporal alignment with EIBIS waves.
- Whether MBILs (intermediated operations) are present: look for a financing
  type or modality column. If absent, all rows may be direct lending only —
  which would undercount EIB's SME exposure and invalidate the Bartik shifts
  (see Check 2 sub-task A). Flag immediately if MBILs appear absent.

Sub-task 1b — Year coverage:
Confirm the dataset spans at least 2015–2023 (the minimum needed to align with
EIBIS wave coverage and compute Bartik shifts). Log the min and max year
present in the date column.

Sub-task 1c — NUTS-2 geographic coverage:
As originally specified: compute the share of signed amount associated with
rows that have a populated NUTS-2 region field. Pass criterion: >30%. Fallback:
country-level main spec.

**Check 1 actual results (logged 2026-04-27):**
- Dataset: `loanExport.xlsx`, 29,195 rows x 7 columns, 1959–2025.
- `Region` field is 100% populated but at macro-region level only (European Union,
  Africa/Caribbean/Pacific, Mediterranean countries, etc.). No NUTS-2 codes in any field.
- NUTS-2 coverage = 0%. Decision: country-level main spec applied.
- 455 rows have `Country or Territory = "EU Countries"` (generic pan-EU entry).
  Text analysis recovered 153/455 (34%) from country/city names in descriptions;
  remaining 302 are genuinely pan-EU and excluded from country-level regressions.
- The closest literature (Amamou et al. 2020, Barbera et al. 2022) also runs at
  country level with firm-level fixed effects. Our geographic level is standard.
- NUTS-2 robustness is deferred to Phase 3 (ORBIS, aspirational) if firm addresses
  become available.
- EIB "projects to be financed" (pipeline) noted as potential future extension
  (`data/raw/pipelineExport.xlsx` if provided) but not part of current design.

**On Check 2 — sector coding and NACE alignment (preflight for Check 3 and
Bartik construction):** Check 2 has two sub-tasks that must both be resolved
before the Bartik instrument can be built.

Sub-task A — intermediated coverage (preflight for Check 3):
Determine whether the EIB Projects Financed CSV includes intermediated lending
(MBILs), not only direct operations — look for a `financing_type` or `modality`
column distinguishing direct vs intermediated. If intermediated operations are
present with sector codes, Check 3 (Annual Report PDF extraction) can be
bypassed entirely. Log "Check 3 bypassed: EIB Projects CSV covers intermediated
operations at sector level" and skip to [INGEST] EIBIS aggregates. If the CSV
covers direct lending only, proceed to Check 3 as specified.

Sub-task B — NACE alignment:
The EIB Projects CSV may use EIB's internal sector classification ("Infrastructure
- Energy", "SMEs and Mid-Caps", etc.) rather than NACE 2-digit codes. The Bartik
shares from Eurostat SBS are NACE-based, so alignment is required. Inspect the
sector column(s) in the CSV and determine whether they map to NACE or require a
crosswalk. If a crosswalk is needed: construct it manually (10–15 EIB sector
categories → NACE sections suffice for Bartik construction) and save to
`data/raw/eib_nace_crosswalk.csv` with columns `eib_sector, nace_section,
nace_section_name, notes`. Log the crosswalk approach and any ambiguous
mappings in impl-log.md. Do not proceed to Bartik construction
until this is resolved.

**On Check 4 — EIBIS aggregates, indicator identity, and wave mapping:**
Check 4 has three sub-tasks beyond the coverage criterion.

Sub-task 4a — Indicator identity:
The targeting regression and plausibility check use a constraint indicator named
`fin_constraint_share` in this document. Confirm that an indicator matching this
concept exists in the downloaded EIBIS aggregate export — the EIBIS portal uses
its own indicator labels, which may differ. The concept is: share of SMEs
reporting access to finance as their main obstacle to investment. If the column
name differs, log the actual name and update all references in analysis scripts.
If no financing constraint indicator is present, the fallback is ECB SAFE (see
Check 4 fallback rule in the table).

Sub-task 4b — Wave-to-year mapping:
EIBIS waves do not map trivially to calendar years. The 2019 methodology report
(https://www.eib.org/files/survey/eibis-methodology-report-2019-en.pdf) documents
the fieldwork periods. Log: which calendar year does each wave refer to? Does
the aggregate export label rows by wave number or by year? Does the investment
reference period in the survey questionnaire refer to the past 12 months, the
past fiscal year, or another window? This matters for temporal alignment with
EIB Projects signed amounts and ECB SAFE waves.

Sub-task 4c — Coverage criterion:
As originally specified: ≥24/27 EU countries, ≥7 years. Log country and year
counts from the downloaded file.

**On Check 3 specifically:** Test 2023 first (most recent, most likely clean).
Then test 2015 (oldest target year, most likely to be image-embedded). If 2023
extracts but 2015 fails, manually transcribe 2015–2018 only (likely pre-digital
workflow) and automate 2019–2023. Log exact page numbers of sector tables for
each year tested.

**On Check 5 — Eurostat SBS variable existence, scope, and base-year availability:**
Check 5 has three sub-tasks beyond the NUTS-2 × sector coverage criterion.

Sub-task 5a — Variable availability and ratio validity:
Confirm that table `sbs_sc_sca_r2` returns non-null data for the following
variables at size class 10–249 employees for at least 20 EU countries:
- V11110: number of enterprises (Bartik denominator and targeting regression LHS)
- V15110: gross investment in tangible goods (plausibility check outcome 1 numerator)
- V12110: value added at factor cost (plausibility check outcome 1 denominator)
Read the variable codes annex
(https://ec.europa.eu/eurostat/cache/metadata/Annexes/sbs_esms_an_1.pdf)
before using these variables. Key question: does V15110 include financial
leasing? What is the reference unit — enterprise group, enterprise, or local
unit? Log findings before computing any ratio.

Coverage comparability check (required before computing investment rate):
V15110 (gross investment) has mandatory reporting thresholds that vary by EU
country — some member states do not require firms below the VAT threshold to
report investment even if they file value added. Within the 10–249 size range,
V15110 may therefore be missing for smaller firms while V12110 is not, producing
a selected ratio that reflects only larger, more capital-intensive firms. Before
constructing V15110 / V12110, compute the non-null rate of each variable
separately for the 10–249 size class by country×year. If the non-null rate for
V15110 is more than 10 percentage points lower than for V12110 in any country,
note this in impl-log.md, compute the ratio only for cells where both
are non-null above 80%, and add this as a footnote in all output tables using
this ratio.

Sub-task 5b — Base-year employment shares for Bartik:
The Bartik instrument requires employment shares fixed at a pre-period base year.
Confirm that the SBS employment variable (V16110: number of persons employed,
or V13110: number of employees) is available for the intended base year (earliest
year in the analysis window, likely 2015 or 2016) at sufficient NACE × country
or NACE × NUTS-2 coverage. If the base year is missing for many cells, the Bartik
shares will be estimated on a biased subsample — flag to human.

Sub-task 5c — NUTS-2 × sector coverage criterion:
As originally specified: ≥200 regions with >80% sector fill. Fallback: restrict
to Western EU. Log counts.

**On Check 7 (Bartik F-statistic):** If F < 10, the most likely cause is
insufficient geographic variation at country level (only 27 EU member states).
Two potential fixes — log which applies:
- Fix A: If Check 1 returned NUTS-2 data for ≥30% of operations, rerun Bartik
  at NUTS-2 level and retest F-statistic.
- Fix B: Once EIBIS microdata is available (Check 8), interact Bartik with
  firm-size bins to add within-country variation.
Do not attempt Phase 2 IV estimation if F < 10 without human sign-off.

**On C&S pre-trend failure:** If the event study shows significant pre-treatment
coefficients (differential green investment trends before firms adopt EIB support),
apply the following rules in order:
- Primary fix: restrict estimation to cohorts with at most 1 significant
  pre-treatment coefficient at the 5% level. Re-run ATT aggregation on the
  restricted sample. Log the number of cohorts excluded and their share of
  treated observations.
- Robustness: re-run the restricted-sample C&S with a linear pre-trend
  control (Freyaldenhoven, Hansen & Shapiro 2019 approach). Report alongside
  the main estimate.
- If pre-trends are pervasive (>50% of cohorts fail): C&S estimates are
  unreliable. Fall back to Bartik supplementary as the primary causal claim
  and flag to human before writing Phase 2 outputs.
Early cohort rule: EIBIS begins in 2016. Cohorts first treated in wave 2 (2017)
have at most one pre-treatment period — insufficient for a pre-trend test.
Exclude these cohorts from the event study plot but retain them in the overall
ATT aggregation. Document the number of excluded cohorts in the balance table
footnote.

**Bartik identification argument (state explicitly in README and outputs):**
The Bartik instrument uses predetermined regional industrial structure to
predict regional EIB lending exposure. The formula is:

    Bartik_rt = Σ_j (employment_share_jr,0 × EIB_sectoral_lending_jt)

where:
- j       = NACE 2-digit sector
- r       = country (or NUTS-2 region if Check 1 passes)
- t       = year
- employment_share_jr,0  = region r's share of employment in sector j,
                           fixed at pre-period base year (shares)
- EIB_sectoral_lending_jt = EU-aggregate EIB signed volume in sector j,
                            year t, from EIB Projects Financed CSV or
                            Annual Reports (shifts)

The shift variable is EU-aggregate EIB sectoral lending, not sectoral green
output growth. Using green output growth as the shift would be an exclusion
restriction violation — it directly causes firm green investment through
industrial composition, not through the EIB lending channel. The EIB sectoral
allocation is plausibly exogenous because it is set at the institutional level
by the Board of Directors in response to EU mandate objectives (operational
plan volume targets, InvestEU allocation mandates) — not by conditions in any
single region. The exclusion restriction is that Bartik exposure affects firm
green investment only through the EIB lending channel, not independently
through correlated regional industrial structure.

Mandatory robustness test (add to `src/analysis/bartik.py`, log in Check 7):
The test must be specified at region×year level — EIB_sectoral_lending_jt is
EU-aggregate (sector×year only) and cannot be directly regressed on a
region×sector×year variable. The correct test is:

    ΔEIB_volume_rt = α + π·Bartik_rt + β·sector_growth_residual_rt
                     + δ_r + θ_t + ε_rt

where ΔEIB_volume_rt is the year-on-year change in actual regional EIB signed
volume, Bartik_rt is the Bartik-predicted change, and sector_growth_residual_rt
is the region's deviation from the EU-wide sectoral growth trend (constructed
as the residual from regressing regional sectoral growth on EU-wide sector×year
means). Test H₀: β = 0. If rejected, actual EIB lending responds to
region-specific conditions beyond what the Bartik predicts — the exclusion
restriction is likely violated. If this test fails, report OLS only and flag
to human before proceeding.

---

## Pre-Analysis Plan

### Purpose and mechanism

`prespec-plan.md` is the project's pre-analysis plan. It records the primary
specification for each estimating equation, the expected direction of each
coefficient, and which analyses are designated primary vs. secondary —
all before any data is downloaded or inspected.

The credibility mechanism is Git's content-addressable history. Once
`PRESPEC.md` is committed, the commit hash is a cryptographic proof that
the pre-analysis plan existed at that moment. The README links to the file
at the exact commit hash, creating a permanent, publicly verifiable record
that the research design predates the data. This is a lightweight but
legitimate pre-registration for an observational study.

### When to create and commit prespec-plan.md

`prespec-plan.md` must be created and committed as the **first substantive commit
in the repository**, before any data is fetched and before Check 1 runs.
The commit message must be exactly:

    Registered primary specifications in prespec-plan.md before start of analysis

After this commit, `prespec-plan.md` must not be modified. If an amendment is
genuinely required (e.g., a data source turns out not to exist), create a
new file `prespec-plan-amendment-<date>.md`, commit it with message
`Amendment to prespec-plan.md — <reason>`, and note it in the README alongside the
original link. Do not edit or force-push the original commit.

### What prespec-plan.md must contain

Write `prespec-plan.md` with exactly the following sections. Fill in each section
precisely — this is not a summary of AGENTS.md but a commitment to specific
choices before data is seen.

Use the content of `prespec-plan.md` in the repository root as the canonical
template. The document contains a narrative introduction establishing the
logical chain from descriptive to causal, four numbered pre-registered
specifications (targeting consistency, aggregate co-movement, aggregate
causal effect, firm-level causal effect), and a section explaining what
is not pre-specified and why. Write `prespec-plan.md` to match that
structure and content exactly. Do not use "Phase" labels in this document —
those are internal guideposts only.

### How to reference prespec-plan.md in README

After making the pre-registration commit, record the commit hash and add the
following blocks to README.md (fill in [HASH] with the actual 40-character hash).

**In the introduction (first or second paragraph):**
```markdown
The empirical design was pre-registered before any data was downloaded, using
Git's content-addressing as a lightweight but cryptographically verifiable
pre-registration mechanism. All primary specifications, expected coefficient
signs, and the primary/secondary designation for every estimating equation are
committed at a fixed, publicly visible hash that cannot be altered retroactively.
```

**Under the Results section, as the first item:**
```markdown
## Results

> **Pre-registered design.** All results below were specified before data access.
> Pre-analysis plan: [`[HASH]`](https://github.com/[owner]/[repo]/blob/[HASH]/prespec-plan.md)
> · [Commit timestamp](https://github.com/[owner]/[repo]/commit/[HASH])
```

The Cowork instruction for this is in the Instructions for Cowork section.
Do not write either README block until the commit hash is known.

---

## Phase 1 Task Graph

Execute in this order. Each task maps to one or more source files in `src/`.
Commit after each completed task.

```
[CHECK 1] EIB Projects — geographic coverage
    → src/ingest/eib_projects.py
    → data/raw/eib_projects_<date>.csv
    ↓
[CHECK 2] EIB Projects — sector coding
    → (same file, additional analysis)
    ↓
[INGEST] EIBIS aggregates
    Before downloading: read EIBIS methodology report (URL in codebook rule).
    → src/ingest/eibis_aggregates.py        ←─┐
    → data/raw/eibis_aggregates.csv           │ parallel
[INGEST] ECB SAFE aggregates                  │ if human
    Before downloading: read ECB SAFE        │ approves
    methodology PDF (URL in codebook rule).  │
    On ingest, confirm: (a) the financing    ←───┘
    obstacle series key exists at the API
    endpoint; (b) each wave can be mapped
    to a calendar year with no gaps;
    (c) the series covers ≥20 EU countries.
    If series key has changed or endpoint
    returns errors, log and ask human for
    the current key before proceeding.
    → src/ingest/ecb_safe.py
    → data/raw/ecb_safe_<series>.csv
    ↓
[CHECK 4] EIBIS coverage assessment
    → (in eibis_aggregates.py)
    ↓
[INGEST] Eurostat regional tables
    Before downloading: read SBS ESMS metadata and variable codes annex,
    and business demography methodology (URLs in codebook rule above).
    In a single script, fetch and validate the following tables:
    - sbs_sc_sca_r2: V11110, V15110, V12110 at size 10–249 (see Check 5a)
    - sbs_sc_sca_r2: employment variable at base year (see Check 5b)
    - bd_9bd_sz_cl_r2: enterprise births and active stock at size 0–249.
      Confirm columns for births count and active enterprise stock exist
      and are non-null for ≥20 EU countries. Log year coverage.
    - nama_10_pc: CP_EUR_HAB at country×year. Confirm coverage matches
      the analysis panel (same countries and years as EIBIS waves). If
      any country-year cells are missing, log which ones — these will
      be dropped from regressions requiring this control.
    → src/ingest/eurostat_data.py
    → data/raw/eurostat_<table>.csv
    ↓
[CHECK 5] Bartik shares coverage
    → (in eurostat_data.py)
    ↓
[INGEST] Cohesion eligibility (manual + script)
    → data/raw/cohesion_eligibility.csv     # manual CSV from DG REGIO PDFs
    → src/ingest/cohesion.py               # loads and validates
    ↓
[CHECK 6] Reclassification event count
    → (in cohesion.py)
    ↓
[CHECK 3] Annual Report PDF extraction
    → src/ingest/eib_annual_reports.py
    → data/raw/eib_sector_lending_<year>.csv
    ↓
[BUILD] Analysis dataset
    Before merging, write a log entry in impl-log.md that explicitly
    answers the following three questions. Do not proceed to analysis until this
    entry exists. The purpose is to force conceptual grounding before the two
    series are combined — not to block progress, but to ensure the merge is
    understood, not just executed.

    Q1 — What does EIB_volume_per_SME measure, precisely?
    The numerator (EIB Projects signed amount) is a supply-side commitment
    recorded at contract signature, denominated in EUR at the date of signing.
    The denominator (Eurostat SBS V11110) is a count of active enterprises at
    year-end. State: what does the ratio represent economically? What does a
    doubling of this ratio mean — more EIB activity, fewer SMEs, or both? Does
    the signature-year timing of the numerator align with the reference year of
    the denominator? If they are misaligned by one year, note this and decide
    whether to lag one of them.

    Q2 — What does the EIBIS constraint indicator measure, precisely?
    The EIBIS aggregate reports the share of SMEs reporting access to finance as
    their main obstacle. Is this a net balance (% constrained minus % unconstrained)
    or a gross share? Does it refer to the survey fieldwork year or to the prior
    investment year (per the EIBIS methodology report)? State this explicitly and
    confirm it matches the temporal alignment assumed in the targeting regression.

    Q3 — Are the two series measuring the same universe of firms?
    EIB Projects covers all EIB Group operations, including large corporates and
    infrastructure projects, not only SMEs. The targeting regression restricts to
    SME lending by construction only if the CSV has an SME-specific filter. Confirm
    whether a filter on financing type, beneficiary size, or PPG code is needed to
    restrict EIB Projects to SME-relevant operations before computing the ratio.
    Log the filter applied (or the explicit decision that no filter is needed).

    → src/analysis/build_dataset.py
    → data/processed/eib_analysis.duckdb
    ↓
[ANALYSIS — can parallelise below this point]
    ↓                           ↓
[DESCRIPTIVE]              [BARTIK]
Beat 1: constraint map     Build instrument
Beat 2: Δconstraint vs     → src/analysis/bartik.py
        ΔEIB allocation    → data/interim/bartik_exposure.csv
        (scatter: annual   ↓
        change in          [CHECK 7] First-stage F
        constraint_rt vs   → (in bartik.py)
        change in EIB
        volume_rt; country
        labels; OLS fit)
Beat 3: time series
Beat 4: cohesion dist.
→ src/analysis/
  descriptives.py
→ outputs/figures/
    ↓
[TARGETING REGRESSION]
    Operational definition of "targeting consistency":
    EIB lending volume per SME is higher where financial constraints are worse,
    controlling for GDP/capita, country FE, and year FE.

    Variable construction:
    - LHS: EIB_volume_per_SME_rt = EIB signed amount (EUR, from eib_projects raw)
      aggregated to country×year, divided by number of SME enterprises from
      Eurostat SBS table `sbs_sc_sca_r2`, variable V11110 (number of enterprises),
      size classes 10–249 employees (SME proxy). Log-transform before regression.
    - constraint_index_rt: share of SMEs reporting access to finance as main
      obstacle, from EIBIS aggregates (indicator: `fin_constraint_share`,
      country×year). If EIBIS coverage fails Check 4, substitute ECB SAFE
      (Survey on the Access to Finance of Enterprises): dataset `ECB_SAFE`,
      indicator "financing obstacles: access to finance" for SMEs, country×wave
      → map waves to years using ECB SAFE field guide. Fetch via
      https://data-api.ecb.europa.eu/service/data/ECB_SAFE; confirm exact
      series key with human before fetching (series key structure may have
      changed).
    - GDP_pc_rt: Eurostat table `nama_10_pc`, variable CP_EUR_HAB (GDP per capita
      at current prices, EUR), country×year.
    - Coverage: all EU-27 countries, years matching EIBIS wave coverage (≥7 years
      per Check 4). If country-level per Check 1 decision: r = country. If NUTS-2
      per Check 1: r = NUTS-2 region; use NUTS-2 FE and cluster SEs at country level.

    Primary specification:
        log(EIB_volume_per_SME_rt) = α + β·constraint_rt + γ·log(GDP_pc_rt)
                                     + δ_r + θ_t + ε_rt
    SEs clustered at country level. Report β. A positive significant β is the
    pass criterion. If β ≤ 0, flag immediately per "What to Ask the Human" rule 5.

    Robustness: also run with EIB_volume / GDP_rt as LHS to check denominator
    sensitivity.
→ src/analysis/targeting.py
→ outputs/tables/phase1_targeting_regression.csv
    Columns: spec, N, β_constraint, se_constraint, t_stat, p_value, R2_within,
             FE_type, cluster_level, notes
    ↓
[PLAUSIBILITY CHECK]
    A correlational test: does lagged EIB lending intensity co-move with
    subsequent SME outcomes after conditioning on constraint severity and
    fixed effects? This is a plausibility check for the causal chain, not
    a causal estimate. OVB is unresolved — EIB selects where to lend based
    on factors that also determine regional outcomes, and conditioning on
    lagged observables does not fully address this. Label all outputs
    "correlational — not causal" in table footnotes and README text.
    Do not use language implying prediction or causation.

    Data availability check (run before analysis, log in impl-log.md):
    Eurostat SBS has a 10–22 month publication lag (preliminary at T+10,
    final at T+22). Before running this step, check which outcome years are
    currently available. If SBS outcomes only extend to 2020 or 2021, note
    this as the analysis endpoint and assess whether the 2020 COVID shock is
    a confounder the specification cannot adequately address (COVID
    simultaneously depressed EIB lending, SME investment, and firm entry).
    If 2020 is the last available year, consider dropping it and noting the
    truncation, or adding a 2020 indicator as a control.

    Variable construction:
    - Outcome 1 — SME investment rate: gross investment in tangible goods
      divided by value added, from Eurostat SBS table `sbs_sc_sca_r2`,
      variables V15110 (gross investment) / V12110 (value added at factor
      cost), size classes 10–249 employees, country×year. Winsorise at
      1st/99th percentile.
    - Outcome 2 — firm entry rate: number of enterprise births divided by
      active enterprise stock, from Eurostat business demography table
      `bd_9bd_sz_cl_r2`, size classes 0–249 employees, country×year.
    - EIB_intensity_rt: same construction as targeting regression LHS
      (log EIB signed amount per SME), lagged 1 year (t−1).
    - constraint_rt: same EIBIS / ECB SAFE measure as targeting regression,
      lagged 1 year (t−1).
    - GDP_pc_rt: same Eurostat source as targeting regression.
    - Temporal alignment: constraints at t−1, EIB intensity at t−1,
      outcomes at t (e.g., 2019 EIB intensity and constraints → 2020
      outcomes). Panel coverage determined by SBS availability check above.

    Primary specification (run separately for each outcome):
        Outcome_rt = α + β·EIB_intensity_r,t-1 + γ·constraint_r,t-1
                     + φ·log(GDP_pc_rt) + δ_r + θ_t + ε_rt
    SEs clustered at country level. Report β.

    Cross-region placebo (add to same script):
    To distinguish a genuine within-region EIB effect from eurozone-wide cycle
    effects, estimate for each country r a placebo regression substituting
    EIB_intensity from a different country r' as the regressor:
        Outcome_rt = α + β_placebo·EIB_intensity_r',t-1 + γ·constraint_r,t-1
                     + φ·log(GDP_pc_rt) + δ_r + θ_t + ε_rt
    Use a leave-one-out approach: for each country r, regress its outcomes on
    the GDP-weighted average EIB intensity of all other countries. If β_placebo
    is significant, a common eurozone factor is likely driving both EIB lending
    and regional outcomes — flag in outputs as a limitation. If β_placebo is
    near zero while the main β is significant, within-region co-movement is
    specific to the country's own EIB exposure. Report β_placebo alongside the
    main estimate in the output table; label it "cross-region placebo — diagnostic
    only, not a causal test."

    Coverage notes (add to all output table footnotes):
    (a) Eurostat SBS covers firms above the filing threshold — typically ≥10
    employees or above the VAT threshold. Micro-enterprises (<10 employees) are
    excluded. Results reflect SMEs in the 10–249 employee range, which is also
    EIB's primary intermediated lending target through MBILs.
    (b) EIBIS samples from ORBIS, which under-represents very young firms, very
    small firms (<10 employees), and firms in countries with weak financial filing
    requirements. Results may not generalise to the full population of EIB SME
    beneficiaries, which includes firms as small as 0 employees under EIB
    microfinance mandates.

    Decision rule: if both β estimates are near zero or negative, note in
    impl-log.md and flag to human before writing final outputs —
    this is a substantively important null result.
→ src/analysis/plausibility_check.py
→ outputs/tables/phase1_plausibility_check.csv
    Columns: outcome_var, spec, N, analysis_endpoint_year, β_eib_intensity,
             β_placebo, se, t_stat, p_value, R2_within, FE_type, cluster_level,
             notes
    ↓
[OUTPUTS]
All figures to outputs/figures/
All tables to outputs/tables/
Commit: "phase1: complete — all outputs written"
```

**Note on Phase 1b (post-execution reframing, 2026-04-28):**
Phase 1b was originally discussed as a possible causal regression of financing
constraints on EIB intensity. After discussion with the human, it is **reframed
as a set of robustness/heterogeneity checks around the targeting regression,
not a standalone causal specification.** The only aggregate causal claim in
this project is the Bartik IV (Spec 3, Phase 2b). The reframed checks test
whether the null targeting result masks heterogeneity by income level (B2),
financial integration (B3: euro vs. non-euro), or constraint severity (B4),
or whether planning delays explain the contemporaneous null (1b-lagged, already
run). These are exploratory/descriptive, not causal, and do not require a
prespec-plan amendment. They are logged in impl-log.md as "remaining robustness
checks" for any future agent to resume.

**Note on Phase 2b Bartik IV (executed 2026-04-28, human decision: Option 1):**
The Bartik instrument was constructed exactly as pre-registered:

    Bartik_rt = Σ_j (employment_share_jr,2015 × EIB_sectoral_lending_jt)

- Shares: SBS V16110 (persons employed), size classes 10-249 aggregated,
  base year 2015, 27 countries × 12 NACE sections.
- Shifts: EIB Projects CSV mapped to NACE via `data/raw/eib_nace_crosswalk.csv`,
  EU-aggregate signed amount by NACE section × year.
- Common sectors: C, D, E, F, G, H, I, J, L, M, N (11 sections).

**First-stage result:** F = 2.45 (t = 1.56, p = 0.13) — **far below the F > 10**
**threshold.** The instrument is too weak at the country level to support a
causal claim. This is a structural feature of 27-cluster analysis, not a data
or coding error.

**Human decision:** Accept the weak instrument. Do not report 2SLS as causal.
Phase 2b is documented (instrument saved, code committed, results logged) but
**does not produce a pre-registered causal estimate.**

**For future agents:**
- Do NOT tweak instrument construction to chase a higher F. That would be
  specification searching and violates the pre-registration.
- To rescue the Bartik IV, add geographic units (NUTS-2 from ORBIS/EIBIS
  microdata — Fix B in Check 7) or cross-level interactions (firm size bins
  within countries). Both require data not currently available.
- The pre-registered fallback is to rely on Spec 1 (targeting, null) and
  Spec 4 (firm-level C&S) for causal inference.
- All Phase 2b artifacts: `src/analysis/bartik.py`,
  `data/interim/bartik_instrument.csv`, `outputs/tables/phase2b_bartik_iv.csv`.

**Note on statistical power and descriptive reassurance (2026-04-28):**
All Phase 1 country-level regressions operate with 27 clusters and ~120–160
observations. CRV1 standard errors are noisy; wild cluster bootstrap is
essential. The null targeting result and weak plausibility result may reflect
thin variation as much as a true zero effect. Descriptive outputs (constraint
map, time-series trends, scatter plot) provide face-validity reassurance:
- Geographic variation aligns with textbook market-failure geography
  (Southern/Eastern Europe = worse constraints).
- Time-series trends show the expected pre-COVID easing of constraints.
- Scatter outliers are dominated by small-country volatility (SI, LU, EE, LT),
  reinforcing that the signal-to-noise ratio at country-level is poor.
These patterns should be cited in README/paper as evidence that the data are
not nonsensical, even if regressions are underpowered.

---

## Phase 2 Task Graph

**Phase 2 and Phase 2b produce complementary contributions, not a hierarchy:**
Phase 2b (Bartik + ECB SAFE, public data only) is the project's core replicable
contribution — it tests whether EIB sectoral exposure reduces aggregate financing
constraints using only public data, demonstrates the Bartik methodology, and
produces a deliverable regardless of EIBIS approval. Phase 2 (C&S + EIBIS
microdata) extends this to the firm-level causal question: does EIB support cause
individual firms to invest more in green activities? If EIBIS is approved, Phase
2b becomes a macro-level robustness check for the firm-level Phase 2 result. If
denied, Phase 2b stands alone as a complete paper. Execute Phase 2b in parallel
with the EIBIS application; do not treat it as a consolation prize.

**Pre-specified primary result (commit to this before EIBIS data arrives):**
The primary specification is C&S with `green_inv_share` as outcome, not-yet-treated
comparison group, overall ATT aggregation. This is the result that will be
reported as the main finding. All other specifications — Bartik IV, `green_inv_any`,
heterogeneity cuts, event-study dynamics — are secondary and must be labelled as
such in all outputs and README text. This pre-specification is not a formal
pre-registration but is a binding commitment within this project: do not
re-designate the primary result after seeing the data.

Note on treatment concepts: Phase 1 and Phase 2b use supply-side EIB volume
(signed amounts from EIB Projects CSV, aggregated to country×year) — they answer
"where does EIB lend and does aggregate exposure matter?" Phase 2 uses demand-side
receipt (EIBIS firm-level eib_support flag) — it answers "does receiving EIB
support cause a specific firm to invest more green?" These are distinct estimands
and results do not speak to each other directly. State this distinction explicitly
in README and in output table headers.

**Power calculation before EIBIS application (run at Phase 1 completion):**
Before submitting or re-submitting the EIBIS data access request, run a quick
power assessment using Phase 1 aggregate data. The goal is to confirm Phase 2
is viable before investing in the application process.

Compute and log in impl-log.md:
1. Number of country×sector×year cells in the Bartik instrument
2. Standard deviation of Bartik_rt across cells (variation in EIB exposure)
3. Assumed treatment share: 10–20% of ~12,000 EIBIS firms = 1,200–2,400 treated
4. Minimum detectable effect (MDE) at 80% power, α=0.05, given cluster count
   (27 countries) and treatment share — use a simple cluster-robust power
   formula: MDE ≈ 2.8 × σ_outcome / √(n_treated × (1 - ρ_intracluster))
5. Compare MDE to plausible effect sizes using the correct outcome distribution.
   The relevant outcome is green_inv_share — the share of capex in green
   activities — which is concentrated near zero for most SMEs, with SD likely
   in the 10–20pp range based on EIBIS annual report descriptives. Do not
   use employment or output growth effect sizes from EIF/EIB studies as the
   benchmark — those are a different outcome with a different variance structure.
   Use the SD of green_inv_share from published EIBIS descriptive statistics
   (check EIBIS annual report most recent wave) to compute the MDE.

If MDE >> plausible effect size: flag to human before proceeding with EIBIS
application. C&S may be better powered than Bartik IV (more variation) — note
separately. Add this as → src/analysis/power_check.py

**Do not begin Phase 2 data work until Check 8 (EIBIS microdata approval) is
confirmed by the human. However, begin the Phase 2 analysis skeleton (pseudocode,
stub functions, merge logic) as soon as Phase 1 ingest is complete. This means
`src/analysis/iv_estimation.py` and `src/analysis/merge_phase2.py` should have
function signatures, docstrings, and pseudocode stubs committed before Check 8
resolves, so execution is immediate once data arrives.**

```
[PHASE 2b — execute in parallel with Check 8, regardless of outcome]
    Data: ECB SAFE aggregates (already ingested in Phase 1) + Bartik instrument
    (already constructed in Phase 1). No new data required.

    Estimating equation (2SLS):
    - Outcome:             constraint_rt (ECB SAFE financing obstacle share,
                           country×year)
    - Endogenous regressor: EIB_volume_per_SME_rt (actual EIB signed amount per
                           SME, from Phase 1)
    - Instrument:          Bartik_rt (from Phase 1)
    First stage: EIB_volume_per_SME_rt = π·Bartik_rt + γ·log(GDP_pc_rt) + δ_r + θ_t
    Second stage: constraint_rt = β·EIB_volume_per_SME_hat_rt + γ·log(GDP_pc_rt)
                                  + δ_r + θ_t + ε_rt
    Report OLS and 2SLS. Wild cluster bootstrap p-values (27 clusters).

    If Check 8 approved: Phase 2b is a macro-level robustness check alongside
    the firm-level Phase 2 results.
    If Check 8 denied: Phase 2b is the main deliverable — a complete paper
    on the reduced-form effect of EIB sectoral exposure on aggregate financing
    constraints.

    → src/analysis/phase2b_safe_iv.py
    → outputs/tables/phase2b_safe_iv.csv
    Commit: "phase2b: complete — Bartik IV on ECB SAFE constraints written"
```

```
[INGEST] EIBIS microdata
    → src/ingest/eibis_microdata.py
    → data/raw/eibis_microdata_<date>.csv
    ↓
[VALIDATE] EIBIS structure check
    Run before any analysis. Three critical-path items must be resolved first.

    Critical-path item 1 — EIB support indicator:
    The C&S design depends entirely on a firm-level binary identifying EIB
    Group-supported financing. Search for any of: eib_support, eib_group_finance,
    policy_support_type, favourable_finance_source, or equivalent. If the variable
    is categorical (e.g., EIB / EIF / national promotional bank as separate
    categories), redefine treatment as any EIB Group category and log the decision.
    If no such variable exists, C&S cannot be implemented — flag to human
    immediately before proceeding with any other analysis.

    Critical-path item 2 — Sub-national geography:
    Check for a NUTS-2 or regional location field (nuts2, region, nuts2_code).
    If present, Bartik can run at NUTS-2 level (~200+ regions vs 27 countries),
    substantially improving first-stage power. Assess this before running any
    Phase 2 analysis and revisit the Check 7 F-statistic decision accordingly.

    Critical-path item 3 — Panel identifiers and wave mapping:
    Confirm bvd_id (or equivalent) is stable across waves and that the wave
    variable is mappable to a calendar year. If either is absent, C&S cannot
    be implemented — fall back to Bartik only.

    Confirm also: green_inv_share, green_inv_any, nace2, size_class.
    Log all findings and ask human before proceeding if any critical-path
    item is unresolved.
    ↓
[MERGE] EIBIS microdata + Bartik exposure
    → src/analysis/merge_phase2.py
    → data/processed/phase2_analysis.duckdb
    ↓
[VALIDATE — PANEL STRUCTURE CHECK]
    Confirm EIBIS microdata has:
    (a) firm-level identifier stable across waves (bvd_id or equivalent);
    (b) wave variable mappable to calendar year;
    (c) eib_support indicator that can define a "first treated wave" per firm;
    (d) sub-national location field (nuts2 or region) — needed to assess whether
        Bartik can be run at NUTS-2 level rather than country level.
    Decision rules:
    - If (a) or (b) absent: skip C&S; run Bartik at country FE only. Log.
    - If (d) absent: Bartik runs at country×year level (27 clusters). Flag
      thin variation risk in impl-log.md; C&S remains primary.
    ↓
[ANALYSIS — PRIMARY: Callaway-Sant'Anna staggered DiD]
    C&S identifies off temporal variation in firm-level treatment adoption —
    this is where the real identifying power lies in EIBIS panel data.

    Spec:
    - Treatment: first EIBIS wave in which firm i reports eib_support == 1
    - Outcomes: green_inv_share (continuous), green_inv_any (binary)
    - Estimand: ATT(g,t) — average treatment effect for cohort g at time t
    - Comparison group: not-yet-treated firms (preferred over never-treated;
      never-treated firms may differ systematically on green investment propensity)
    - Implementation: Sun & Abraham (2021) interaction-weighted estimator via
      `pyfixest` (saturated TWFE with cohort×time interactions). This addresses
      the negative-weight problem under staggered adoption and is available in
      the existing Python stack. If access to R is available, the preferred
      implementation is the doubly-robust C&S estimator via the `did` CRAN
      package called through `rpy2` — add `rpy2` to pyproject.toml and document
      the R ≥4.2 + `did` dependency if this route is taken. Do not implement
      C&S from scratch.
    - Aggregate ATT(g,t) to overall ATT and event-study plot (τ_-3 to τ_+3).
      Note on cohort informativeness: EIBIS begins in 2016 (wave 1). Cohorts
      first treated in wave 1 have zero pre-treatment periods and are excluded
      from the event-study plot entirely (included in ATT aggregation only).
      Cohorts first treated in wave 2 (2017) have one pre-treatment period —
      they appear in the plot at τ_-1 but cannot support a formal pre-trend test.
      Only cohorts first treated in wave 3 (2018) or later fully populate the
      pre-treatment side of the plot. State this explicitly in the figure caption.
    - Pre-trend test: pre-treatment coefficients statistically indistinguishable
      from zero. Shared with pretrend.py.

    Balance table (run before estimation):
    - Compare firm-level observables (size_class, nace2, country, wave of first
      observation as age proxy) across early-treated cohorts vs not-yet-treated
      firms at baseline. Large imbalances weaken the parallel trends assumption
      even if pre-trend tests pass. Report in outputs/tables/phase2_cs_balance.csv
      and note any imbalances in table footnotes.
    - Report the share of firms with eib_support == 1 by wave. If the treated
      share exceeds 40% in any wave, the not-yet-treated comparison group is thin
      and potentially selected — flag to human and run a sensitivity check pooling
      never-treated and not-yet-treated firms as an alternative comparison group.
      Note: if EIB intermediated support is as widespread as the AIM framework
      suggests (~80% climate-tagged), the not-yet-treated pool may be small by
      later waves, which would substantially constrain C&S power.

    → src/analysis/cs_estimation.py
    → outputs/tables/phase2_cs_att.csv
    → outputs/tables/phase2_cs_balance.csv
    → outputs/figures/phase2_cs_event_study.png

[ANALYSIS — SUPPLEMENTARY: Bartik IV at country FE]
    Bartik identifies off cross-regional variation in predetermined industrial
    structure interacted with EU-level EIB sectoral lending shifts. With firm FE
    and year FE, the identifying variation is within-country deviations from the
    EU-wide time trend — thin at 27 countries. Bartik is therefore run here at
    country×year level with country FE and year FE (not firm FE), serving as an
    external validity check: do regions more exposed to EIB sectoral lending
    shocks show higher green investment, controlling for country and year?
    Convergence with C&S strengthens the causal interpretation.

    This is an ecological correlation at country×year level — a different estimand
    from the firm-level C&S ATT. Label it explicitly as such in output tables.

    The 2SLS structure is:
    - Outcome:             green_inv_share_ct  (country×year mean from EIBIS)
    - Endogenous regressor: EIB_volume_per_SME_ct (actual EIB signed amount per
                           SME at country×year, same construction as Phase 1 LHS)
    - Instrument:          Bartik_ct (predetermined exposure — exogenous to any
                           single region's green investment decisions)

    First stage:
        EIB_volume_per_SME_ct = π·Bartik_ct + γ·log(GDP_pc_ct) + δ_c + θ_t + u_ct
    Report π and first-stage F. F > 10 required to proceed to second stage.

    Second stage:
        green_inv_share_ct = β·EIB_volume_per_SME_hat_ct + γ·log(GDP_pc_ct)
                             + δ_c + θ_t + ε_ct

    OLS baseline (same equation, replacing fitted values with actuals). Wild
    cluster bootstrap p-values for both OLS and 2SLS (27 clusters).

    The OLS/2SLS gap is informative but not a clean additionality test: 2SLS > OLS
    is consistent with negative selection bias in OLS (EIB targets regions that
    would have invested less green absent support), but equally consistent with
    OLS attenuation from measurement error, or LATE for Bartik compliers exceeding
    the average. Note this interpretation explicitly in output table footnotes.
    → src/analysis/iv_estimation.py
    → outputs/tables/phase2_iv_main.csv
    → outputs/tables/phase2_iv_heterogeneity.csv

[ANALYSIS — Pre-trend test]
    → src/analysis/pretrend.py
    → outputs/figures/phase2_pretrend_plot.png
    ↓
[OUTPUTS]
Commit: "phase2: complete — C&S and Bartik IV results written"
```

---

## Phase 3 Task Graph

**Aspirational. Begin only if ORBIS access is confirmed by human.**

```
[INGEST] ORBIS via BvD ID merge with EIBIS
    → src/ingest/orbis_merge.py
    → data/raw/orbis_linked_<date>.csv
    ↓
[ANALYSIS] Phase 2 regressions + firm financial controls
    → src/analysis/phase3_robustness.py
    ↓
[OUTPUTS]
→ outputs/tables/robustness_firm_controls.csv
Commit: "phase3: complete — robustness results written"
```

---

## Coding Standards

- All functions have a docstring stating: inputs, outputs, and side effects.
- All scripts are runnable standalone: `uv run python src/ingest/eib_projects.py`
- No hardcoded paths. Use `pathlib.Path` and define root in a `config.py`:

```python
# src/config.py
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS_FIGURES = ROOT / "outputs" / "figures"
OUTPUTS_TABLES = ROOT / "outputs" / "tables"

# Create directories if they don't exist
for d in [DATA_RAW, DATA_INTERIM, DATA_PROCESSED, OUTPUTS_FIGURES, OUTPUTS_TABLES]:
    d.mkdir(parents=True, exist_ok=True)
```

- All DuckDB connections use context managers:
```python
import duckdb
with duckdb.connect("data/processed/eib_analysis.duckdb") as con:
    con.execute("...")
```

- For regressions with fewer than 40 clusters, do not rely on analytic
  cluster-robust SEs alone (downward bias per Cameron, Gelbach & Miller 2008).
  Use wild cluster bootstrap (Webb 6-point weights) for p-values, implemented
  via `pyfixest`'s `wildboottest` argument or a shared utility function in
  `src/analysis/inference_utils.py`. Report both analytic and bootstrap p-values
  in all output tables. This applies to all Phase 1 country-level regressions
  (27 clusters) and Phase 2 Bartik supplementary analysis.

- Figures are saved at 150 dpi minimum, bbox_inches='tight', to
  `outputs/figures/<phase>_<description>.png`. Never use `plt.show()` in
  scripts — always save to file.

- Tables are saved as CSV to `outputs/tables/<phase>_<description>.csv`.
  Also print a formatted version to stdout for quick inspection.

---

## What to Ask the Human

Stop and ask the human (do not guess, do not proceed) when:

1. A feasibility check produces an ambiguous result not covered by the decision
   rules above.
2. A data source returns unexpected schema — column names, units, or coverage
   differ materially from what is specified in this document.
3. A network request is ready to execute (log URL, wait for confirmation).
4. Check 7 returns F < 10 and neither Fix A nor Fix B is immediately applicable.
5. Any result looks implausible — e.g., targeting regression returns a large
   negative coefficient on constraint severity (EIB lends less where constraints
   are worse), which would be a substantively important finding requiring human
   review before proceeding.
6. EIBIS microdata arrives and columns differ from the expected schema listed
   in Phase 2.
7. You are about to modify a file that another parallel agent has declared
   ownership of in the implementation log.

**Do not ask the human about:**
- Which package to use for a standard task (use what is in pyproject.toml)
- Code style questions (ruff handles this)
- Whether to commit (commit autonomously after each logical unit)
- Exploratory questions about the research design (answer is in this document;
  if not covered, check README.md; if still not covered, ask)

---

## Instructions for Cowork

The following items are not yet fully specified and require Cowork to clarify
with the human before acting:

1. **README narrative thread:** When drafting README.md, lead with the following
   research question — it is the framing that connects Phase 1, Phase 2b, and
   Phase 2 into a single coherent evaluation:

   > "The EIB tags approximately 80% of its intermediated SME support as
   > 'climate-aligned,' but the SME evaluation finds weak incentives for
   > intermediaries to shift firm behavior. This project tests whether
   > EIB climate-tagged lending actually changes firm green investment —
   > or whether it merely relabels existing financial flows."

   This framing positions the project as an evaluation of behavioral additionality,
   not just an impact study, and is the question most likely to resonate with a
   senior EIB evaluation officer. Phase 1 establishes the targeting baseline
   (does EIB go where market failures are worst?). Phase 2b tests the aggregate
   reduced-form (does regional EIB exposure reduce financing constraints?). Phase
   2 tests the firm-level behavioral question (does receiving EIB support cause
   firms to invest more in green activities?). The three phases answer the same
   question at increasing levels of causal credibility and data intensity.

2. **README contribution statement:** Include a brief positioning relative to the
   two closest existing EIB impact studies. Suggested wording:

   > "Amamou et al. (2020) use propensity-score matching with difference-in-
   > differences and find positive employment effects of EIB lending, but cannot
   > address staggered adoption or test the green investment mechanism. Barbera
   > et al. (2022) use a generalized propensity score for continuous treatment
   > intensity but rely on the same matching identification. This project improves
   > on both by (a) using the Callaway-Sant'Anna estimator to address the
   > negative-weight problem under staggered treatment adoption, (b) using a
   > Bartik instrument that exploits exogenous EU-level sectoral variation rather
   > than firm-level matching on observables, and (c) testing the green investment
   > additionality question — whether EIB climate-tagged lending changes firm
   > behaviour or merely relabels existing flows — that neither paper examines."

3. **Repo initialisation — full sequence:**

   **Step 0 — Verify prerequisites before touching the filesystem.**
   Check that `uv`, `git`, and `gh` (GitHub CLI) are available:
   ```
   uv --version
   git --version
   gh --version
   ```
   If `uv` is missing: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
   If `gh` is missing: install via https://cli.github.com. Do not proceed
   until all three are present.

   **Step 1 — Create the GitHub repository first.**
   The remote must exist before the local init so the URL is known in time
   to write the README permalink (which depends on the hash from the next
   step). Run:
   ```
   gh repo create eib-seclending --private
   ```
   This creates the remote. Do not clone — local init follows separately.
   Ask the human to confirm visibility (private vs public) before running.

   **Step 2 — Local init and infrastructure commit.**
   From inside the `eib-seclending/` directory the human has already created:
   ```
   git init
   git remote add origin https://github.com/<owner>/eib-seclending.git
   uv init
   uv add pandas polars duckdb requests beautifulsoup4 pdfplumber \
          eurostat geopandas contextily matplotlib seaborn \
          statsmodels linearmodels pyfixest scipy numpy jupyter
   uv add --dev pre-commit ruff
   ```
   Then create `.gitignore` and `.pre-commit-config.yaml` exactly as
   specified in this document. Create the directory skeleton with
   `.gitkeep` files so git tracks the empty directories:
   ```
   mkdir -p src/ingest src/analysis src/viz
   mkdir -p outputs/figures outputs/tables
   touch src/ingest/.gitkeep src/analysis/.gitkeep src/viz/.gitkeep
   touch outputs/figures/.gitkeep outputs/tables/.gitkeep
   ```
   Install pre-commit hooks:
   ```
   uv run pre-commit install
   ```
   Stage and commit everything so far:
   ```
   git add pyproject.toml .gitignore .pre-commit-config.yaml \
           src/ outputs/
   git commit -m "chore: initialise repository structure and environment"
   git push -u origin main
   ```

4. **Pre-registration commit — exact sequence, no shortcuts.**

   Copy `prespec-plan.md` into the repo root. Then stage only that file:
   ```
   git add prespec-plan.md
   git commit -m "Registered primary specifications in prespec-plan.md before start of analysis"
   git push
   ```
   Immediately record the hash:
   ```
   git rev-parse HEAD
   ```
   This 40-character string is the pre-registration hash. The push
   timestamp on GitHub is the verifiable server-side record.

   **Pre-commit hook behaviour on this commit:** The hooks run on
   `prespec-plan.md` as on any other file. `ruff` lints Python only, so
   the Markdown file is ignored by it. The `trailing-whitespace` and
   `end-of-file-fixer` hooks will, however, silently fix any trailing
   spaces or missing final newline in the file — and when they do, the
   commit is aborted (hooks that modify files always abort the first
   attempt). This is not an error. Simply re-run:
   ```
   git add prespec-plan.md
   git commit -m "Registered primary specifications in prespec-plan.md before start of analysis"
   ```
   The second attempt succeeds because the file is now clean. The
   substantive content is unchanged; only invisible whitespace was
   corrected. Push immediately after.

   **After the push:** Write `README.md` — and only now, because the hash
   and remote URL are both known. Add the two blocks specified in the
   Pre-Analysis Plan section of this document, substituting the actual
   40-character hash and `<owner>/eib-seclending`. Ask the human to
   confirm the hash before writing it into the README. Commit:
   ```
   git add README.md
   git commit -m "docs: add README with research question and pre-registration link"
   git push
   ```
   After this commit, no further changes to `prespec-plan.md` are
   permitted. All subsequent work proceeds per the Phase 1 task graph.

5. **Annual Report URL pattern:** The URL pattern
   `https://www.eib.org/attachments/publications/annual_report_<year>_en.pdf`
   is approximate. Verify the exact URL for 2023 and 2015 by checking the EIB
   website manually. Update `src/ingest/eib_annual_reports.py` with the confirmed
   pattern before running any downloads. Ask human to verify URLs before fetching.

6. **EIBIS aggregate download:** The EIBIS data portal (data.eib.org/eibis/graph)
   requires manual navigation to select indicators and export. Cowork should:
   (a) confirm with the human which exact indicators to download (list in Check 4
   section of this document), (b) confirm whether the portal has changed its
   export interface since this document was written, (c) assist the human with
   the download if the portal does not support automated export.

7. **Cohesion eligibility PDFs:** DG REGIO publishes cohesion region eligibility
   as PDF annexes to regulations. These require manual extraction into
   `data/raw/cohesion_eligibility.csv`. Cowork should locate the correct PDFs
   for programming periods 2007–2013, 2014–2020, and 2021–2027, confirm URLs
   with the human, and assist with extraction. The CSV schema should be:
   `nuts2_code, nuts2_name, country, period, category` where category is one of
   `less_developed`, `transition`, `more_developed`.

8. **NUTS-2 shapefile:** For the constraint map (Beat 1), download the Eurostat
   GISCO NUTS-2 shapefile. Confirm the correct vintage (2021 boundaries) and
   projection (EPSG:4326) with the human. URL:
   https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_20M_2021_4326.shp.zip
   Save to `data/raw/nuts2_shapefile/`. Ask human to confirm before downloading.
