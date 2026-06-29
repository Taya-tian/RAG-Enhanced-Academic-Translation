import os
import json
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Callable, Optional
from itertools import product


# ========================================================================
# 第 1 步：加载两个方向的 CSV，统一为中英句对结构
# ========================================================================
def load_and_unify_corpus(
    zh2en_csv: str,
    en2zh_csv: str,
    zh2en_cols: tuple = ('source_zh', 'target_en'),  # 按你的列名改
    en2zh_cols: tuple = ('source_en', 'target_zh'),  # 按你的列名改
) -> List[Dict]:
    """
    统一结构：无论原始方向，一律变成 {zh, en, direction, zh_is_source}
    """
    corpus = []

    # 汉译英子库：中文=原文，英文=译文
    df1 = pd.read_csv(zh2en_csv)
    for _, row in df1.iterrows():
        zh = str(row[zh2en_cols[0]]).strip()
        en = str(row[zh2en_cols[1]]).strip()
        if zh and en and zh != 'nan' and en != 'nan':
            corpus.append({
                'zh': zh, 'en': en,
                'direction': 'zh2en',
                'zh_is_source': True,
            })

    # 英译汉子库：英文=原文，中文=译文
    df2 = pd.read_csv(en2zh_csv)
    for _, row in df2.iterrows():
        en = str(row[en2zh_cols[0]]).strip()
        zh = str(row[en2zh_cols[1]]).strip()
        if zh and en and zh != 'nan' and en != 'nan':
            corpus.append({
                'zh': zh, 'en': en,
                'direction': 'en2zh',
                'zh_is_source': False,
            })

    n_zh2en = sum(1 for c in corpus if c['direction'] == 'zh2en')
    n_en2zh = sum(1 for c in corpus if c['direction'] == 'en2zh')
    print(f"[语料统计] 汉译英 = {n_zh2en} | 英译汉 = {n_en2zh} | 合计 = {len(corpus)}")
    return corpus


def filter_by_subset(corpus: List[Dict], subset: str) -> List[Dict]:
    """按方向子集过滤"""
    if subset == 'zh2en_only':
        return [c for c in corpus if c['direction'] == 'zh2en']
    if subset == 'en2zh_only':
        return [c for c in corpus if c['direction'] == 'en2zh']
    if subset == 'merged':
        return corpus
    raise ValueError(f"未知 subset: {subset}")


# ========================================================================
# 第 2 步：检索器（支持粒度 × 子集的任意组合）
# ========================================================================
class Retriever:
    def __init__(self, corpus: List[Dict], granularity: str,
                 model: SentenceTransformer):
        assert granularity in ('src', 'tgt', 'concat')
        self.corpus = corpus
        self.granularity = granularity
        self.model = model
        self.texts = self._texts_for_index()
        self.index = self._build_index()

    def _texts_for_index(self) -> List[str]:
        if self.granularity == 'src':
            return [c['zh'] for c in self.corpus]       # 中文侧
        if self.granularity == 'tgt':
            return [c['en'] for c in self.corpus]       # 英文侧
        return [f"{c['zh']} [SEP] {c['en']}" for c in self.corpus]

    def _build_index(self):
        if len(self.texts) == 0:
            return None
        emb = self.model.encode(
            self.texts, batch_size=64,
            show_progress_bar=False, normalize_embeddings=True,
        ).astype('float32')
        idx = faiss.IndexFlatIP(emb.shape[1])
        idx.add(emb)
        return idx

    def retrieve(self, query_zh: str, top_k: int = 5,
                 sim_cutoff: float = 0.5) -> List[Dict]:
        if self.index is None:
            return []
        q = self.model.encode(
            [query_zh], normalize_embeddings=True
        ).astype('float32')
        scores, ids = self.index.search(q, top_k * 3)
        hits = []
        for s, i in zip(scores[0], ids[0]):
            if i < 0 or s < sim_cutoff:
                continue
            c = self.corpus[i]
            hits.append({
                'zh': c['zh'], 'en': c['en'],
                'direction': c['direction'],
                'score': float(s),
            })
            if len(hits) >= top_k:
                break
        return hits


# ========================================================================
# 第 3 步：Prompt 构建（汉译英方向）
# ========================================================================
def build_prompt(query_zh: str, retrieved: List[Dict]) -> str:
    if not retrieved:
        return (
            "You are a professional academic translator. "
            "Translate the following Chinese sentence into English:\n\n"
            f"中文：{query_zh}\nEnglish:"
        )
    examples = "\n\n".join(
        f"中文：{r['zh']}\nEnglish: {r['en']}" for r in retrieved
    )
    return (
        "You are a professional academic translator. "
        "The following Chinese-English translation pairs were written by the "
        "same author in the same period. Use them as references for "
        "terminology and style, then translate the final Chinese sentence "
        "into academically accurate English.\n\n"
        f"Reference pairs:\n{examples}\n\n"
        f"中文：{query_zh}\nEnglish:"
    )


# ========================================================================
# 第 4 步：双重敏感性实验主流程
# ========================================================================
def run_experiment(
    zh2en_csv: str,
    en2zh_csv: str,
    test_queries: List[Dict],            # [{"zh": ..., "en_ref": ...}, ...]
    top_k: int = 5,
    sim_cutoff: float = 0.5,
    model_name: str = 'sentence-transformers/LaBSE',
    llm_translate_func: Optional[Callable[[str], str]] = None,
    out_dir: str = './rag_results',
    zh2en_cols: tuple = ('source_zh', 'target_en'),
    en2zh_cols: tuple = ('source_en', 'target_zh'),
):
    os.makedirs(out_dir, exist_ok=True)

    # ---- 1. 加载语料 ----
    full_corpus = load_and_unify_corpus(
        zh2en_csv, en2zh_csv, zh2en_cols, en2zh_cols
    )

    # ---- 2. 加载编码器 ----
    print(f"[模型加载] {model_name}")
    model = SentenceTransformer(model_name)

    # ---- 3. 预构建 9 个检索器 ----
    GRANS = ['src', 'tgt', 'concat']
    SUBSETS = ['zh2en_only', 'en2zh_only', 'merged']
    retrievers: Dict[tuple, Retriever] = {}

    print("\n[检索器构建]")
    for subset in SUBSETS:
        sub = filter_by_subset(full_corpus, subset)
        print(f"  子集 {subset:12s} 规模 = {len(sub)}")
        for gran in GRANS:
            retrievers[(gran, subset)] = Retriever(sub, gran, model)

    # ---- 4. 遍历 queries × 9 种条件 ----
    rows = []
    for qi, q in enumerate(test_queries):
        query_zh = q['zh']
        en_ref = q.get('en_ref', '')
        print(f"\n===== Query {qi+1}/{len(test_queries)} =====")
        print(f"中文：{query_zh[:70]}...")

        for gran, subset in product(GRANS, SUBSETS):
            retriever = retrievers[(gran, subset)]
            hits = retriever.retrieve(query_zh, top_k, sim_cutoff)
            prompt = build_prompt(query_zh, hits)

            if llm_translate_func is not None:
                try:
                    translation = llm_translate_func(prompt)
                except Exception as e:
                    translation = f"[LLM_ERROR] {e}"
            else:
                translation = "[LLM_PLACEHOLDER]"

            n_zh2en = sum(1 for h in hits if h['direction'] == 'zh2en')
            n_en2zh = sum(1 for h in hits if h['direction'] == 'en2zh')
            avg_score = float(np.mean([h['score'] for h in hits])) if hits else 0.0

            rows.append({
                'query_id': qi,
                'query_zh': query_zh,
                'en_ref': en_ref,
                'granularity': gran,
                'kb_subset': subset,
                'num_retrieved': len(hits),
                'n_from_zh2en': n_zh2en,
                'n_from_en2zh': n_en2zh,
                'avg_sim_score': round(avg_score, 4),
                'retrieved_pairs': json.dumps(hits, ensure_ascii=False),
                'prompt': prompt,
                'translation': translation,
            })

            print(f"  [{gran:6s} | {subset:12s}] "
                  f"hits={len(hits):2d} "
                  f"(zh2en={n_zh2en}, en2zh={n_en2zh}) "
                  f"avg_sim={avg_score:.3f}")

    # ---- 5. 保存与汇总 ----
    df = pd.DataFrame(rows)
    res_path = os.path.join(out_dir, 'full_results.csv')
    df.to_csv(res_path, index=False, encoding='utf-8-sig')
    print(f"\n[已保存] 明细结果 → {res_path}")

    # 透视表 1：平均检索相似度
    piv_sim = df.pivot_table(
        index='granularity', columns='kb_subset',
        values='avg_sim_score', aggfunc='mean',
    ).round(3)
    # 透视表 2：平均命中条数
    piv_hits = df.pivot_table(
        index='granularity', columns='kb_subset',
        values='num_retrieved', aggfunc='mean',
    ).round(2)
    # 透视表 3：合并子集下 zh2en 方向句对的平均占比
    merged_df = df[df['kb_subset'] == 'merged'].copy()
    merged_df['zh2en_ratio'] = merged_df['n_from_zh2en'] / merged_df['num_retrieved'].replace(0, np.nan)
    piv_ratio = merged_df.pivot_table(
        index='granularity', values='zh2en_ratio', aggfunc='mean',
    ).round(3)

    print("\n===== 透视表 1：各条件平均检索相似度 =====")
    print(piv_sim)
    print("\n===== 透视表 2：各条件平均命中条数 =====")
    print(piv_hits)
    print("\n===== 透视表 3：合并子集下 zh2en 句对占比（揭示检索偏好）=====")
    print(piv_ratio)

    piv_sim.to_csv(os.path.join(out_dir, 'pivot_sim.csv'), encoding='utf-8-sig')
    piv_hits.to_csv(os.path.join(out_dir, 'pivot_hits.csv'), encoding='utf-8-sig')
    piv_ratio.to_csv(os.path.join(out_dir, 'pivot_zh2en_ratio.csv'), encoding='utf-8-sig')
    print(f"\n[已保存] 透视表 → {out_dir}/pivot_*.csv")

    return df


# ========================================================================
# 第 5 步：使用示例
# ========================================================================
if __name__ == "__main__":

    # --- 5.1 准备测试集（你的待译文本，中文） ---
    test_queries = [
        {
            "zh": "神经网络的发展彻底革新了机器翻译领域。",
            "en_ref": "The development of neural networks has revolutionized machine translation."
        },
        {
            "zh": "本文提出一种基于检索增强的翻译质量评估方法。",
            "en_ref": "This paper proposes a retrieval-augmented approach to translation quality assessment."
        },
        # ... 继续加
    ]

    # --- 5.2 可选：接入真实 LLM ---
    # def my_llm(prompt: str) -> str:
    #     from openai import OpenAI
    #     client = OpenAI()
    #     resp = client.chat.completions.create(
    #         model="gpt-4o",
    #         messages=[{"role": "user", "content": prompt}],
    #         temperature=0.2,
    #     )
    #     return resp.choices[0].message.content.strip()

    df = run_experiment(
        zh2en_csv='kb_zh2en.csv',
        en2zh_csv='kb_en2zh.csv',
        test_queries=test_queries,
        top_k=5,
        sim_cutoff=0.5,
        model_name='sentence-transformers/LaBSE',   # 支持中英跨语言
        llm_translate_func=None,                    # 或替换为 my_llm
        out_dir='./rag_results',
        zh2en_cols=('source_zh', 'target_en'),      # 改成你 CSV 的真实列名
        en2zh_cols=('source_en', 'target_zh'),      # 改成你 CSV 的真实列名
    )