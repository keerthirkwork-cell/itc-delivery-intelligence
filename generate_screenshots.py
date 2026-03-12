"""
generate_screenshots.py
Generates 4 high-quality PNG screenshots for the GitHub README
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

BLUE='#1A3C6E'; RED='#C0392B'; GREEN='#27AE60'; ORANGE='#E67E22'
GRAY='#95A5A6'; LIGHT='#EEF4FB'; ACCENT='#2563A8'; YELLOW='#F1C40F'

plt.rcParams.update({
    'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': 'white', 'font.family': 'DejaVu Sans',
    'axes.facecolor': '#FAFCFF', 'grid.alpha': 0.3,
    'axes.grid': True, 'grid.linestyle': '--'
})

clients     = pd.read_csv('data/clients.csv')
projects    = pd.read_csv('data/projects.csv')
tickets     = pd.read_csv('data/tickets.csv')
timesheets  = pd.read_csv('data/timesheets.csv')
consultants = pd.read_csv('data/consultants.csv')

# ── Compute health scores ─────────────────────────────────────────────────
sla = tickets.groupby('client_id').agg(
    breach_rate=('sla_breached','mean'),
    avg_csat=('csat_score','mean'),
    fcr=('first_contact_resolved','mean'),
    esc=('escalated','mean')
).reset_index()
sla['sla_score'] = ((1-sla['breach_rate'])*40 + (sla['avg_csat']/5)*30 + sla['fcr']*20 + (1-sla['esc'])*10).clip(0,100)

delivery = projects.groupby('client_id').agg(
    on_track=('status', lambda x: (x=='On Track').mean()),
    overrun=('cost_overrun_pct','mean'),
    delay=('delay_days','mean'),
    milestone=('milestone_hit_rate_pct','mean')
).reset_index()
delivery['delivery_score'] = (delivery['on_track']*35 + (1-(delivery['overrun']/100).clip(0,1))*30 + (1-(delivery['delay']/60).clip(0,1))*15 + (delivery['milestone']/100)*20).clip(0,100)

rev = timesheets.groupby('client_id').agg(
    billed=('billable_hrs','sum'), unbilled=('unbilled_hrs','sum'), util=('utilisation_pct','mean')
).reset_index()
rev['leakage'] = rev['unbilled']/(rev['billed']+rev['unbilled']+1)
rev['revenue_score'] = ((1-rev['leakage'])*60 + (rev['util']/100).clip(0,1)*40).clip(0,100)

recent = tickets[tickets['week']>=40].groupby('client_id')['ticket_id'].count().reset_index()
recent.columns = ['client_id','recent']
early  = tickets[tickets['week']<=12].groupby('client_id')['ticket_id'].count().reset_index()
early.columns  = ['client_id','early']
trend = recent.merge(early, on='client_id', how='left')
trend['growth'] = (trend['recent']-trend['early'])/(trend['early']+1)
trend['trend_score'] = (1-trend['growth'].clip(0,1))*100

health = clients[['client_id','client_name','industry','tier']].merge(
    sla[['client_id','sla_score','breach_rate','avg_csat']], on='client_id', how='left'
).merge(delivery[['client_id','delivery_score','on_track','overrun']], on='client_id', how='left'
).merge(rev[['client_id','revenue_score','leakage','util']], on='client_id', how='left'
).merge(trend[['client_id','trend_score','growth']], on='client_id', how='left').fillna(50)

health['health_score'] = (
    health['sla_score']*0.30 + health['delivery_score']*0.35 +
    health['revenue_score']*0.20 + health['trend_score']*0.15
).round(1)
health['health_band'] = pd.cut(health['health_score'], bins=[0,40,60,75,100],
    labels=['Critical','At Risk','Healthy','Excellent'])
health['watermelon'] = ((health['on_track']>0.6) & (health['health_score']<55)).astype(int)

print("Health scores computed. Generating screenshots...")

# ═══════════════════════════════════════════════════════════════════════════
# SCREENSHOT 1 — Client Health Score Dashboard
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('📊 Client Health Score Dashboard', fontsize=18, fontweight='bold', color=BLUE, y=0.98)
fig.patch.set_facecolor('white')

# 1a — Health score bar chart
ax = axes[0,0]
hs = health.sort_values('health_score')
colors = [RED if s<60 else ORANGE if s<75 else GREEN for s in hs['health_score']]
ax.bar(range(len(hs)), hs['health_score'], color=colors, alpha=0.85, width=0.8)
ax.axhline(75, color=GREEN, linestyle='--', lw=1.5, label='Healthy (75)')
ax.axhline(60, color=RED,   linestyle='--', lw=1.5, label='At Risk (60)')
wm = [i for i,(w,s) in enumerate(zip(hs['watermelon'],hs['health_score'])) if w==1]
ax.scatter(wm, [hs['health_score'].iloc[i]+2 for i in wm], marker='*', color=ORANGE, s=120, zorder=5, label='🍉 Watermelon')
ax.set_title('Health Scores — All 50 Accounts', fontweight='bold', color=BLUE)
ax.set_xlabel('Client Accounts'); ax.set_ylabel('Score (0–100)')
ax.legend(fontsize=8); ax.set_xlim(-1, 50)

# 1b — Band distribution donut
ax = axes[0,1]
band_c = health['health_band'].value_counts()
bcolors = {'Excellent':GREEN,'Healthy':'#2980B9','At Risk':ORANGE,'Critical':RED}
bc = [bcolors.get(b,GRAY) for b in band_c.index]
wedges,texts,autos = ax.pie(band_c.values, labels=band_c.index, colors=bc,
    autopct='%1.0f%%', startangle=90, wedgeprops={'width':0.6}, textprops={'fontsize':9})
for a in autos: a.set_fontsize(9); a.set_fontweight('bold')
ax.set_title('Account Health Distribution', fontweight='bold', color=BLUE)

# 1c — Industry health
ax = axes[0,2]
ind = health.groupby('industry')['health_score'].mean().sort_values()
ic = [RED if v<60 else ORANGE if v<75 else GREEN for v in ind]
bars = ax.barh(ind.index, ind.values, color=ic, alpha=0.85)
for i,v in enumerate(ind.values): ax.text(v+0.5, i, f'{v:.0f}', va='center', fontsize=9, fontweight='bold')
ax.axvline(75, color=GREEN, linestyle='--', lw=1.2, alpha=0.7)
ax.set_title('Avg Health by Industry', fontweight='bold', color=BLUE)
ax.set_xlim(0, 105)

# 1d — Score components
ax = axes[1,0]
dims = ['sla_score','delivery_score','revenue_score','trend_score']
dlabels = ['SLA\n(30%)','Delivery\n(35%)','Revenue\n(20%)','Trend\n(15%)']
top10 = health.nsmallest(10,'health_score')
x = np.arange(4); w = 0.35
ax.bar(x-w/2, [health[d].mean() for d in dims], w, color=BLUE, alpha=0.85, label='All accounts avg')
ax.bar(x+w/2, [top10[d].mean() for d in dims], w, color=RED, alpha=0.85, label='Bottom 10 accounts')
ax.set_xticks(x); ax.set_xticklabels(dlabels, fontsize=9)
ax.set_ylabel('Score'); ax.set_title('Score Components: All vs At-Risk', fontweight='bold', color=BLUE)
ax.legend(fontsize=8)

# 1e — KPI cards
ax = axes[1,1]; ax.axis('off')
kpis = [
    (f"{(health['health_band'].isin(['Healthy','Excellent'])).sum()}", 'Healthy Accounts', GREEN),
    (f"{(health['health_band']=='At Risk').sum()}", 'At Risk', ORANGE),
    (f"{(health['health_band']=='Critical').sum()}", 'Critical', RED),
    (f"{health['watermelon'].sum()}", '🍉 Watermelon', ORANGE),
]
for i,(v,l,c) in enumerate(kpis):
    row, col = divmod(i,2)
    ax.add_patch(FancyBboxPatch((col*0.52+0.02, 0.52-row*0.52+0.02), 0.46, 0.44,
        boxstyle='round,pad=0.03', facecolor=LIGHT, edgecolor=c, linewidth=2, transform=ax.transAxes))
    ax.text(col*0.52+0.25, 0.52-row*0.52+0.3, v, ha='center', fontsize=20, fontweight='bold', color=c, transform=ax.transAxes)
    ax.text(col*0.52+0.25, 0.52-row*0.52+0.12, l, ha='center', fontsize=9, color=BLUE, fontweight='bold', transform=ax.transAxes)
ax.set_title('Portfolio KPIs', fontweight='bold', color=BLUE)

# 1f — Tier health
ax = axes[1,2]
tier = health.groupby('tier')['health_score'].mean().sort_values()
tc = [RED if v<60 else ORANGE if v<75 else GREEN for v in tier]
ax.bar(tier.index, tier.values, color=tc, alpha=0.85, width=0.5)
for i,v in enumerate(tier.values): ax.text(i, v+0.5, f'{v:.0f}', ha='center', fontsize=11, fontweight='bold')
ax.set_title('Health Score by Client Tier', fontweight='bold', color=BLUE)
ax.set_ylabel('Avg Health Score'); ax.set_ylim(0,100)

plt.tight_layout()
plt.savefig('screenshots/01_client_health_dashboard.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("✅ Screenshot 1 — Client Health Dashboard")

# ═══════════════════════════════════════════════════════════════════════════
# SCREENSHOT 2 — SLA Breach Early Warning
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('🚨 SLA Breach Early Warning System', fontsize=18, fontweight='bold', color=BLUE, y=0.98)
fig.patch.set_facecolor('white')

# 2a — Weekly breach trend
ax = axes[0,0]
weekly = tickets.groupby('week').agg(total=('ticket_id','count'), breached=('sla_breached','sum')).reset_index()
weekly['rate'] = weekly['breached']/weekly['total']*100
ax.fill_between(weekly['week'], weekly['rate'], alpha=0.15, color=RED)
ax.plot(weekly['week'], weekly['rate'], color=RED, lw=2, label='Breach Rate %')
ax.axhline(5, color=GREEN, linestyle='--', lw=1.5, label='Target: 5%')
ax.axhline(weekly['rate'].mean(), color=ORANGE, linestyle=':', lw=1.5, label=f'Avg: {weekly["rate"].mean():.1f}%')
ax.set_title('SLA Breach Rate — 52-Week Trend', fontweight='bold', color=BLUE)
ax.set_xlabel('Week'); ax.set_ylabel('Breach Rate %')
ax.legend(fontsize=9); ax.set_xlim(1,52)

# 2b — Breach by priority
ax = axes[0,1]
bp = tickets.groupby('priority')['sla_breached'].mean()*100
bp = bp.sort_values()
bc2 = [RED if v>20 else ORANGE if v>10 else GREEN for v in bp]
ax.barh(bp.index, bp.values, color=bc2, alpha=0.85)
ax.axvline(5, color=GREEN, linestyle='--', lw=1.5, label='Target 5%')
for i,v in enumerate(bp.values): ax.text(v+0.2, i, f'{v:.1f}%', va='center', fontsize=10, fontweight='bold')
ax.set_title('SLA Breach Rate by Priority', fontweight='bold', color=BLUE)
ax.set_xlabel('Breach Rate %'); ax.legend(fontsize=9)

# 2c — Top 10 breaching accounts
ax = axes[1,0]
top_breach_df = tickets.groupby('client_id')['sla_breached'].mean().reset_index()
top_breach_df['sla_breached'] = top_breach_df['sla_breached']*100
top_breach_df = top_breach_df.merge(clients[['client_id','client_name']], on='client_id').nlargest(10,'sla_breached').set_index('client_name')
top_breach = top_breach_df['sla_breached']
bc3 = [RED if v>25 else ORANGE for v in top_breach.values]
ax.barh(top_breach.index, top_breach.values, color=bc3, alpha=0.85)
ax.axvline(5, color=GREEN, linestyle='--', lw=1.5, alpha=0.7)
for i,v in enumerate(top_breach.values): ax.text(v+0.2, i, f'{v:.1f}%', va='center', fontsize=9, fontweight='bold')
ax.set_title('Top 10 Highest SLA Breach Accounts', fontweight='bold', color=RED)
ax.set_xlabel('Breach Rate %')

# 2d — Resolution time vs SLA target
ax = axes[1,1]
sample = tickets.sample(min(500, len(tickets)), random_state=42)
breached_t = sample[sample['sla_breached']==1]
ok_t = sample[sample['sla_breached']==0]
ax.scatter(ok_t['sla_target_hrs'], ok_t['actual_resolution_hrs'], alpha=0.4, color=GREEN, s=20, label='Within SLA')
ax.scatter(breached_t['sla_target_hrs'], breached_t['actual_resolution_hrs'], alpha=0.5, color=RED, s=20, label='SLA Breached')
maxv = sample['sla_target_hrs'].max()*2
ax.plot([0,maxv],[0,maxv], color=BLUE, linestyle='--', lw=1.5, label='SLA boundary')
ax.set_title('Actual Resolution vs SLA Target (sample)', fontweight='bold', color=BLUE)
ax.set_xlabel('SLA Target (hrs)'); ax.set_ylabel('Actual Resolution (hrs)')
ax.legend(fontsize=9); ax.set_xlim(0,55); ax.set_ylim(0,120)

plt.tight_layout()
plt.savefig('screenshots/02_sla_breach_warning.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("✅ Screenshot 2 — SLA Breach Warning")

# ═══════════════════════════════════════════════════════════════════════════
# SCREENSHOT 3 — Resource Utilisation & Revenue Leakage
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('💰 Resource Utilisation & Revenue Leakage Analysis', fontsize=18, fontweight='bold', color=BLUE, y=0.98)
fig.patch.set_facecolor('white')

util_data = timesheets.merge(consultants[['consultant_id','grade']])

# 3a — Utilisation distribution
ax = axes[0,0]
ax.hist(timesheets['utilisation_pct'], bins=30, color=BLUE, alpha=0.8, edgecolor='white')
ax.axvline(85, color=GREEN, linestyle='--', lw=2, label='Target: 85%')
ax.axvline(100, color=RED,   linestyle='--', lw=2, label='Overload: 100%')
ax.axvline(timesheets['utilisation_pct'].mean(), color=ORANGE, linestyle=':', lw=2, label=f'Avg: {timesheets["utilisation_pct"].mean():.1f}%')
ax.set_title('Consultant Utilisation Distribution', fontweight='bold', color=BLUE)
ax.set_xlabel('Utilisation %'); ax.set_ylabel('Count'); ax.legend(fontsize=9)

# 3b — Utilisation by grade
ax = axes[0,1]
ug = util_data.groupby('grade')['utilisation_pct'].mean().sort_values()
ugc = [RED if v>105 else ORANGE if v>95 else GREEN if v>75 else GRAY for v in ug]
ax.barh(ug.index, ug.values, color=ugc, alpha=0.85)
ax.axvline(85, color=GREEN, linestyle='--', lw=1.5, label='Target: 85%')
ax.axvline(100, color=RED, linestyle=':', lw=1.5, label='Overload: 100%')
for i,v in enumerate(ug.values): ax.text(v+0.3, i, f'{v:.1f}%', va='center', fontsize=9, fontweight='bold')
ax.set_title('Avg Utilisation by Grade', fontweight='bold', color=BLUE)
ax.set_xlabel('Utilisation %'); ax.legend(fontsize=9); ax.set_xlim(0,115)

# 3c — Revenue leakage by client (top 10)
ax = axes[1,0]
rl = timesheets.groupby('client_id').agg(
    billed=('billable_hrs','sum'), unbilled=('unbilled_hrs','sum')
).reset_index()
rl['leakage_lakh'] = rl['unbilled'] * 2.5
rl = rl.merge(clients[['client_id','client_name']])
top_leak = rl.nlargest(10,'leakage_lakh')
lc = [RED if v>200 else ORANGE for v in top_leak['leakage_lakh']]
ax.barh(top_leak['client_name'], top_leak['leakage_lakh'], color=lc, alpha=0.85)
for i,v in enumerate(top_leak['leakage_lakh']): ax.text(v+1, i, f'₹{v:.0f}L', va='center', fontsize=9, fontweight='bold')
ax.set_title('Top 10 Accounts — Revenue Leakage (₹L)', fontweight='bold', color=RED)
ax.set_xlabel('Estimated Lost Revenue (₹ Lakhs)')

# 3d — Weekly unbilled trend
ax = axes[1,1]
wk_unbilled = timesheets.groupby('week')['unbilled_hrs'].sum().reset_index()
ax.fill_between(wk_unbilled['week'], wk_unbilled['unbilled_hrs'], alpha=0.2, color=RED)
ax.plot(wk_unbilled['week'], wk_unbilled['unbilled_hrs'], color=RED, lw=2)
ax.axhline(wk_unbilled['unbilled_hrs'].mean(), color=ORANGE, linestyle='--', lw=1.5, label=f'Avg: {wk_unbilled["unbilled_hrs"].mean():.0f} hrs/week')
ax.set_title('Weekly Unbilled Hours Trend', fontweight='bold', color=BLUE)
ax.set_xlabel('Week'); ax.set_ylabel('Unbilled Hours')
ax.legend(fontsize=9); ax.set_xlim(1,52)

plt.tight_layout()
plt.savefig('screenshots/03_resource_revenue.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("✅ Screenshot 3 — Resource & Revenue")

# ═══════════════════════════════════════════════════════════════════════════
# SCREENSHOT 4 — Watermelon Account Detector
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('🍉 Watermelon Account Detector — Looks Green, Is Red', fontsize=17, fontweight='bold', color=BLUE, y=0.98)
fig.patch.set_facecolor('white')

# 4a — Scatter: surface vs underlying health
ax = axes[0]
normal = health[health['watermelon']==0]
watermelon = health[health['watermelon']==1]
ax.scatter(normal['on_track']*100, normal['health_score'], alpha=0.6, color=GREEN, s=80, label='Genuinely Healthy', zorder=3)
ax.scatter(watermelon['on_track']*100, watermelon['health_score'], alpha=0.9, color=RED, s=120, marker='*', label='🍉 Watermelon Account', zorder=5)
for _, row in watermelon.iterrows():
    ax.annotate(row['client_name'], (row['on_track']*100, row['health_score']),
        textcoords='offset points', xytext=(5,5), fontsize=7.5, color=RED, fontweight='bold')
ax.axhline(60, color=RED, linestyle='--', lw=1.5, alpha=0.7, label='At-Risk threshold (60)')
ax.axvline(60, color=BLUE, linestyle=':', lw=1.5, alpha=0.7, label='Surface "healthy" boundary')
ax.fill_between([60,100],[0,0],[60,60], alpha=0.08, color=RED)
ax.text(75, 30, '⚠️ DANGER ZONE\nLooks healthy,\nis actually at risk', ha='center', fontsize=10, color=RED,
    fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE8E8', edgecolor=RED))
ax.set_xlabel('Projects On Track (%)', fontsize=11)
ax.set_ylabel('Composite Health Score', fontsize=11)
ax.set_title('Surface Health vs True Health Score', fontweight='bold', color=BLUE)
ax.legend(fontsize=9); ax.set_xlim(0,105); ax.set_ylim(0,100)

# 4b — Watermelon detail table
ax = axes[1]; ax.axis('off')
wm_data = health[health['watermelon']==1][['client_name','industry','on_track','health_score','breach_rate','leakage']].copy()
wm_data.columns = ['Account','Industry','On Track %','Health Score','SLA Breach %','Leakage %']
wm_data['On Track %'] = (wm_data['On Track %']*100).round(1)
wm_data['SLA Breach %'] = (wm_data['SLA Breach %']*100).round(1)
wm_data['Leakage %'] = (wm_data['Leakage %']*100).round(1)

if len(wm_data) > 0:
    tbl = ax.table(cellText=wm_data.values, colLabels=wm_data.columns, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1, 1.8)
    for (r,c),cell in tbl.get_celld().items():
        if r==0:
            cell.set_facecolor(BLUE); cell.set_text_props(color='white', fontweight='bold')
        elif r%2==0:
            cell.set_facecolor('#FFF0F0')
        else:
            cell.set_facecolor('#FFF8F8')
    ax.set_title('🍉 Watermelon Accounts — Immediate Action Required', fontweight='bold', color=RED, pad=20, fontsize=12)
else:
    ax.text(0.5,0.5,'No watermelon accounts detected\nin this dataset run.',
        ha='center',va='center',fontsize=14,color=GREEN,transform=ax.transAxes)

plt.tight_layout()
plt.savefig('screenshots/04_watermelon_detector.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("✅ Screenshot 4 — Watermelon Detector")

print("\n🎉 All 4 screenshots saved to screenshots/")
