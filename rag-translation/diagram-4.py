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

# A维度数据
a_types = ['漏译', '误译', '增译']
a_cot = [4, 51, 1]
a_rct = [15, 41, 0]

# B维度数据
b_types = ['术语\n不一致', '术语脱离\n语境', '关键概念\n误译', '术语过度\n字面化']
b_cot = [1, 8, 5, 3]
b_rct = [2, 6, 5, 1]

# C维度数据
c_types = ['连接失效', '词汇衔接\n断裂', '指称错误', '替代不当']
c_cot = [3, 5, 1, 1]
c_rct = [5, 7, 1, 0]

# 创建图表
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# A维度
x1 = np.arange(len(a_types))
width = 0.35
axes[0].bar(x1 - width/2, a_cot, width, label='COT', color='#e67e22', alpha=0.8, edgecolor='black')
axes[0].bar(x1 + width/2, a_rct, width, label='RCT', color='#e74c3c', alpha=0.8, edgecolor='black')
axes[0].set_title('图4(a) A维度：基础翻译质量\n[注意] 漏译激增275%', fontsize=12, fontweight='bold')
axes[0].set_ylabel('错误次数', fontsize=11)
axes[0].set_xticks(x1)
axes[0].set_xticklabels(a_types, fontsize=10)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# 标注关键数据
axes[0].annotate('', xy=(0, 15), xytext=(0, 4),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
axes[0].text(0.2, 9.5, '+275%', fontsize=10, color='darkred', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='darkred'))

# B维度
x2 = np.arange(len(b_types))
axes[1].bar(x2 - width/2, b_cot, width, label='COT', color='#e67e22', alpha=0.8, edgecolor='black')
axes[1].bar(x2 + width/2, b_rct, width, label='RCT', color='#e74c3c', alpha=0.8, edgecolor='black')
axes[1].set_title('图4(b) B维度：学术概念准确性\n[改善] 术语脱离语境改善25%', fontsize=12, fontweight='bold')
axes[1].set_ylabel('错误次数', fontsize=11)
axes[1].set_xticks(x2)
axes[1].set_xticklabels(b_types, fontsize=9)
axes[1].legend()
axes[1].grid(axis='y', alpha=0.3)

# C维度
x3 = np.arange(len(c_types))
axes[2].bar(x3 - width/2, c_cot, width, label='COT', color='#e67e22', alpha=0.8, edgecolor='black')
axes[2].bar(x3 + width/2, c_rct, width, label='RCT', color='#e74c3c', alpha=0.8, edgecolor='black')
axes[2].set_title('图4(c) C维度：语篇衔接性\n[恶化] 连接失效+66.6%', fontsize=12, fontweight='bold')
axes[2].set_ylabel('错误次数', fontsize=11)
axes[2].set_xticks(x3)
axes[2].set_xticklabels(c_types, fontsize=9)
axes[2].legend()
axes[2].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('图4_子维度详细对比.png', dpi=300, bbox_inches='tight')
plt.show()