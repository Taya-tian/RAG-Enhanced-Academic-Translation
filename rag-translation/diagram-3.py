# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
import seaborn as sns

# 符号用此字体可正确显示 ✓ ✗（CJK 字体常不包含）
_symbol_font = FontProperties(family='DejaVu Sans', size=10)

# 设置中文字体：优先 macOS/Linux 可用字体，再回退到 Windows 字体
def _setup_chinese_font():
    candidates = [
        'PingFang SC', 'Heiti SC', 'STHeiti', 'Hiragino Sans GB',
        'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei', 'Microsoft YaHei',
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams['font.sans-serif'] = [name]
            return
    plt.rcParams['font.sans-serif'] = candidates[:1]

_setup_chinese_font()
plt.rcParams['axes.unicode_minus'] = False

# 数据
dimensions = ['A. 基础\n翻译质量', 'B. 学术\n概念准确性', 'C. 语篇\n衔接性', 
              'D. 语篇\n连贯性', 'E. 风格\n适切性', '总计']
cot_scores = [-111, -31, -18, -10, -6, -176]
rct_scores = [-112, -27, -25, -4, -3.5, -171.5]
# 改善值/率：正=变好（RCT 更好），负=变差（RCT 更差）
improvements = [rct - cot for cot, rct in zip(cot_scores, rct_scores)]
improvement_rates = [(rct - cot) / abs(cot) * 100 if cot != 0 else 0
                     for cot, rct in zip(cot_scores, rct_scores)]

# 创建瀑布图
fig, ax = plt.subplots(figsize=(14, 7))

colors = ['red' if x < 0 else 'green' for x in improvements[:-1]] + ['blue']
bars = ax.bar(range(len(dimensions)), improvements, color=colors, alpha=0.7, edgecolor='black')

# 添加数值标签
for i, (bar, val, rate) in enumerate(zip(bars, improvements, improvement_rates)):
    # 改善值
    y_pos = bar.get_height() + (0.5 if val > 0 else -0.5)
    ax.text(bar.get_x() + bar.get_width()/2, y_pos, 
           f'{val:+.1f}', ha='center', va='bottom' if val > 0 else 'top',
           fontsize=11, fontweight='bold')
    # 改善率
    if i < len(dimensions) - 1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
               f'{rate:+.1f}%', ha='center', va='center',
               fontsize=9, color='white', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.6))

ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
ax.set_ylabel('改善值（负值=恶化）', fontsize=13, fontweight='bold')
ax.set_xlabel('维度', fontsize=13, fontweight='bold')
ax.set_title('图3 RAG技术对ChatGPT各维度的改善/恶化效果\n（绿色=改善，红色=恶化）', 
            fontsize=15, fontweight='bold')
ax.set_xticks(range(len(dimensions)))
ax.set_xticklabels(dimensions, fontsize=11)
ax.grid(axis='y', alpha=0.3)

# 添加关键发现标注（符号用 DejaVu Sans 单独绘制，保证 ✓✗ 正确显示）
ax.annotate('严重恶化\n-38.89%', xy=(2, improvements[2]), xytext=(2.58, improvements[2] / 2),
           arrowprops=dict(arrowstyle='->', color='red', lw=2),
           fontsize=10, color='red', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='mistyrose'))
ax.text(2.48, improvements[2] / 2, '\u2717', fontproperties=_symbol_font, color='red',
        fontweight='bold', va='center', ha='right')  # ✗ U+2717

ax.annotate('显著改善\n+60.00%', xy=(3, improvements[3]), xytext=(3.53, 3),
           arrowprops=dict(arrowstyle='->', color='green', lw=2),
           fontsize=10, color='green', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen'))
ax.text(3.43, 3, '\u2713', fontproperties=_symbol_font, color='green',
        fontweight='bold', va='center', ha='right')  # ✓ U+2713

plt.tight_layout()
plt.savefig('图3_RAG改善恶化瀑布图.png', dpi=300, bbox_inches='tight')
plt.show()