# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
import seaborn as sns

# 设置中文字体：优先 macOS/Linux 可用字体，再回退到 Windows 字体
def _setup_chinese_font():
    # 按平台常见字体排序，保证中文正确显示
    candidates = [
        'PingFang SC',           # macOS 苹方
        'Heiti SC',              # macOS 黑体
        'STHeiti',               # macOS
        'Hiragino Sans GB',      # macOS
        'WenQuanYi Micro Hei',   # Linux
        'Noto Sans CJK SC',      # Linux
        'SimHei',                # Windows
        'Microsoft YaHei',       # Windows
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams['font.sans-serif'] = [name]
            return
    # 若都未找到，用 matplotlib 默认支持 CJK 的字体（如 DejaVu 不支持，则至少不报错）
    plt.rcParams['font.sans-serif'] = candidates[:1]

_setup_chinese_font()
plt.rcParams['axes.unicode_minus'] = False

# 数据
models = ['HET\n(人类专家)', 'RCT\n(RAG-ChatGPT)', 'COT\n(ChatGPT-Only)']
total_deductions = [-14, -171.5, -176]
error_counts = [7, 92, 100]
error_density = [0.95, 12.43, 13.51]

# 创建图表
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 子图1：总扣分对比
colors = ['#2ecc71', '#e74c3c', '#e67e22']
bars1 = axes[0].bar(models, total_deductions, color=colors, alpha=0.8, edgecolor='black')
axes[0].set_ylabel('总扣分', fontsize=12, fontweight='bold')
axes[0].set_title('(a) 总扣分对比', fontsize=14, fontweight='bold')
axes[0].axhline(y=0, color='black', linestyle='--', linewidth=0.8)
axes[0].grid(axis='y', alpha=0.3)
# 添加数值标签（负值条形图：标签放在条形内侧居中，避免被底边裁切）
for bar, val in zip(bars1, total_deductions):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height()/2,
                f'{val}', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# 子图2：错误次数
bars2 = axes[1].bar(models, error_counts, color=colors, alpha=0.8, edgecolor='black')
axes[1].set_ylabel('错误次数', fontsize=12, fontweight='bold')
axes[1].set_title('(b) 错误次数对比', fontsize=14, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)
axes[1].set_ylim(0, max(error_counts) * 1.12)  # 留出顶部空间，避免数值被裁切
for bar, val in zip(bars2, error_counts):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val}次', ha='center', va='bottom', fontsize=11, fontweight='bold')

# 子图3：标准化错误密度（核心指标）
bars3 = axes[2].bar(models, error_density, color=colors, alpha=0.8, edgecolor='black')
axes[2].set_ylabel('错误密度（错误/千源文字）', fontsize=12, fontweight='bold')
axes[2].set_title('(c) 标准化错误密度对比 ★', fontsize=14, fontweight='bold')
axes[2].grid(axis='y', alpha=0.3)
axes[2].set_ylim(0, max(error_density) * 1.12)  # 留出顶部空间，避免数值被裁切
for bar, val in zip(bars3, error_density):
    axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# 添加HET优势标注
axes[2].annotate('HET仅为RAG/COT的\n7.6%/7.0%', 
                xy=(0, error_density[0]), xytext=(0.5, 5),
                arrowprops=dict(arrowstyle='->', color='green', lw=2),
                fontsize=10, color='green', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))

plt.tight_layout()
plt.savefig('图1_总扣分统计.png', dpi=300, bbox_inches='tight')
plt.show()