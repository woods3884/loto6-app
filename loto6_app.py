# loto6_app.py

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib

import base64
import os
from datetime import datetime
from collections import Counter
from itertools import combinations

# --- 🎌 日本語フォント設定（ipaexg.ttfをプロジェクト直下に配置） ---
font_path = "ipaexg.ttf"
font_prop = fm.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()

# --- 📄 PDFレポートダウンロードセクション ---
st.markdown("### 📄 PDFレポートダウンロード")

today = datetime.today()
months = [today.replace(day=1).strftime("%Y-%m")]
for i in range(1, 12):
    prev = today.replace(day=1) - pd.DateOffset(months=i)
    months.append(prev.strftime("%Y-%m"))

selected_month = st.selectbox("📅 表示したい月を選んでください", sorted(months, reverse=True))
pdf_filename = f"{selected_month}_report.pdf"

if os.path.exists(pdf_filename):
    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()
        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">📥 {pdf_filename} をダウンロード</a>'
        st.markdown(pdf_link, unsafe_allow_html=True)
else:
    st.warning(f"⚠️ {pdf_filename} は見つかりません。")

# --- 📊 データ読み込みと加工 ---
df = pd.read_csv("loto6_past_100.csv")
number_cols = [f"num{i}" for i in range(1, 7)]
df[number_cols] = df["本数字"].str.split(" ", expand=True).astype(int)

# --- 頻出数字 ---
all_numbers = pd.Series(df[number_cols].values.ravel())
freq = all_numbers.value_counts().sort_values(ascending=False)

# --- 未出数字 ---
all_possible = set(range(1, 44))
unused = sorted(all_possible - set(freq.index))

# --- 奇数・偶数 ---
odd = all_numbers[all_numbers % 2 == 1].count()
even = all_numbers[all_numbers % 2 == 0].count()

# --- 連続数字検出 ---
def count_consecutive(row):
    nums = sorted(row)
    return sum(1 for i in range(len(nums)-1) if nums[i+1] - nums[i] == 1)

df["連続数"] = df[number_cols].apply(count_consecutive, axis=1)
consec_counts = df["連続数"].value_counts().sort_index()

# --- ポジション別出現傾向 ---
def get_position_counts():
    position_df = pd.DataFrame()
    for pos in number_cols:
        counts = df[pos].value_counts()
        position_df[pos] = counts
    return position_df.fillna(0).astype(int).sort_index()

position_df = get_position_counts()

# --- Streamlit UI 表示 ---
st.title("ロト6出現数字分析アプリ")

st.subheader("📈 頻出数字ランキング")
for num, count in freq.head(10).items():
    st.write(f"{num}：{count}回")

st.subheader("🔍 未出数字")
st.write(unused)

st.subheader("⚖️ 奇数・偶数の比率")
st.write(f"奇数：{odd} 個")
st.write(f"偶数：{even} 個")

st.subheader("📊 連続数字の出現パターン")
fig1, ax1 = plt.subplots()
ax1.bar(consec_counts.index, consec_counts.values)
ax1.set_xlabel("連続数字の個数")
ax1.set_ylabel("出現回数")
ax1.set_title("連続数字の出現回数")
st.pyplot(fig1)

st.subheader("📊 ポジション別出現傾向（棒グラフ）")
fig2, ax2 = plt.subplots(figsize=(12, 6))
position_df.plot(kind="bar", ax=ax2)
ax2.set_xlabel("数字")
ax2.set_ylabel("出現回数")
ax2.set_title("各ポジションにおける数字の出現回数")
st.pyplot(fig2)

st.subheader("📊 ポジション×数字の出現ヒートマップ")
fig3, ax3 = plt.subplots(figsize=(14, 8))
sns.heatmap(position_df.T, cmap="YlOrRd", linewidths=0.5, annot=True, fmt="d", cbar_kws={'label': '出現回数'}, ax=ax3)
ax3.set_xlabel("数字")
ax3.set_ylabel("ポジション")
ax3.set_title("ポジションごとの数字出現ヒートマップ")
st.pyplot(fig3)

# --- 📈 累積出現回数の推移 ---
st.markdown("---")
st.subheader("📈 数字ごとの出現回数の推移（累計）")

number_counts = {i: [] for i in range(1, 44)}
cumulative_counts = {i: 0 for i in range(1, 44)}
x_labels = df["抽選日"].tolist()

for _, row in df.iterrows():
    numbers = list(map(int, row["本数字"].split()))
    for i in range(1, 44):
        if i in numbers:
            cumulative_counts[i] += 1
        number_counts[i].append(cumulative_counts[i])

selected_numbers = st.multiselect("表示する数字を選んでください（複数選択可）", options=list(range(1, 44)), default=[6, 19, 38])

fig, ax = plt.subplots(figsize=(10, 5))
for num in selected_numbers:
    ax.plot(x_labels, number_counts[num], label=f"{num}番")

ax.set_title("数字別 累積出現回数の推移")
ax.set_xlabel("抽選日")
ax.set_ylabel("累積出現回数")
ax.tick_params(axis='x', labelrotation=45)
ax.legend()
st.pyplot(fig)

# --- 🔗 よく一緒に出る数字（ペア／トリプル） ---
st.markdown("---")
st.subheader("🔗 よく一緒に出る数字の組み合わせ（ペア／トリプル）")

all_main_numbers = df["本数字"].apply(lambda x: list(map(int, x.split())))
pair_counter = Counter()
triple_counter = Counter()

for numbers in all_main_numbers:
    pair_counter.update(combinations(sorted(numbers), 2))
    triple_counter.update(combinations(sorted(numbers), 3))

top_n = st.slider("表示する件数（上位）", 5, 30, 10)

st.write(f"🎯 **よく出るペア（上位 {top_n} 件）**")
for pair, count in pair_counter.most_common(top_n):
    st.write(f"{pair[0]}, {pair[1]}：{count} 回")

st.write("---")
st.write(f"🎯 **よく出るトリプル（上位 {top_n} 件）**")
for triple, count in triple_counter.most_common(top_n):
    st.write(f"{triple[0]}, {triple[1]}, {triple[2]}：{count} 回")

# --- 📈 出現スパン（間隔）分析 ---
st.markdown("---")
st.subheader("📈 数字の出現スパン（間隔）分析")

span_dict = {n: [] for n in range(1, 44)}
number_series = df["本数字"].apply(lambda x: list(map(int, x.split()))).tolist()[::-1]

last_seen = {}
span_result = []

for idx, numbers in enumerate(number_series):
    for num in numbers:
        if num in last_seen:
            span = idx - last_seen[num]
            span_dict[num].append(span)
            span_result.append(span)
        last_seen[num] = idx

fig, ax = plt.subplots()
ax.hist(span_result, bins=range(1, max(span_result)+2), edgecolor='black')
ax.set_title("出現スパン（数字が再び出るまでの回数）")
ax.set_xlabel("スパン（回）")
ax.set_ylabel("頻度")
ax.grid(True)
st.pyplot(fig)

# --- 📄 PDFレポートのダウンロードリンク（サンプル） ---
pdf_file_path = "2025-07_report.pdf"
if os.path.exists(pdf_file_path):
    with open(pdf_file_path, "rb") as f:
        pdf_data = f.read()
        b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_file_path}">📄 PDFレポートをダウンロード</a>'
        st.markdown(href, unsafe_allow_html=True)

import random

st.markdown("---")
st.subheader("🎲 おすすめ数字自動生成")

# --- 各ロジック定義 ---
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

# --- ロジック辞書（セレクトボックス表示用） ---
strategies = {
    "頻出数字から選ぶ": generate_from_frequent,
    "未出数字を優先": generate_from_unused,
    "奇数・偶数バランス重視": generate_balanced_odd_even,
    "連続数字を含める": generate_with_consecutive,
    "よく出るペアを含める": generate_with_common_pair,
    "ランダム（自動選択）": None,  # ランダムで選ぶ
}

# --- セレクトボックスでロジック選択 ---
selected_strategy_name = st.selectbox("🧠 ロジックを選択してください", list(strategies.keys()))

# --- ボタンで毎回再生成 ---
if st.button("🔁 数字を再生成"):
    if selected_strategy_name == "ランダム（自動選択）":
        strategy_func = random.choice(list(strategies.values())[:-1])  # 最後のNone以外から選ぶ
    else:
        strategy_func = strategies[selected_strategy_name]
    suggested_numbers = strategy_func()
    st.markdown(f"#### 💡 おすすめの数字（{selected_strategy_name}）")
    st.success("、".join(map(str, suggested_numbers)))

