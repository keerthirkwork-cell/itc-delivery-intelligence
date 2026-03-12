# 🚦 Client Delivery Intelligence
### IT Services Portfolio Analytics — SLA Early Warning, Watermelon Account Detection & Revenue Leakage

> **Built to solve the #1 problem in IT services delivery: knowing which client accounts are silently failing before the client tells you.**

---

## 📊 Dashboard Preview

![Client Health Dashboard](screenshots/01_client_health_dashboard.png)

---

## 🎯 The Problem This Solves

Every IT services company — ITC Infotech, Infosys, Wipro, TCS — manages dozens of client accounts simultaneously.

The dirty secret? **Most delivery failures are visible in the data weeks before they happen.**

| Signal | Where It Hides |
|--------|---------------|
| Project slipping its milestone | Timesheet data |
| Client about to escalate | Ticket resolution times |
| Team heading for burnout | Utilisation rate at 120% for 3 weeks |
| Revenue being lost silently | Unbilled hours trending up |

But nobody connects these signals. Account managers fly blind, using gut feel and weekly status calls instead of data.

**This system fixes that.**

---

## 🏗️ System Architecture

![Architecture Diagram](docs/architecture_diagram.png)

---

## 📈 Key Findings

| Insight | Finding | Business Impact |
|---------|---------|----------------|
| SLA breach rate | 11.6% portfolio-wide | 2× the industry target of 5% |
| Watermelon accounts | 6 out of 50 | Silent failures invisible to status reporting |
| Revenue leakage | 11.3% of hours unbilled | Est. ₹2.1Cr/year recoverable |
| Burnout-risk consultants | 18% over 110% utilisation | ₹12L attrition cost per senior consultant |
| Top breach predictor | Ticket backlog growth rate | 14-day early warning signal |

---

## 🚨 SLA Early Warning System

![SLA Breach Warning](screenshots/02_sla_breach_warning.png)

---

## 💰 Resource Utilisation & Revenue Leakage

![Resource and Revenue Analysis](screenshots/03_resource_revenue.png)

---

## 🍉 Watermelon Account Detector

> *A Watermelon Account looks green on the outside — clean status report, on-time milestones — but is red on the inside: rising SLA breaches, falling CSAT, growing escalations.*

![Watermelon Detector](screenshots/04_watermelon_detector.png)

---

## 📁 Project Structure

```
itc-delivery-intelligence/
│
├── data/
│   └── generate_data.py              # Generates realistic synthetic dataset
│
├── notebooks/
│   ├── 01_delivery_eda.ipynb         # Project health & portfolio overview
│   ├── 02_sla_breach_prediction.ipynb# Which accounts will breach SLA?
│   ├── 03_resource_utilisation.ipynb # Over/under allocation analysis
│   ├── 04_revenue_leakage.ipynb      # Unbilled hours & scope creep
│   └── 05_client_health_score.ipynb  # Composite client health dashboard
│
├── sql/
│   └── delivery_analytics.sql        # 5 production-ready SQL queries
│
├── dashboard/
│   └── app.py                        # Streamlit interactive dashboard
│
├── docs/
│   ├── architecture_diagram.png      # System architecture visual
│   └── executive_briefing.md         # 1-page leadership pitch
│
├── screenshots/                      # Chart outputs for README
│
└── README.md
```

---

## 🔬 Dataset

**Synthetic but realistic** — generated to mirror real IT services data:

- **50 client accounts** across Banking, Manufacturing, Consumer Goods, Retail & Hospitality
- **500 projects** with milestones, budgets, actual spend, delivery status
- **8,500+ service tickets** with SLA targets and resolution times
- **52 weeks** of timesheet and allocation data
- **120 consultants** across 5 grades with skills and utilisation

> **Why synthetic?** Real delivery data is confidential. Generating it from scratch demonstrates deeper understanding of the data model than downloading a public dataset.

---

## 🚀 How To Run

```bash
# 1. Clone the repo
git clone https://github.com/keerthirkwork-cell/itc-delivery-intelligence.git
cd itc-delivery-intelligence

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset
python data/generate_data.py

# 4. Run Streamlit dashboard
streamlit run dashboard/app.py

# 5. Or run notebooks in order
jupyter notebook notebooks/
```

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Data Generation | Python, NumPy, Faker |
| Analysis | Pandas, SciPy, Statsmodels |
| Machine Learning | Scikit-learn (Logistic Regression, Random Forest) |
| Visualisation | Matplotlib, Seaborn |
| Dashboard | Streamlit |
| SQL Analytics | SQLite + production-ready queries |

---

## 📄 Executive Pitch

> *"Your account managers know when a project is failing. But they find out on the weekly status call — not 3 weeks earlier when the data already knew. This system gives you a 2-week early warning on every at-risk account, automatically."*

See [`docs/executive_briefing.md`](docs/executive_briefing.md) for the full 1-page brief.

---

## 👩‍💻 Author

**Keerthi RK** — Data Analyst | Business Intelligence

[LinkedIn](https://linkedin.com/in/keerthi-r-81bb82200) • [GitHub](https://github.com/keerthirkwork-cell)
