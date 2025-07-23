# loto6_app.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib
import matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'Yu Gothic', 'Meiryo', 'MS Gothic']
import base64
import os
from datetime import datetime
import streamlit as st

# --- 📅 月選択（過去12ヶ月分） ---
st.markdown("### 📄 PDFレポートダウンロード")

today = datetime.today()
months = [today.replace(day=1).strftime("%Y-%m")]

for i in range(1, 12):
    prev = today.replace(day=1) - pd.DateOffset(months=i)
    months.append(prev.strftime("%Y-%m"))
selected_month = st.selectbox("📅 表示したい月を選んでください", sorted(months, reverse=True))

# --- 📄 PDFファイル名を生成 ---
pdf_filename = f"{selected_month}_report.pdf"

# --- 🔽 PDFダウンロードリンク表示 ---
if os.path.exists(pdf_filename):
    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()
        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">📥 {pdf_filename} をダウンロード</a>'
        st.markdown(pdf_link, unsafe_allow_html=True)
else:
    st.warning(f"⚠️ {pdf_filename} は見つかりません。")
# 日本語フォント設定
font_path = fm.findfont("Meiryo")
plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()

# データ読み込み
df = pd.read_csv("loto6_past_100.csv")

# 本数字を分解
number_cols = [f"num{i}" for i in range(1, 7)]
df[number_cols] = df["本数字"].str.split(" ", expand=True).astype(int)

# 頻出数字ランキング
all_numbers = pd.Series(df[number_cols].values.ravel())
freq = all_numbers.value_counts().sort_values(ascending=False)

# 未出数字
all_possible = set(range(1, 44))
existing = set(freq.index)
unused = sorted(all_possible - existing)

# 奇数偶数比
odd = all_numbers[all_numbers % 2 == 1].count()
even = all_numbers[all_numbers % 2 == 0].count()

# 連続数字パターン検出
def count_consecutive(row):
    nums = sorted(row)
    count = 0
    for i in range(len(nums) - 1):
        if nums[i+1] - nums[i] == 1:
            count += 1
    return count

df["連続数"] = df[number_cols].apply(count_consecutive, axis=1)
consec_counts = df["連続数"].value_counts().sort_index()

# ポジション別傾向
def get_position_counts():
    position_df = pd.DataFrame()
    for pos in number_cols:
        counts = df[pos].value_counts()
        position_df[pos] = counts
    position_df = position_df.fillna(0).astype(int).sort_index()
    return position_df

position_df = get_position_counts()

# Streamlit 表示
st.title("ロト6出現数字分析アプリ")

st.subheader("頻出数字ランキング")
for num, count in freq.head(10).items():
    st.write(f"{num}: {count}回")

st.subheader("未出数字")
st.write(unused)

st.subheader("奇数・偶数比")
st.write(f"奇数: {odd} 個")
st.write(f"偶数: {even} 個")

st.subheader("連続数字の出現パターン")
fig1, ax1 = plt.subplots()
ax1.bar(consec_counts.index, consec_counts.values)
ax1.set_xlabel("連続数字の個数")
ax1.set_ylabel("出現回数")
ax1.set_title("連続数字の出現回数")
st.pyplot(fig1)

st.subheader("ポジション別出現傾向（棒グラフ）")
fig2, ax2 = plt.subplots(figsize=(12, 6))
position_df.plot(kind="bar", ax=ax2)
ax2.set_xlabel("数字")
ax2.set_ylabel("出現回数")
ax2.set_title("各ポジションにおける数字の出現回数")
st.pyplot(fig2)

st.subheader("ポジション×数字の出現傾向（ヒートマップ）")
fig3, ax3 = plt.subplots(figsize=(14, 8))
sns.heatmap(position_df.T, cmap="YlOrRd", linewidths=0.5, annot=True, fmt="d", cbar_kws={'label': '出現回数'}, ax=ax3)
ax3.set_xlabel("数字")
ax3.set_ylabel("ポジション")
ax3.set_title("ポジションごとの数字出現ヒートマップ")
st.pyplot(fig3)
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# フォント設定（日本語対応）
plt.rcParams['font.family'] = 'Meiryo'

st.markdown("---")
st.subheader("📈 数字ごとの出現回数の推移（累計）")

# 数字ごとの累積出現回数を作成
number_counts = {i: [] for i in range(1, 44)}
cumulative_counts = {i: 0 for i in range(1, 44)}
x_labels = df["抽選日"].tolist()

for index, row in df.iterrows():
    numbers = list(map(int, row["本数字"].split()))
    for i in range(1, 44):
        if i in numbers:
            cumulative_counts[i] += 1
        number_counts[i].append(cumulative_counts[i])

# 折れ線グラフ表示
selected_numbers = st.multiselect(
    "表示する数字を選んでください（複数選択可）",
    options=list(range(1, 44)),
    default=[6, 19, 38]
)

fig, ax = plt.subplots(figsize=(10, 5))
for num in selected_numbers:
    ax.plot(x_labels, number_counts[num], label=f"{num}番")

ax.set_title("数字別 累積出現回数の推移")
ax.set_xlabel("抽選日")
ax.set_ylabel("累積出現回数")
ax.tick_params(axis='x', labelrotation=45)
ax.legend()
st.pyplot(fig)
from collections import Counter
from itertools import combinations

st.markdown("---")
st.subheader("🔗 よく一緒に出る数字の組み合わせ（ペア／トリプル）")

# 本数字リストを抽出
all_main_numbers = df["本数字"].apply(lambda x: list(map(int, x.split())))

# ペアとトリプルをカウント
pair_counter = Counter()
triple_counter = Counter()

for numbers in all_main_numbers:
    pair_counter.update(combinations(sorted(numbers), 2))
    triple_counter.update(combinations(sorted(numbers), 3))

# 上位ペア＆トリプルを表示
top_n = st.slider("表示する件数（上位）", 5, 30, 10)

st.write(f"🎯 **よく出るペア（上位 {top_n} 件）**")
for pair, count in pair_counter.most_common(top_n):
    st.write(f"{pair[0]}, {pair[1]}：{count} 回")

st.write("---")
st.write(f"🎯 **よく出るトリプル（上位 {top_n} 件）**")
for triple, count in triple_counter.most_common(top_n):
    st.write(f"{triple[0]}, {triple[1]}, {triple[2]}：{count} 回")
st.markdown("---")
st.subheader("📈 数字の出現スパン（間隔）分析")

# 数字ごとに直近の出現回数インデックスを記録
span_dict = {n: [] for n in range(1, 44)}

# 各回の数字（直近が上）
number_series = df["本数字"].apply(lambda x: list(map(int, x.split()))).tolist()[::-1]

# 各数字のスパンを記録
last_seen = {}
span_result = []

for idx, numbers in enumerate(number_series):
    for num in numbers:
        if num in last_seen:
            span = idx - last_seen[num]
            span_dict[num].append(span)
            span_result.append(span)
        last_seen[num] = idx

# ヒストグラムでスパン分布を表示
fig, ax = plt.subplots()
ax.hist(span_result, bins=range(1, max(span_result) + 2), edgecolor='black')
ax.set_title("出現スパン（数字が再び出るまでの回数）")
ax.set_xlabel("スパン（回）")
ax.set_ylabel("頻度")
ax.grid(True)

# フォント調整（matplotlib）
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

st.pyplot(fig)
import base64

# 画面内の適切な場所に以下を挿入（例：サイドバーや最後の分析結果の下）
pdf_file_path = "2025-07_report.pdf"
with open(pdf_file_path, "rb") as f:
    pdf_data = f.read()
    b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_file_path}">📄 PDFレポートをダウンロード</a>'
    st.markdown(href, unsafe_allow_html=True)
