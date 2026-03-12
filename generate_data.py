"""
generate_data.py
----------------
Generates realistic synthetic IT services delivery data
mimicking what ITC Infotech / any IT services company would have.

Produces:
  - clients.csv         — 50 client accounts with industry, tier, ARR
  - projects.csv        — 500 projects with budget, actual, status
  - tickets.csv         — 8,500+ service tickets with SLA data
  - timesheets.csv      — 52 weeks of consultant allocation data
  - consultants.csv     — 120 consultants with skills and grades
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ── CONFIG ────────────────────────────────────────────────────────────────
N_CLIENTS     = 50
N_PROJECTS    = 500
N_CONSULTANTS = 120
N_WEEKS       = 52
START_DATE    = datetime(2024, 1, 1)

INDUSTRIES    = ["Banking & Financial Services", "Manufacturing", "Consumer Goods", "Retail", "Hospitality"]
CLIENT_TIERS  = ["Platinum", "Gold", "Silver"]
PROJECT_TYPES = ["BI & Analytics", "ERP Implementation", "Digital Transformation", "Managed Services", "Cloud Migration"]
SKILLS        = ["SQL", "Python", "Tableau", "Power BI", "SAP", "Azure", "AWS", "Java", "Data Engineering"]
GRADES        = ["Analyst", "Senior Analyst", "Consultant", "Senior Consultant", "Manager"]

print("Generating IT Services Delivery Intelligence Dataset...")
print("="*55)

# ── CLIENTS ────────────────────────────────────────────────────────────────
clients = pd.DataFrame({
    "client_id":   [f"CLT{str(i).zfill(3)}" for i in range(1, N_CLIENTS+1)],
    "client_name": [f"Client_{i}" for i in range(1, N_CLIENTS+1)],
    "industry":    np.random.choice(INDUSTRIES, N_CLIENTS),
    "tier":        np.random.choice(CLIENT_TIERS, N_CLIENTS, p=[0.2, 0.4, 0.4]),
    "annual_revenue_lakh": np.random.choice([50, 100, 150, 200, 300, 500], N_CLIENTS),
    "account_start_date": [
        (START_DATE - timedelta(days=np.random.randint(180, 1800))).strftime("%Y-%m-%d")
        for _ in range(N_CLIENTS)
    ],
    "region": np.random.choice(["North India", "South India", "West India", "UK", "US", "APAC"], N_CLIENTS),
    "sla_target_resolution_hrs": np.random.choice([4, 8, 24, 48], N_CLIENTS, p=[0.1, 0.3, 0.4, 0.2]),
    "csat_target": np.random.choice([4.0, 4.2, 4.5], N_CLIENTS),
})
clients.to_csv("data/clients.csv", index=False)
print(f"✅ Clients         : {len(clients)} accounts across {len(INDUSTRIES)} industries")

# ── CONSULTANTS ────────────────────────────────────────────────────────────
consultants = pd.DataFrame({
    "consultant_id":   [f"CON{str(i).zfill(3)}" for i in range(1, N_CONSULTANTS+1)],
    "grade":           np.random.choice(GRADES, N_CONSULTANTS, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
    "primary_skill":   np.random.choice(SKILLS, N_CONSULTANTS),
    "experience_yrs":  np.random.randint(1, 15, N_CONSULTANTS),
    "cost_per_day_lakh": np.round(np.random.uniform(0.5, 3.5, N_CONSULTANTS), 2),
    "billable_rate_per_day_lakh": np.round(np.random.uniform(1.0, 6.0, N_CONSULTANTS), 2),
})
consultants.to_csv("data/consultants.csv", index=False)
print(f"✅ Consultants     : {len(consultants)} across {len(GRADES)} grades")

# ── PROJECTS ───────────────────────────────────────────────────────────────
project_rows = []
for i in range(1, N_PROJECTS+1):
    client_id = np.random.choice(clients["client_id"])
    start_offset = np.random.randint(0, 300)
    duration_days = np.random.randint(30, 365)
    start_dt = START_DATE + timedelta(days=start_offset)
    end_dt = start_dt + timedelta(days=duration_days)
    budget = np.random.randint(5, 200) * 10  # in lakhs
    overrun_factor = np.random.choice([0.9, 1.0, 1.05, 1.15, 1.3, 1.5],
                                       p=[0.1, 0.35, 0.2, 0.15, 0.12, 0.08])
    actual_cost = round(budget * overrun_factor, 1)
    delay_days = int(np.random.choice([0, 0, 0, 7, 14, 30, 60], p=[0.4, 0.2, 0.1, 0.1, 0.1, 0.07, 0.03]))
    status = np.random.choice(
        ["On Track", "At Risk", "Delayed", "Completed", "On Hold"],
        p=[0.4, 0.2, 0.15, 0.2, 0.05]
    )
    project_rows.append({
        "project_id": f"PRJ{str(i).zfill(4)}",
        "client_id": client_id,
        "project_name": f"{np.random.choice(PROJECT_TYPES)} Phase {np.random.randint(1,4)}",
        "project_type": np.random.choice(PROJECT_TYPES),
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "planned_end_date": end_dt.strftime("%Y-%m-%d"),
        "actual_end_date": (end_dt + timedelta(days=delay_days)).strftime("%Y-%m-%d") if status == "Completed" else None,
        "budget_lakh": budget,
        "actual_cost_lakh": actual_cost,
        "cost_overrun_pct": round((overrun_factor - 1) * 100, 1),
        "delay_days": delay_days,
        "status": status,
        "milestone_hit_rate_pct": round(np.random.uniform(50, 100), 1),
        "lead_consultant_id": np.random.choice(consultants["consultant_id"]),
    })

projects = pd.DataFrame(project_rows)
projects.to_csv("data/projects.csv", index=False)
print(f"✅ Projects        : {len(projects)} | At Risk: {(projects.status=='At Risk').sum()} | Delayed: {(projects.status=='Delayed').sum()}")

# ── TICKETS ────────────────────────────────────────────────────────────────
ticket_rows = []
priorities = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
priority_weights = [0.05, 0.15, 0.45, 0.35]
priority_sla_hrs = {"P1-Critical": 4, "P2-High": 8, "P3-Medium": 24, "P4-Low": 48}

for week in range(N_WEEKS):
    week_start = START_DATE + timedelta(weeks=week)
    n_tickets = np.random.randint(130, 200)
    for _ in range(n_tickets):
        client_id = np.random.choice(clients["client_id"])
        priority = np.random.choice(priorities, p=priority_weights)
        sla_target = priority_sla_hrs[priority]
        # Inject some accounts that consistently breach SLA
        breach_prob = 0.08 if client_id not in ["CLT005", "CLT012", "CLT027", "CLT038", "CLT045"] else 0.45
        breached = np.random.random() < breach_prob
        actual_resolution = sla_target * np.random.uniform(0.3, 0.9) if not breached else sla_target * np.random.uniform(1.1, 3.0)
        created = week_start + timedelta(hours=np.random.randint(0, 168))
        ticket_rows.append({
            "ticket_id": f"TKT{str(len(ticket_rows)+1).zfill(6)}",
            "client_id": client_id,
            "week": week + 1,
            "created_date": created.strftime("%Y-%m-%d"),
            "priority": priority,
            "category": np.random.choice(["Incident", "Service Request", "Change", "Problem"], p=[0.4, 0.3, 0.2, 0.1]),
            "sla_target_hrs": sla_target,
            "actual_resolution_hrs": round(actual_resolution, 1),
            "sla_breached": int(breached),
            "first_contact_resolved": int(np.random.random() < 0.72),
            "csat_score": round(np.random.uniform(2.5, 5.0) if not breached else np.random.uniform(1.5, 3.5), 1),
            "escalated": int(np.random.random() < (0.05 if not breached else 0.35)),
            "assigned_consultant_id": np.random.choice(consultants["consultant_id"]),
        })

tickets = pd.DataFrame(ticket_rows)
tickets.to_csv("data/tickets.csv", index=False)
print(f"✅ Tickets         : {len(tickets):,} | SLA Breached: {tickets.sla_breached.sum():,} ({tickets.sla_breached.mean()*100:.1f}%)")

# ── TIMESHEETS ─────────────────────────────────────────────────────────────
timesheet_rows = []
for week in range(N_WEEKS):
    for _, con in consultants.iterrows():
        # Most consultants allocated to 1-2 projects
        allocated_hrs = np.random.choice(
            [0, 20, 30, 40, 45, 50, 55, 60],
            p=[0.05, 0.05, 0.10, 0.40, 0.15, 0.10, 0.08, 0.07]
        )
        billable_hrs = min(allocated_hrs, allocated_hrs * np.random.uniform(0.7, 1.0))
        unbilled_hrs = max(0, allocated_hrs - billable_hrs - np.random.uniform(0, 3))
        timesheet_rows.append({
            "timesheet_id": f"TS{str(len(timesheet_rows)+1).zfill(6)}",
            "consultant_id": con["consultant_id"],
            "week": week + 1,
            "week_start_date": (START_DATE + timedelta(weeks=week)).strftime("%Y-%m-%d"),
            "allocated_hrs": allocated_hrs,
            "billable_hrs": round(billable_hrs, 1),
            "unbilled_hrs": round(unbilled_hrs, 1),
            "utilisation_pct": round((billable_hrs / 40) * 100, 1),
            "overtime_hrs": max(0, allocated_hrs - 40),
            "client_id": np.random.choice(clients["client_id"]),
            "project_id": np.random.choice(projects["project_id"]),
        })

timesheets = pd.DataFrame(timesheet_rows)
timesheets.to_csv("data/timesheets.csv", index=False)
print(f"✅ Timesheets      : {len(timesheets):,} records across {N_WEEKS} weeks")

# ── SUMMARY ────────────────────────────────────────────────────────────────
print()
print("="*55)
print("DATASET SUMMARY")
print("="*55)
print(f"Total records     : {len(clients)+len(consultants)+len(projects)+len(tickets)+len(timesheets):,}")
print(f"Date range        : {START_DATE.strftime('%Y-%m-%d')} → {(START_DATE+timedelta(weeks=N_WEEKS)).strftime('%Y-%m-%d')}")
print(f"At-risk projects  : {(projects.status.isin(['At Risk','Delayed'])).sum()}/{len(projects)}")
print(f"SLA breach rate   : {tickets.sla_breached.mean()*100:.1f}%")
print(f"Avg utilisation   : {timesheets.utilisation_pct.mean():.1f}%")
print(f"Total unbilled hrs: {timesheets.unbilled_hrs.sum():,.0f}")
print()
print("Files saved to data/:")
for f in ["clients.csv","consultants.csv","projects.csv","tickets.csv","timesheets.csv"]:
    size = os.path.getsize(f"data/{f}")
    print(f"  {f:<25} {size/1024:.1f} KB")
