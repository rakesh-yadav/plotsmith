"""Generate 13 benchmark datasets spanning time series, comparison, distribution, ML."""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True, parents=True)


# ============================================================================
# 01) TIME SERIES (single) with event annotations - DAU over 18 months
# ============================================================================
dates = pd.date_range("2024-01-01", "2025-06-30", freq="D")
n = len(dates)
trend = np.linspace(85_000, 142_000, n)
weekly = 6_000 * np.sin(np.arange(n) * 2 * np.pi / 7)
yearly = 4_000 * np.sin(np.arange(n) * 2 * np.pi / 365)
noise = rng.normal(0, 2_500, n)
dau = trend + weekly + yearly + noise

# event impulses
events = [
    ("2024-04-15", "v2 launch",        18_000),
    ("2024-09-10", "Pricing change",   -9_000),
    ("2025-02-20", "Mobile app",       22_000),
]
for ev_date, _, amp in events:
    idx = (dates == pd.Timestamp(ev_date)).argmax()
    decay = np.exp(-np.arange(n - idx) / 28)
    dau[idx:] += amp * decay

ts1 = pd.DataFrame({"date": dates, "dau": dau.astype(int)})
ts1.to_csv(OUT / "01_dau_timeseries.csv", index=False)
pd.DataFrame(events, columns=["date", "label", "_amp"]).drop(columns="_amp").to_csv(
    OUT / "01_dau_events.csv", index=False
)


# ============================================================================
# 02) MULTI-SERIES TIME SERIES (highlight pattern) - revenue by region, monthly
# ============================================================================
months = pd.date_range("2023-01-01", "2025-06-01", freq="MS")
regions = ["North America", "Europe", "LATAM", "APAC", "MEA", "ANZ"]
base = {"North America": 12.0, "Europe": 9.0, "LATAM": 3.2, "APAC": 7.5, "MEA": 2.1, "ANZ": 2.8}
growth = {"North America": 0.018, "Europe": 0.011, "LATAM": 0.022, "APAC": 0.034, "MEA": 0.009, "ANZ": 0.014}
rows = []
for r in regions:
    series = []
    v = base[r]
    for i, m in enumerate(months):
        v = v * (1 + growth[r] + rng.normal(0, 0.012))
        rows.append({"month": m, "region": r, "revenue_musd": round(v, 2)})
ts2 = pd.DataFrame(rows)
ts2.to_csv(OUT / "02_regional_revenue.csv", index=False)


# ============================================================================
# 03) STACKED AREA - traffic source mix over time (monthly, 24 months)
# ============================================================================
mo = pd.date_range("2023-07-01", "2025-06-01", freq="MS")
nm = len(mo)
# total sessions trending up
total = np.linspace(420_000, 920_000, nm) + rng.normal(0, 18_000, nm)
# evolving mix - organic stable, paid declining, email + social rising
mix = pd.DataFrame({
    "month":   mo,
    "Organic search": total * np.linspace(0.42, 0.36, nm),
    "Paid search":    total * np.linspace(0.26, 0.17, nm),
    "Social":         total * np.linspace(0.10, 0.21, nm),
    "Email":          total * np.linspace(0.08, 0.14, nm),
    "Direct":         total * np.linspace(0.10, 0.09, nm),
    "Referral":       total * np.linspace(0.04, 0.03, nm),
})
mix.iloc[:, 1:] = mix.iloc[:, 1:].round().astype(int)
mix.to_csv(OUT / "03_traffic_mix.csv", index=False)


# ============================================================================
# 04) HORIZONTAL BAR (ranking) - top 15 product categories by revenue
# ============================================================================
cats = ["Smartphones","Laptops","Headphones","Smart TVs","Tablets","Gaming consoles",
        "Cameras","Smartwatches","Speakers","Printers","Routers","Drones",
        "E-readers","VR headsets","Monitors"]
rev = np.sort(rng.lognormal(2.4, 0.7, len(cats)))[::-1] * 4.2
bar_df = pd.DataFrame({"category": cats, "revenue_musd": np.round(rev, 1)})
bar_df = bar_df.sort_values("revenue_musd", ascending=False).reset_index(drop=True)
bar_df.to_csv(OUT / "04_category_revenue.csv", index=False)


# ============================================================================
# 05) SLOPE CHART (two-period comparison) - country GDP per capita 2023 vs 2024
# ============================================================================
countries = ["USA","Germany","Japan","UK","France","Canada","Australia","S. Korea",
             "Italy","Spain","Netherlands","Poland","Mexico","Brazil","Turkey"]
gdp_2023 = np.array([76.4, 52.7, 33.8, 48.9, 44.5, 53.2, 65.1, 33.1, 38.4, 32.6, 56.7, 22.0, 11.5, 9.7, 12.9])
moves   = np.array([+3.1, -1.4, -2.3, +2.0, +0.6, +1.8, +2.4, +1.1, -0.9, -1.6, +2.1, +1.7, +0.4, -0.8, -2.1])
gdp_2024 = gdp_2023 + moves
slope_df = pd.DataFrame({"country": countries, "gdp_2023_k": gdp_2023, "gdp_2024_k": gdp_2024})
slope_df.to_csv(OUT / "05_gdp_slope.csv", index=False)


# ============================================================================
# 06) WATERFALL - Q3 -> Q4 revenue bridge (same as v1 but renamed)
# ============================================================================
waterfall = pd.DataFrame({
    "label": ["Q3 Revenue", "New customers", "Expansion", "Price increase",
              "Churn", "Downgrades", "FX impact", "Q4 Revenue"],
    "type":  ["total", "delta", "delta", "delta", "delta", "delta", "delta", "total"],
    "value": [48.2, 6.4, 3.8, 1.9, -2.1, -1.3, -0.7, 56.2],
})
waterfall.to_csv(OUT / "06_waterfall.csv", index=False)


# ============================================================================
# 07) HISTOGRAM / KDE - customer LTV distribution by 3 segments (long-tailed)
# ============================================================================
segs = {
    "SMB":        (np.log(800),  0.7, 4_000),
    "Mid-market": (np.log(3500), 0.6, 2_500),
    "Enterprise": (np.log(28000), 0.5, 800),
}
records = []
for seg, (mu, sigma, n_seg) in segs.items():
    vals = rng.lognormal(mean=mu, sigma=sigma, size=n_seg)
    for v in vals:
        records.append({"segment": seg, "ltv_usd": round(v, 2)})
ltv_df = pd.DataFrame(records)
ltv_df.to_csv(OUT / "07_ltv_distribution.csv", index=False)


# ============================================================================
# 08) BOX PLOT BY GROUP - salary distribution across 8 departments
# ============================================================================
depts = {
    "Engineering": (152, 38, 220),
    "Data Science":(148, 34, 180),
    "Product":     (138, 32, 95),
    "Design":      (118, 28, 70),
    "Marketing":   (104, 26, 110),
    "Sales":       (122, 45, 160),   # high variance from commission
    "Support":     (78,  18, 145),
    "Operations":  (92,  22, 88),
}
sal_rows = []
for d, (mu, sd, n_d) in depts.items():
    vals = rng.normal(mu, sd, n_d).clip(40, None)
    for v in vals:
        sal_rows.append({"department": d, "salary_k": round(v, 1)})
sal_df = pd.DataFrame(sal_rows)
sal_df.to_csv(OUT / "08_salary_by_dept.csv", index=False)


# ============================================================================
# 09) SCATTER WITH REGRESSION - marketing spend vs new customers, 40 cities
# ============================================================================
cities = ["NYC","LA","Chicago","Houston","Phoenix","Philly","SD","Dallas","Austin","SJ",
          "Seattle","Denver","Boston","Portland","Vegas","Atlanta","Miami","DC","Charlotte","Detroit",
          "Minneapolis","Tampa","Orlando","Pittsburgh","Cincinnati","Cleveland","Indianapolis","Columbus",
          "Kansas City","Nashville","Memphis","Louisville","Milwaukee","Baltimore","Richmond","Raleigh",
          "St. Louis","Salt Lake","OKC","Albuquerque"]
spend = rng.uniform(40, 380, len(cities))                       # $k
slope = 4.6
intercept = -55
noise = rng.normal(0, 95, len(cities))
new_cust = (intercept + slope * spend + noise).clip(0, None).round().astype(int)
sc_df = pd.DataFrame({"city": cities, "spend_k": np.round(spend, 1), "new_customers": new_cust})
sc_df.to_csv(OUT / "09_spend_vs_customers.csv", index=False)


# ============================================================================
# 10) CORRELATION HEATMAP - 10 mixed customer features (carried from v1)
# ============================================================================
n_c = 800
age = rng.normal(38, 11, n_c).clip(18, 75)
income = (25_000 + 1_200 * age + rng.normal(0, 15_000, n_c)).clip(15_000, None)
tenure = rng.exponential(3, n_c).clip(0, 20)
sessions = rng.poisson(np.maximum(2, 12 - 0.1 * age + 0.4 * tenure), n_c)
purchases = rng.poisson(np.maximum(0.2, sessions * 0.08 + income / 80_000), n_c)
basket = (40 + 0.0008 * income + 1.4 * tenure + rng.normal(0, 12, n_c)).clip(5, None)
revenue = purchases * basket + rng.normal(0, 30, n_c)
tickets = rng.poisson(np.maximum(0.1, 1.8 - 0.04 * tenure + 0.02 * sessions), n_c)
nps = (8 - 0.06 * tickets + 0.05 * tenure + rng.normal(0, 1.4, n_c)).clip(0, 10)
churn = (1 / (1 + np.exp(-(0.4 * tickets - 0.18 * tenure - 0.0015 * revenue + rng.normal(0, 0.6, n_c))))).clip(0, 1)
feats = pd.DataFrame({
    "age": age, "income": income, "tenure_yrs": tenure,
    "sessions_30d": sessions, "purchases_30d": purchases,
    "basket_size": basket, "revenue_30d": revenue,
    "support_tickets": tickets, "nps_score": nps, "churn_risk": churn,
})
feats.to_csv(OUT / "10_features.csv", index=False)


# ============================================================================
# 11) COHORT RETENTION TRIANGLE (carried from v1)
# ============================================================================
cohorts = pd.date_range("2024-01-01", "2024-12-01", freq="MS").strftime("%Y-%m").tolist()
max_age = 12
records = []
for i, cohort in enumerate(cohorts):
    base_r = 100.0
    decay = 0.18 + 0.005 * (len(cohorts) - i)
    floor = 22 + 0.6 * i
    for age in range(max_age + 1):
        if i + age >= len(cohorts):
            records.append({"cohort": cohort, "age_months": age, "retention_pct": np.nan})
            continue
        if age == 0:
            r = 100.0
        else:
            r = max(floor, base_r * np.exp(-decay * age) + rng.normal(0, 1.2))
        records.append({"cohort": cohort, "age_months": age, "retention_pct": round(r, 1)})
pd.DataFrame(records).to_csv(OUT / "11_cohort_retention.csv", index=False)


# ============================================================================
# 12) ROC CURVES + 13) FEATURE IMPORTANCE - shared ML setup
# ============================================================================
X, y = make_classification(
    n_samples=4_000, n_features=14, n_informative=8, n_redundant=3,
    weights=[0.78, 0.22], class_sep=0.9, random_state=42,
)
feature_names = [
    "tenure_yrs","monthly_charges","support_tickets","n_logins","discount_used",
    "contract_length","age","payment_failures","feature_adoption","nps_score",
    "competitor_visits","data_usage_gb","referrals_made","billing_disputes",
]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000),
    "Random Forest":       RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=200, random_state=42),
}
roc_rows = []
for name, m in models.items():
    m.fit(X_train, y_train)
    p = m.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, p)
    a = auc(fpr, tpr)
    for f_, t_ in zip(fpr, tpr):
        roc_rows.append({"model": name, "fpr": f_, "tpr": t_, "auc": a})
pd.DataFrame(roc_rows).to_csv(OUT / "12_roc_curves.csv", index=False)

B = 50
boot_imp = np.zeros((B, X.shape[1]))
for b in range(B):
    idx = rng.integers(0, len(X_train), len(X_train))
    rf_b = RandomForestClassifier(n_estimators=150, random_state=b, n_jobs=-1)
    rf_b.fit(X_train[idx], y_train[idx])
    boot_imp[b] = rf_b.feature_importances_
fi_df = pd.DataFrame({
    "feature": feature_names,
    "importance": boot_imp.mean(axis=0),
    "ci_low":  np.quantile(boot_imp, 0.025, axis=0),
    "ci_high": np.quantile(boot_imp, 0.975, axis=0),
}).sort_values("importance", ascending=False).reset_index(drop=True)
fi_df.to_csv(OUT / "13_feature_importance.csv", index=False)


# ============================================================================
# 14) (also 13th chart) KAPLAN-MEIER SURVIVAL - 3 treatment arms, 24-mo follow-up
# Generate raw (time, event, group) so the agent does the K-M math.
# ============================================================================
def gen_arm(n_arm, hazard, name):
    t_event = rng.exponential(1 / hazard, n_arm)
    t_cens  = rng.uniform(0, 24, n_arm)
    t = np.minimum(t_event, t_cens)
    e = (t_event <= t_cens).astype(int)
    return pd.DataFrame({"time_months": np.round(t, 2), "event": e, "arm": name})
km = pd.concat([
    gen_arm(220, 0.040, "Control"),
    gen_arm(218, 0.028, "Treatment A"),
    gen_arm(214, 0.020, "Treatment B"),
], ignore_index=True)
km.to_csv(OUT / "14_survival.csv", index=False)


print("Generated:")
for f in sorted(OUT.glob("*.csv")):
    print(f"  {f.name}  ({f.stat().st_size:>7} bytes)")
