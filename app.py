"""
dashboard/app.py
----------------
Streamlit Client Delivery Intelligence Dashboard
Run: streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(
    page_title="Client Delivery Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

BLUE='#1A3C6E'; RED='#C0392B'; GREEN='#27AE60'; ORANGE='#E67E22'; GRAY='#95A5A6'; LIGHT='#EEF4FB'

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(__file__))
    clients     = pd.read_csv(f'{base}/data/clients.csv')
    projects    = pd.read_csv(f'{base}/data/projects.csv')
    tickets     = pd.read_csv(f'{base}/data/tickets.csv')
    timesheets  = pd.read_csv(f'{base}/data/timesheets.csv')
    consultants = pd.read_csv(f'{base}/data/consultants.csv')
    return clients, projects, tickets, timesheets, consultants

@st.cache_data
def compute_health(clients, projects, tickets, timesheets):
    sla = tickets.groupby('client_id').agg(
        breach_rate=('sla_breached','mean'), avg_csat=('csat_score','mean'),
        fcr=('first_contact_resolved','mean'), esc=('escalated','mean')
    ).reset_index()
    sla['sla_score'] = ((1-sla['breach_rate'])*40+(sla['avg_csat']/5)*30+sla['fcr']*20+(1-sla['esc'])*10).clip(0,100)

    delivery = projects.groupby('client_id').agg(
        on_track=('status', lambda x: (x=='On Track').mean()),
        overrun=('cost_overrun_pct','mean'), delay=('delay_days','mean'),
        milestone=('milestone_hit_rate_pct','mean')
    ).reset_index()
    delivery['delivery_score'] = (delivery['on_track']*35+(1-(delivery['overrun']/100).clip(0,1))*30+(1-(delivery['delay']/60).clip(0,1))*15+(delivery['milestone']/100)*20).clip(0,100)

    rev = timesheets.groupby('client_id').agg(
        billed=('billable_hrs','sum'), unbilled=('unbilled_hrs','sum'), util=('utilisation_pct','mean')
    ).reset_index()
    rev['leakage'] = rev['unbilled']/(rev['billed']+rev['unbilled']+1)
    rev['revenue_score'] = ((1-rev['leakage'])*60+(rev['util']/100).clip(0,1)*40).clip(0,100)

    recent = tickets[tickets['week']>=40].groupby('client_id')['ticket_id'].count().reset_index()
    recent.columns = ['client_id','recent']
    early  = tickets[tickets['week']<=12].groupby('client_id')['ticket_id'].count().reset_index()
    early.columns  = ['client_id','early']
    trend = recent.merge(early, on='client_id', how='left').fillna(0)
    trend['growth'] = (trend['recent']-trend['early'])/(trend['early']+1)
    trend['trend_score'] = (1-trend['growth'].clip(0,1))*100

    health = clients[['client_id','client_name','industry','tier']].merge(
        sla[['client_id','sla_score','breach_rate','avg_csat']], on='client_id', how='left'
    ).merge(delivery[['client_id','delivery_score','on_track','overrun']], on='client_id', how='left'
    ).merge(rev[['client_id','revenue_score','leakage','util']], on='client_id', how='left'
    ).merge(trend[['client_id','trend_score']], on='client_id', how='left').fillna(50)

    health['health_score'] = (
        health['sla_score']*0.30 + health['delivery_score']*0.35 +
        health['revenue_score']*0.20 + health['trend_score']*0.15
    ).round(1)
    health['health_band'] = pd.cut(health['health_score'], bins=[0,40,60,75,100],
        labels=['Critical','At Risk','Healthy','Excellent'])
    health['watermelon'] = ((health['on_track']>0.6) & (health['health_score']<55)).astype(int)
    return health

# ── Load Data ──────────────────────────────────────────────────────────────
clients, projects, tickets, timesheets, consultants = load_data()
health = compute_health(clients, projects, tickets, timesheets)

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.shields.io/badge/Client%20Delivery-Intelligence-1A3C6E?style=for-the-badge")
st.sidebar.title("Filters")
selected_industry = st.sidebar.multiselect("Industry", options=clients['industry'].unique(), default=list(clients['industry'].unique()))
selected_tier = st.sidebar.multiselect("Client Tier", options=['Platinum','Gold','Silver'], default=['Platinum','Gold','Silver'])
min_score = st.sidebar.slider("Min Health Score", 0, 100, 0)

h = health[
    health['industry'].isin(selected_industry) &
    health['tier'].isin(selected_tier) &
    (health['health_score'] >= min_score)
]

# ── Header ────────────────────────────────────────────────────────────────
st.title("🚦 Client Delivery Intelligence Dashboard")
st.markdown("*Real-time health monitoring across your entire IT services portfolio*")
st.divider()

# ── KPI Row ───────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
healthy_count   = (h['health_band'].isin(['Healthy','Excellent'])).sum()
at_risk_count   = (h['health_band']=='At Risk').sum()
critical_count  = (h['health_band']=='Critical').sum()
watermelon_count= h['watermelon'].sum()
breach_rate     = tickets[tickets['client_id'].isin(h['client_id'])]['sla_breached'].mean()*100

col1.metric("Total Accounts",   len(h))
col2.metric("Healthy",          healthy_count, delta=None)
col3.metric("At Risk",          at_risk_count, delta=f"-{at_risk_count} need attention", delta_color="inverse")
col4.metric("Critical",         critical_count, delta=f"-{critical_count} urgent", delta_color="inverse")
col5.metric("SLA Breach Rate",  f"{breach_rate:.1f}%", delta=f"Target: 5%", delta_color="inverse")

st.divider()

# ── Main Charts ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2,1])

with col_left:
    st.subheader("Client Health Scores — All Accounts")
    fig, ax = plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor('white'); ax.set_facecolor('#FAFCFF')
    hs = h.sort_values('health_score')
    colors = [RED if s<60 else ORANGE if s<75 else GREEN for s in hs['health_score']]
    ax.bar(range(len(hs)), hs['health_score'], color=colors, alpha=0.85, width=0.8)
    ax.axhline(75, color=GREEN, linestyle='--', lw=1.5, label='Healthy (75)')
    ax.axhline(60, color=RED,   linestyle='--', lw=1.5, label='At Risk (60)')
    wm = [i for i,(w,s) in enumerate(zip(hs['watermelon'],hs['health_score'])) if w==1]
    if wm: ax.scatter(wm, [hs['health_score'].iloc[i]+2 for i in wm], marker='*', color=ORANGE, s=120, zorder=5, label='Watermelon')
    ax.set_ylabel('Health Score'); ax.legend(fontsize=8)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    st.pyplot(fig); plt.close()

with col_right:
    st.subheader("Health Distribution")
    fig, ax = plt.subplots(figsize=(4,4))
    fig.patch.set_facecolor('white')
    band_c = h['health_band'].value_counts()
    bcolors = {'Excellent':GREEN,'Healthy':'#2980B9','At Risk':ORANGE,'Critical':RED}
    bc = [bcolors.get(b,GRAY) for b in band_c.index]
    ax.pie(band_c.values, labels=band_c.index, colors=bc, autopct='%1.0f%%',
        startangle=90, wedgeprops={'width':0.6}, textprops={'fontsize':9})
    st.pyplot(fig); plt.close()

st.divider()

# ── Watermelon Alert ──────────────────────────────────────────────────────
wm_accounts = h[h['watermelon']==1]
if len(wm_accounts) > 0:
    st.error(f"⚠️ **WATERMELON ALERT: {len(wm_accounts)} accounts look healthy but are at risk!**")
    wm_display = wm_accounts[['client_name','industry','tier','health_score','breach_rate','leakage']].copy()
    wm_display.columns = ['Account','Industry','Tier','Health Score','SLA Breach %','Revenue Leakage %']
    wm_display['SLA Breach %'] = (wm_display['SLA Breach %']*100).round(1)
    wm_display['Revenue Leakage %'] = (wm_display['Revenue Leakage %']*100).round(1)
    st.dataframe(wm_display, use_container_width=True)
    st.divider()

# ── Bottom Row ────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("SLA Breach Trend (52 Weeks)")
    w_tickets = tickets[tickets['client_id'].isin(h['client_id'])]
    weekly = w_tickets.groupby('week').agg(total=('ticket_id','count'), breached=('sla_breached','sum')).reset_index()
    weekly['rate'] = weekly['breached']/weekly['total']*100
    fig, ax = plt.subplots(figsize=(7,3.5))
    fig.patch.set_facecolor('white'); ax.set_facecolor('#FAFCFF')
    ax.fill_between(weekly['week'], weekly['rate'], alpha=0.15, color=RED)
    ax.plot(weekly['week'], weekly['rate'], color=RED, lw=2)
    ax.axhline(5, color=GREEN, linestyle='--', lw=1.5, label='Target: 5%')
    ax.set_xlabel('Week'); ax.set_ylabel('Breach Rate %')
    ax.legend(fontsize=8); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    st.pyplot(fig); plt.close()

with col_b:
    st.subheader("Resource Utilisation by Grade")
    util_data = timesheets.merge(consultants[['consultant_id','grade']])
    ug = util_data.groupby('grade')['utilisation_pct'].mean().sort_values()
    ugc = [RED if v>105 else ORANGE if v>95 else GREEN if v>75 else GRAY for v in ug]
    fig, ax = plt.subplots(figsize=(7,3.5))
    fig.patch.set_facecolor('white'); ax.set_facecolor('#FAFCFF')
    ax.barh(ug.index, ug.values, color=ugc, alpha=0.85)
    ax.axvline(85, color=GREEN, linestyle='--', lw=1.5, label='Target: 85%')
    ax.axvline(100, color=RED, linestyle=':', lw=1.5, label='Overload')
    for i,v in enumerate(ug.values): ax.text(v+0.3, i, f'{v:.1f}%', va='center', fontsize=9)
    ax.legend(fontsize=8); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    st.pyplot(fig); plt.close()

st.divider()
st.subheader("Full Account Health Table")
display_cols = ['client_name','industry','tier','health_score','health_band','breach_rate','overrun','leakage','watermelon']
display = h[display_cols].copy()
display.columns = ['Account','Industry','Tier','Health Score','Status','SLA Breach %','Cost Overrun %','Leakage %','Watermelon?']
display['SLA Breach %'] = (display['SLA Breach %']*100).round(1)
display['Leakage %'] = (display['Leakage %']*100).round(1)
display['Cost Overrun %'] = display['Cost Overrun %'].round(1)
display['Watermelon?'] = display['Watermelon?'].map({1:'YES ⚠️', 0:'No'})
display = display.sort_values('Health Score')
st.dataframe(display, use_container_width=True, height=400)

st.markdown("---")
st.markdown("*Built by **Keerthi RK** | [GitHub](https://github.com/keerthirkwork-cell/itc-delivery-intelligence) | [LinkedIn](https://linkedin.com/in/keerthi-r-81bb82200)*")
