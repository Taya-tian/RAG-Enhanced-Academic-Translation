# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
import seaborn as sns

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
dimensions = ['A. 基础翻译\n质量', 'B. 学术概念\n准确性', 
              'C. 语篇\n衔接性', 'D. 语篇\n连贯性', 'E. 风格\n适切性']
het_scores = [-8, -6, 0, 0, 0]
rct_scores = [-112, -27, -25, -4, -3.5]
cot_scores = [-111, -31, -18, -10, -6]

# 创建图表
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 子图1：分组柱状图
x = np.arange(len(dimensions))
width = 0.25

bars1 = axes[0].bar(x - width, het_scores, width, label='HET', color='#2ecc71', alpha=0.8, edgecolor='black')
bars2 = axes[0].bar(x, rct_scores, width, label='RCT', color='#e74c3c', alpha=0.8, edgecolor='black')
bars3 = axes[0].bar(x + width, cot_scores, width, label='COT', color='#e67e22', alpha=0.8, edgecolor='black')

axes[0].set_ylabel('扣分', fontsize=12, fontweight='bold')
axes[0].set_title('图2(a) 五维度扣分对比', fontsize=14, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(dimensions, fontsize=10)
axes[0].legend(fontsize=11, loc='lower right')
axes[0].axhline(y=0, color='black', linestyle='--', linewidth=0.8)
axes[0].grid(axis='y', alpha=0.3)

# 子图2：热力图（展示问题严重程度）
heatmap_data = np.array([het_scores, rct_scores, cot_scores])
sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlGn', 
            cbar_kws={'label': '扣分程度'}, ax=axes[1],
            xticklabels=['A', 'B', 'C', 'D', 'E'],
            yticklabels=['HET', 'RCT', 'COT'],
            linewidths=0.5, linecolor='gray')
axes[1].set_title('图2(b) 五维度问题严重程度热力图', fontsize=14, fontweight='bold')
axes[1].set_xlabel('维度', fontsize=12)

plt.tight_layout()
plt.savefig('图2_五维度对比.png', dpi=300, bbox_inches='tight')
plt.show()
