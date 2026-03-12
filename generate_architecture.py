"""Generate a clean architecture diagram for the README"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 9))
ax.set_xlim(0, 14); ax.set_ylim(0, 9)
ax.axis('off')
fig.patch.set_facecolor('white')

BLUE='#1A3C6E'; ACCENT='#2563A8'; GREEN='#27AE60'; ORANGE='#E67E22'
RED='#C0392B'; LIGHT='#EEF4FB'; GRAY='#95A5A6'; PURPLE='#8E44AD'

def box(ax, x, y, w, h, label, sublabel, color, text_color='white'):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
        boxstyle='round,pad=0.15', facecolor=color, edgecolor='white', linewidth=2, zorder=3))
    ax.text(x, y+0.12, label, ha='center', va='center', fontsize=11,
        fontweight='bold', color=text_color, zorder=4)
    if sublabel:
        ax.text(x, y-0.25, sublabel, ha='center', va='center', fontsize=8.5,
            color=text_color, alpha=0.9, zorder=4)

def arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
        arrowprops=dict(arrowstyle='->', color=GRAY, lw=2), zorder=2)

# Title
ax.text(7, 8.5, 'Client Delivery Intelligence — System Architecture',
    ha='center', va='center', fontsize=16, fontweight='bold', color=BLUE)

# Row 1 — Data Sources
y1 = 7.4
box(ax, 2.5, y1, 2.8, 0.75, 'Raw Data Sources', 'Clients • Projects • Tickets\nTimesheets • Consultants', ACCENT)

# Row 2 — Data Generation
y2 = 6.2
box(ax, 2.5, y2, 2.8, 0.75, 'Data Generation', 'generate_data.py\n5 tables • 15,455 records', '#16A085')

# Row 3 — Analytics layer (3 boxes side by side)
y3 = 4.8
box(ax, 1.8, y3, 2.6, 0.8, 'EDA & Delivery', 'Notebook 01\nProject health overview', BLUE)
box(ax, 4.8, y3, 2.6, 0.8, 'SLA Prediction', 'Notebooks 02–03\nBreach forecasting', ORANGE)
box(ax, 7.8, y3, 2.6, 0.8, 'Revenue Leakage', 'Notebook 04\nUnbilled hours model', RED)

# Row 4 — SQL Layer
y4 = 3.4
box(ax, 4.8, y4, 5.5, 0.75, 'SQL Analytics Layer', 'delivery_analytics.sql — 5 production queries\nSLA trends • Utilisation • Watermelon detection', '#7F8C8D')

# Row 5 — Health Score
y5 = 2.1
box(ax, 4.8, y5, 5.5, 0.8, 'Client Health Score Engine', 'Notebook 05 — Composite scoring\nSLA (30%) + Delivery (35%) + Revenue (20%) + Trend (15%)', PURPLE)

# Row 6 — Outputs (3 boxes)
y6 = 0.85
box(ax, 2.2, y6, 3.0, 0.75, 'Visual Dashboards', '4 screenshot-quality\ncharts & heatmaps', GREEN)
box(ax, 5.5, y6, 3.0, 0.75, 'Watermelon Alerts', 'Silent failure detection\nAccount risk flags', RED)
box(ax, 8.8, y6, 3.0, 0.75, 'Executive Briefing', 'docs/executive_briefing.md\nLeadership 1-pager', ACCENT)

# Arrows
arrow(ax, 2.5, 7.02, 2.5, 6.58)   # sources → generation
arrow(ax, 2.5, 5.83, 1.8, 5.2)    # generation → EDA
arrow(ax, 2.5, 5.83, 4.8, 5.2)    # generation → SLA
arrow(ax, 2.5, 5.83, 7.8, 5.2)    # generation → Revenue
arrow(ax, 1.8, 4.4, 4.0, 3.78)    # EDA → SQL
arrow(ax, 4.8, 4.4, 4.8, 3.78)    # SLA → SQL
arrow(ax, 7.8, 4.4, 5.6, 3.78)    # Revenue → SQL
arrow(ax, 4.8, 3.02, 4.8, 2.5)    # SQL → Health Score
arrow(ax, 3.5, 1.7, 2.5, 1.23)    # Health → Dashboards
arrow(ax, 4.8, 1.7, 5.2, 1.23)    # Health → Watermelon
arrow(ax, 6.1, 1.7, 8.1, 1.23)    # Health → Briefing

# Legend
legend_items = [
    mpatches.Patch(color=ACCENT,  label='Data Layer'),
    mpatches.Patch(color='#16A085', label='Generation'),
    mpatches.Patch(color=BLUE,    label='Analysis Notebooks'),
    mpatches.Patch(color='#7F8C8D', label='SQL Layer'),
    mpatches.Patch(color=PURPLE,  label='ML / Scoring'),
    mpatches.Patch(color=GREEN,   label='Outputs'),
]
ax.legend(handles=legend_items, loc='upper right', fontsize=8.5,
    framealpha=0.9, edgecolor=GRAY, bbox_to_anchor=(0.99, 0.97))

plt.tight_layout()
plt.savefig('docs/architecture_diagram.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("✅ Architecture diagram saved to docs/architecture_diagram.png")
