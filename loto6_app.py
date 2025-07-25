# loto6_app.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib
import os
import base64
import random
from datetime import datetime
from collections import Counter
from itertools import combinations

# --- フォント設定 ---
font_path = "ipaexg.ttf"
font_prop = fm.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['font.family'] = font_prop.get_name()

# --- 月別CSV選択 ---
st.title("ロト6出現数字分析アプリ")
st.markdown("## 月別データから分析")

monthly_dir = "monthly_data"
monthly_files = [f for f in os.listdir(monthly_dir) if f.endswith(".csv")]
available_months = sorted([f.replace(".csv", "") for f in monthly_files], reverse=True)
selected_month = st.selectbox("📅 分析対象の月を選んでください", available_months)
csv_path = os.path.join(monthly_dir, f"{selected_month}.csv")

# --- データ読み込み・前処理 ---
df = pd.read_csv(csv_path)
number_cols = [f"num{i}" for i in range(1, 7)]
df[number_cols] = df["本数字"].str.split(" ", expand=True).astype(int)
all_numbers = pd.Series(df[number_cols].values.ravel())
freq = all_numbers.value_counts().sort_values(ascending=False)
all_possible = set(range(1, 44))
existing = set(freq.index)
unused = sorted(all_possible - existing)
pair_counter = Counter()
for row in df[number_cols].values:
    pair_counter.update(combinations(sorted(row), 2))

# --- ロジック定義 ---
def generate_from_frequent():
    return sorted(random.sample(freq.head(10).index.tolist(), 6))

def generate_from_unused():
    if len(unused) >= 6:
        return sorted(random.sample(unused, 6))
    else:
        return sorted(random.sample(range(1, 44), 6))

def generate_balanced_odd_even():
    odd = [n for n in range(1, 44) if n % 2 == 1]
    even = [n for n in range(1, 44) if n % 2 == 0]
    return sorted(random.sample(odd, 3) + random.sample(even, 3))

def generate_with_consecutive():
    base = random.randint(1, 42)
    pair = [base, base + 1]
    others = random.sample([n for n in range(1, 44) if n not in pair], 4)
    return sorted(pair + others)

def generate_with_common_pair():
    pair = pair_counter.most_common(1)[0][0]
    others = random.sample([n for n in range(1, 44) if n not in pair], 4)
    return sorted(list(pair) + others)

strategies = {
    "頻出数字から生成": generate_from_frequent,
    "未出数字から生成": generate_from_unused,
    "奇数偶数バランス型": generate_balanced_odd_even,
    "連続数字を含む": generate_with_consecutive,
    "よく出るペアを含む": generate_with_common_pair,
}

st.markdown("---")
st.subheader("🎲 おすすめ数字自動生成（選択月のデータから）")

selected_strategy_name = st.selectbox("🧠 ロジックを選択してください", list(strategies.keys()))
selected_strategy = strategies[selected_strategy_name]

if st.button("🔁 数字を再生成"):
    st.session_state.generated_numbers = [selected_strategy() for _ in range(5)]

if "generated_numbers" not in st.session_state:
    st.session_state.generated_numbers = [selected_strategy() for _ in range(5)]

st.markdown("#### 💡 今回のロジック：" + selected_strategy_name)
for i, nums in enumerate(st.session_state.generated_numbers, 1):
    st.success(f"{i}口目: " + "、".join(map(str, nums)))
