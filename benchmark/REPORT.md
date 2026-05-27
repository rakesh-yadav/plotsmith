# PlotSmith vs Baseline — Benchmark

A stress-test of the [`plotsmith`](../.claude/agents/plotsmith.md) agent
definition vs. a vanilla general-purpose Claude agent. Same Claude model,
same one-sentence prompt, 14 chart types spanning data analytics,
business analytics, data science, and machine learning.

## Setup

**14 chart types**, one per dataset in [`data/`](data):

| # | Chart type                                  | Domain              |
|---|---------------------------------------------|---------------------|
| 01 | Single-series time series + event markers  | Data analytics      |
| 02 | Multi-series time series (highlight)        | Data analytics      |
| 03 | Stacked area (composition over time)        | Data analytics      |
| 04 | Horizontal bar ranking                      | Business analytics  |
| 05 | Slope chart (two-period)                    | Business analytics  |
| 06 | Waterfall (period bridge)                   | Business analytics  |
| 07 | LTV distribution by segment                 | Data science        |
| 08 | Boxplot by group                            | Data science / HR   |
| 09 | Scatter w/ OLS regression                   | Data science        |
| 10 | Correlation heatmap                         | Data science        |
| 11 | Cohort retention triangle                   | Product analytics   |
| 12 | ROC curves (multi-model)                    | Machine learning    |
| 13 | Feature importance w/ bootstrap CIs         | Machine learning    |
| 14 | Kaplan-Meier survival                       | Clinical / ML       |

Both runs used `general-purpose` Claude sub-agents on Opus 4.7. The
PlotSmith side was instructed to read the agent manual in full before
starting; the baseline received only the terse task prompt. Data
generation is deterministic (`seed=42`) — see
[`generate_data.py`](generate_data.py).

## Headline

| #  | Chart                  | Winner    | Margin |
|----|------------------------|-----------|--------|
| 01 | DAU time series        | PlotSmith | Medium |
| 02 | Regional revenue       | PlotSmith | Small  |
| 03 | Traffic mix stacked    | PlotSmith | Medium |
| 04 | Top-15 bar ranking     | PlotSmith | Medium |
| 05 | GDP slope              | PlotSmith | Medium |
| 06 | Waterfall              | PlotSmith | Medium |
| 07 | LTV distribution       | PlotSmith | Large  |
| 08 | Salary by department   | PlotSmith | Medium |
| 09 | Spend scatter          | Tie       | —      |
| 10 | Correlation heatmap    | PlotSmith | Large  |
| 11 | Cohort retention       | PlotSmith | Medium |
| 12 | ROC curves             | PlotSmith | Medium |
| 13 | Feature importance     | PlotSmith | Medium |
| 14 | Kaplan-Meier survival  | PlotSmith | Large  |

**Score: PlotSmith 13, Tie 1.**

## Cost

| Agent     | Avg tool calls / chart | Avg duration / chart |
|-----------|------------------------|----------------------|
| Baseline  | 8                      | ~55 s                |
| PlotSmith | 14                     | ~115 s               |

PlotSmith costs ~1.8× more wall-clock and ~1.7× more tool calls. The
low-res preview strategy in the agent manual reduces verification-Read
tokens ~3× per iteration. Most PlotSmith agents converge in 1–2
iterations.

## Per-chart observations

### 01 — DAU time series with event annotations
- **Baseline**: descriptive title "Daily Active Users"; bottom-right
  legend (Daily / 7-day avg) eats vertical space; event labels boxed.
- **PlotSmith**: insight title *"DAU grew +67% over 18 months, lifted by
  product releases"*; subtitle replaces the legend; latest value *141K*
  direct-labeled at the right edge.

### 02 — Multi-series regional revenue (highlight)
The closest pair. Both produced insight titles and highlighted APAC.
- **Baseline**: APAC in red, in-chart annotation.
- **PlotSmith**: APAC in accent blue per palette rules; every region
  direct-labeled with latest value (`$20.1M`, `$19.6M`, …); ticks
  formatted `$NM`.

### 03 — Traffic mix stacked area
- **Baseline**: descriptive title; default categorical palette;
  multi-column legend that overlaps the bands.
- **PlotSmith**: insight title *"Social doubled its share as total
  traffic grew 112%"*; Okabe-Ito colorblind-safe palette; every band
  direct-labeled at the right edge with latest share %; no legend.

### 04 — Horizontal bar ranking (top-15 categories)
- **Baseline**: every bar same blue; descriptive title.
- **PlotSmith**: leader in accent blue, peers in muted grey — visual
  hierarchy maps to ranking; insight title with leader share; `$M`
  formatted ticks.

### 05 — GDP slope chart
- **Baseline**: gainers green / losers red; label collisions at the low
  end (Germany/Canada and Spain/Japan overprint).
- **PlotSmith**: Okabe-Ito blue/orange (colorblind-safe); collision-
  aware vertical stagger with leader lines; ranked left-to-right;
  insight title quantifies how many countries grew.

### 06 — Waterfall
- **Baseline**: 3-item legend (Total / Increase / Decrease) — redundant
  with color; generic title.
- **PlotSmith**: insight title quantifies the net delta and the
  dominant driver; bold totals; dashed grey connectors; no legend.

### 07 — LTV distribution (long-tailed, 3 segments)
**Largest gap in the set.**
- **Baseline**: overlapping histograms on log x-axis. Three colored
  distributions overlap heavily; legend has to carry n + medians.
- **PlotSmith**: substituted a horizontal boxplot on log x — strictly
  better for 3-segment comparison. Medians directly visible, whiskers
  show spread, n in y-tick labels, focal segment in accent blue.

### 08 — Salary by department (8 groups)
- **Baseline**: vertical boxplots with jittered scatter behind; legend
  for Median/Mean markers; same color for all boxes.
- **PlotSmith**: horizontal boxplots (better when group labels are
  long); sorted by median; top-median dept in accent blue; n shown in
  tick labels; medians in a right-edge "Median" column.

### 09 — Scatter with OLS regression — TIE
- **Baseline**: scatter with OLS line + equation + R² in legend; 3
  notable cities annotated. Genuinely well-executed.
- **PlotSmith**: scatter with OLS line + 95% CI band; Pearson r and
  slope in subtitle. Both publication-quality.

### 10 — Correlation heatmap
- **Baseline**: full square (mirrored) with every cell annotated —
  noisy; colorbar in a separate right column; small text.
- **PlotSmith**: lower-triangle only; selective annotation (only
  `|r|≥0.30` labeled, bold ≥0.60); white cell borders; colorbar inset
  into the masked triangle (no wasted column); insight title surfaces
  the load-bearing pairs.

### 11 — Cohort retention triangle
- **Baseline**: large readable triangle, but title overlaps subtitle
  and colorbar sits in a separate right column.
- **PlotSmith**: insight title that quantifies the plateau; calibrated
  figsize (8.2 × 5.6) per the table formula; colorbar parked
  horizontally inside the NaN triangle region; per-cell percentages
  with luminance-aware text color; clean triangle silhouette.

### 12 — ROC curves
- **Baseline**: three saturated colors (red/green/blue), all solid lines
  — colorblind-unsafe; generic title.
- **PlotSmith**: focal model (Random Forest) in accent blue solid,
  peers in dashed orange and dotted grey (Okabe-Ito + redundant line
  styles); inline "chance" label; insight title quantifies the winner.

### 13 — Feature importance with bootstrap CIs
- **Baseline**: top-3 highlighted in barely-darker blue (invisible
  hierarchy); raw `0.104` decimals; legend item for "Top 3" that's
  hard to map.
- **PlotSmith**: top feature in bold accent blue, peers in muted grey;
  `%` ticks; two-sided CI error bars; insight title surfaces top
  drivers.

### 14 — Kaplan-Meier survival
- **Baseline**: solid curves; legend in lower-left with n per arm.
  Clean enough.
- **PlotSmith**: focal arm in accent blue solid, peers in dashed
  orange and dotted grey (Okabe-Ito + redundant line styles); direct
  labels at right edge with milestone survival per arm; 50% median
  reference + 12-mo milestone line; insight title quantifies the lift.

## What the agent definition consistently buys

1. **Insight-bearing titles + decision-grade subtitles.** Every
   PlotSmith chart leads with a sentence-form finding. Baseline titles
   describe axes.
2. **Color discipline.** One accent for the focal series, greys for
   peers, Okabe-Ito for the categorical palette when > 3 distinct hues
   are needed. Baseline uses equal-weight saturated palettes that force
   the reader to chase the legend.
3. **Direct labels over legends.** Replaces ~6 of the 14 legends with
   right-edge labels that don't compete with data.
4. **Whitespace economy.** Colorbar inside the masked region for
   heatmap charts (10, 11) eliminates a 1″+ empty column the baseline
   leaves on both.
5. **Colorblind safety.** Line styles + color (charts 12, 14) instead
   of color alone; Okabe-Ito palettes for ≥ 4 categorical series.
6. **Chart-type substitutions.** Chart 07 (LTV) switched from
   overlapping histograms to a horizontal boxplot; chart 08 (salary)
   from vertical to horizontal boxplots — both are strict improvements
   the prompt didn't ask for.

## When to use it, when not to

**Use** for any chart that will be seen by someone who didn't help
generate it — execs, customers, public reports, README hero images.

**Don't bother** for ad-hoc EDA, sanity scatters, or charts you're
going to look at once and throw away. The ~1.8× cost premium is a
poor trade for one-look plots.
