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
import random

# --- フォント設定 ---
font_path = "ipaexg.ttf"
font_prop = fm.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['font.family'] = font_prop.get_name()

# --- 📄 PDF生成関数 ---
def generate_pdf_report(df, month):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    file_path = f"{month}_report.pdf"
    if os.path.exists(file_path):
        return  # すでに存在すれば生成しない

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    c.setFont('HeiseiKakuGo-W5', 14)
    c.drawString(50, height - 50, f"ロト6 数字出現レポート（{month}）")

    # 頻出数字トップ10
    all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts().sort_values(ascending=False)
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(50, height - 90, "頻出数字トップ10：")
    for i, (num, count) in enumerate(freq.head(10).items()):
        c.drawString(60, height - 110 - i * 20, f"{i+1}位: {num}（{count}回）")

    c.save()

# --- 📄 PDFレポートダウンロードセクション ---
st.markdown("### 📄 PDFレポートダウンロード")

# 月別CSV一覧を収集
csv_folder = "data"
csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]
months = sorted([f.replace(".csv", "") for f in csv_files], reverse=True)

selected_month = st.selectbox("📅 表示したい月を選んでください", months)
csv_path = os.path.join(csv_folder, f"{selected_month}.csv")

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    generate_pdf_report(df, selected_month)
    pdf_filename = f"{selected_month}_report.pdf"
    if os.path.exists(pdf_filename):
        with open(pdf_filename, "rb") as f:
            pdf_bytes = f.read()
            b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">📥 {pdf_filename} をダウンロード</a>'
            st.markdown(pdf_link, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ {pdf_filename} は見つかりません。")
else:
    st.warning(f"⚠️ {csv_path} が存在しません。")

# --- 🎲 おすすめ数字自動生成セクション ---
st.markdown("---")
st.subheader("🎲 おすすめ数字自動生成")

# --- 各ロジック定義 ---
def generate_from_frequent(df):
    all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts().sort_values(ascending=False)
    return sorted(random.sample(freq.head(10).index.tolist(), 6))

def generate_from_unused(df):
    all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
    used = set(all_numbers)
    unused = sorted(set(range(1, 44)) - used)
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

def generate_with_common_pair(df):
    all_numbers = df[[f"num{i}" for i in range(1, 7)]].values.tolist()
    pair_counter = Counter()
    for row in all_numbers:
        pair_counter.update(combinations(sorted(row), 2))
    pair = pair_counter.most_common(1)[0][0]
    others = random.sample([n for n in range(1, 44) if n not in pair], 4)
    return sorted(list(pair) + others)

# --- ロジック選択UI ---
strategy_options = {
    "頻出数字から選ぶ": lambda df: generate_from_frequent(df),
    "未出数字から選ぶ": lambda df: generate_from_unused(df),
    "奇数偶数バランス重視": lambda df: generate_balanced_odd_even(),
    "連続数字を含める": lambda df: generate_with_consecutive(),
    "よく出るペアを含める": lambda df: generate_with_common_pair(df),
}

selected_name = st.selectbox("🧠 ロジックを選択してください", list(strategy_options.keys()))

# --- 数字生成処理 ---
if st.button("🔁 数字を再生成"):
    st.markdown("### 💡 おすすめの数字（5口）")
    for i in range(5):
        numbers = strategy_options[selected_name](df)
        st.success(f"口 {i+1}: " + "、".join(map(str, numbers)))
