<<<<<<< HEAD
# Cow-production-simulator     
=======
# 🐄 Cow Production Simulator

A fully interactive, data-driven simulation of cattle lifecycle management — from birth to either slaughter or culling — built in Python with a Streamlit web interface. This project models the biological, financial, and health dynamics of a mixed dairy/beef herd over time, and includes a Monte Carlo engine for strategy comparison.

---

## 📌 Project Overview

This simulator was built as a portfolio project to demonstrate applied systems thinking, object-oriented programming, simulation design, and data visualization. It models the complete lifecycle of individual cows within a herd, tracking biological growth, health events, feed quality, veterinary treatment, and financial performance — all simultaneously.

The project is split into a clean modular architecture:

| File | Purpose |
|------|---------|
| `cow.py` | Core `Cow` class — state, lifecycle logic, health system |
| `simulation.py` | Herd generation and simulation runner |
| `metrics.py` | Herd-level aggregation and evaluation |
| `Monte_Carlo.py` | Monte Carlo engine for strategy comparison |
| `app.py` | Streamlit web application and dashboard |

---

## 🧬 Biological Model

Each cow is initialized at birth with a **genetic multiplier (GM)** — a randomly drawn float between 0.85 and 1.15 — that scales its growth rate and milk yield throughout its entire life. This represents natural genetic variation between individual animals in a real herd.

### Life Stages

The simulation runs on a **monthly time step**. Each cow moves through the following stages:

```
Birth → Calf (0–2 months)
     → Growing (2–12 months for beef / 2–15 months for dairy)
     → Finishing (beef only, until slaughter weight ~600kg)
     → Lactating (dairy only, 10 months per cycle)
     → Dry (dairy only, 2 months between lactation cycles)
     → Slaughtered / Culled (terminal event)
```

#### Stage Parameters

| Stage | Daily Gain | Duration | Revenue |
|-------|-----------|----------|---------|
| Calf | ~0.9 kg/day | 2 months | None |
| Growing | ~0.8 kg/day | 10–13 months | None |
| Finishing (beef) | ~1.2 kg/day | Until 600kg | Terminal sale |
| Lactating (dairy) | Minimal | 10 months/cycle | Milk revenue |
| Dry (dairy) | None | 2 months/cycle | None |

Dairy cows complete **4 lactation cycles** before being culled. Beef cows are slaughtered once they reach **600kg**.

---

## 🌾 Feed Type System

Three feed types are available, each affecting growth rate, feed cost, illness probability, stress drift, and revenue quality:

| Feed Type | Cost Multiplier | Growth Multiplier | Illness Probability | Revenue Multiplier |
|-----------|----------------|-------------------|--------------------|--------------------|
| Budget | 0.80× | 0.82× | 6%/month | 0.90× |
| Standard | 1.00× | 1.00× | 3%/month | 1.00× |
| Premium | 1.20× | 1.25× | 1.5%/month | 1.15× |

Budget feed saves money monthly but increases illness frequency, raises stress, and produces lower quality meat and milk. Premium feed costs more but produces healthier, more productive cows with better output quality.

---

## 💊 Medicine Type System

Three medicine tiers affect treatment cost, recovery speed, treatment success rate, and output quality (meat grade / milk quality):

| Medicine Type | Treatment Cost | Recovery Months | Success Rate | Revenue Multiplier |
|--------------|---------------|-----------------|--------------|-------------------|
| Basic | $50 | 2 months | 80% | 0.92× |
| Standard | $150 | 1 month | 90% | 1.00× |
| Premium | $300 | 0 months | 99% | 1.08× |

Basic medicine is cheap but slow and occasionally fails, leaving the cow sick for another month. Premium medicine resolves illness immediately with near-certainty and preserves meat/milk quality (analogous to USDA Choice/Prime grading standards and reduced tissue residue risk).

---

## 🏥 Health & Stress System

Every cow carries a continuous **stress level** (0.0–1.0) that evolves dynamically each month based on three interconnected factors:

### Stress Dynamics
- **Natural recovery:** stress decreases by 0.05 each month
- **Feed drift:** premium feed gradually reduces stress; budget feed gradually increases it
- **Illness events:** getting sick adds 0.2 to stress; being sick and untreated adds 0.1/month

### Stress Multiplier
Stress level is converted into a productivity multiplier applied to growth and milk revenue:

```
stress_multiplier = 1.1 - (stress_level × 0.4)
clamped between 0.5 and 1.1
```

A calm cow (stress = 0) performs at 110% baseline. A maximally stressed cow (stress = 1.0) performs at 70% baseline.

### Health Events
- Each month, if not already sick, a cow has a feed-type-dependent chance of falling ill
- If sick: stress rises, treatment fires automatically, cost is charged, success is rolled
- If treatment fails: cow remains sick, stress continues rising, treatment retries next month
- After recovery: a countdown runs (based on medicine type) during which a GM penalty of 0.85× applies

### Effective GM
When sick or recovering, the cow's genetic multiplier is penalized:
```
effective_gm = GM × 0.85
```
This affects both weight gain and milk revenue until full recovery.

---

## 💰 Financial Model

### Cost Components
Every cow accumulates two types of cost throughout its life:

- **Feed cost** — scales with body weight and feed type multiplier, charged every month
- **Vet cost** — flat baseline per stage (higher for calves) plus treatment cost when sick

### Revenue Events
- **Beef:** single terminal payout at slaughter — `weight × $4.00 × feed_revenue_mult × medicine_revenue_mult`
- **Dairy:** monthly milk revenue during lactation — `25 liters/day × 30 days × $0.40/liter × GM × stress_mult × revenue_multipliers`
- **Dairy cull:** terminal payout at end of productive life — `weight × $2.50 × revenue_multipliers`

### Profit & ROI
Each cow exposes two computed properties:

```python
cow.profit  # cumulative_revenue - cumulative_feed_cost - cumulative_vet_cost
cow.roi     # (profit / total_cost) × 100
```

---

## 🎲 Monte Carlo Simulation

The Monte Carlo engine runs the full herd simulation N times with identical parameters, collecting total herd profit per run. It automatically compares two extreme strategies:

- **Budget strategy:** budget feed + basic medicine
- **Premium strategy:** premium feed + premium medicine

Output includes:
- Average profit and ROI for each strategy
- Standard deviation (risk measure)
- Q1 and Q3 profit percentiles (confidence interval)

This allows the user to see not just which strategy is more profitable on average, but how consistent the outcomes are — premium strategy consistently shows lower variance (more predictable outcomes) while budget shows higher variance (more risk).

---

## 📊 Dashboard Features

The Streamlit app provides an interactive dashboard with:

**Left panel — Controls:**
- Herd size slider (1–100 cows)
- Dairy ratio slider (0–100% dairy)
- Max simulation months (1–240)
- Feed type selector (budget / standard / premium)
- Medicine type selector (basic / standard / premium)
- Monte Carlo runs slider
- Run Simulation and Run Monte Carlo buttons

**Right panel — Results:**
- Herd summary metrics (total profit, avg profit, best/worst cow)
- Individual Cow Performance (expandable) — per-cow bar chart colored by type, data table
- Revenue vs Cost Analysis (expandable) — grouped bar chart comparing dairy vs beef financials
- Profit Distribution (expandable) — histogram showing spread of outcomes
- Monte Carlo Strategy Comparison (expandable) — box plot comparing budget vs premium profit ranges with confidence intervals

---

## 🛠️ Technical Stack

- **Python 3.x**
- **Streamlit** — web application framework
- **Plotly** — interactive charts
- **Pandas** — data manipulation
- **statistics** (standard library) — Monte Carlo aggregation

---

## 🚀 Running Locally

**1. Clone the repository:**
```bash
git clone https://github.com/HarounGrine/Cow-production-simulator.git
cd Cow-production-simulator
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run the app:**
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 📐 Project Architecture

```
cow.py              # Cow class — state machine + health system
simulation.py       # Herd generator + simulation loop
metrics.py          # Herd aggregation (evaluate_herd)
Monte_Carlo.py      # Monte Carlo runner (budget vs premium)
app.py              # Streamlit dashboard
requirements.txt    # Dependencies
```

### Design Principles
- **Separation of concerns** — simulation logic is fully decoupled from the UI. `cow.py` and `simulation.py` have no Streamlit dependency and can be used independently.
- **Data-first** — each cow is a self-contained object carrying its full state and financial history. The UI just reads from completed cow objects.
- **Composable multipliers** — feed, medicine, stress, and genetics each contribute independent multipliers that stack. This makes the system extensible — adding a new factor (e.g. breed, season) means adding one new multiplier without restructuring existing logic.

---

## 🔮 Potential Extensions

- **Breed selection** — different breeds (Holstein, Angus, Hereford) with different baseline GM distributions
- **Seasonal feed pricing** — feed costs fluctuate by month of year
- **Herd management decisions** — interactive treatment choices mid-simulation
- **Multi-farm comparison** — run identical herds on different management strategies
- **Export to CSV** — download full per-cow simulation results

---

## 👤 Author

**Haroun Grine**
[GitHub](https://github.com/HarounGrine)
>>>>>>> b51322418df800ac0489e6af571bac9f3f7645c3
