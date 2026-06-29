# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
import seaborn as sns
from matplotlib.patches import Rectangle

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

fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('off')

# 表格数据
categories = ['翻译单位', '知识调用', '主动管理']
het_data = ['段落-篇章级', '深度理解\n（学科训练）', '主动决策\n（术语表+风格调整）']
rct_data = ['句子级', '检索碎片\n（Top-10, ≥0.4）', '被动依赖RAG']
cot_data = ['短语-句子级', '表层对应\n（预训练参数）', '无干预']

# 表格位置
y_start = 0.85
row_height = 0.15
col_widths = [0.18, 0.27, 0.27, 0.27]

# 标题行
headers = ['维度', 'HET', 'RCT', 'COT']
colors_header = ['#34495e', '#2ecc71', '#e74c3c', '#e67e22']
x_pos = 0
for header, width, color in zip(headers, col_widths, colors_header):
    rect = Rectangle((x_pos, y_start), width, 0.08, 
                     facecolor=color, edgecolor='white', linewidth=2)
    ax.add_patch(rect)
    ax.text(x_pos + width/2, y_start + 0.04, header, 
           ha='center', va='center', fontsize=13, fontweight='bold', color='white')
    x_pos += width

# 数据行
for i, (cat, het, rct, cot) in enumerate(zip(categories, het_data, rct_data, cot_data)):
    y_pos = y_start - (i+1) * row_height
    row_data = [cat, het, rct, cot]
    row_colors = ['#ecf0f1', '#d5f4e6', '#fadbd8', '#fdebd0']
    
    x_pos = 0
    for data, width, color in zip(row_data, col_widths, row_colors):
        rect = Rectangle((x_pos, y_pos), width, row_height, 
                        facecolor=color, edgecolor='gray', linewidth=1)
        ax.add_patch(rect)
        ax.text(x_pos + width/2, y_pos + row_height/2, data, 
               ha='center', va='center', fontsize=10, 
               fontweight='bold' if x_pos == 0 else 'normal',
               wrap=True)
        x_pos += width

# 添加总结性标注
ax.text(0.5, 0.20, '关键发现：HET的优势在于"大单位+深理解+主动决策"\nRAG的局限在于"碎片化知识+被动响应"', 
       ha='center', va='center', fontsize=12, fontweight='bold',
       bbox=dict(boxstyle='round,pad=1', facecolor='lightyellow', edgecolor='orange', linewidth=2))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.title('图5 三译本核心差异对比', fontsize=16, fontweight='bold', pad=20)
plt.savefig('图5_三译本核心差异.png', dpi=300, bbox_inches='tight')
plt.show()