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
import chardet

# --- フォント設定 ---
font_path = "ipaexg.ttf"
font_prop = fm.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['font.family'] = font_prop.get_name()

# --- データフォルダ作成 ---
csv_folder = "data"
os.makedirs(csv_folder, exist_ok=True)

# --- 📄 CSV読み込み関数（自動エンコーディング判定） ---
def read_csv_with_chardet(path):
    with open(path, "rb") as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
    return pd.read_csv(path, encoding=encoding)

# --- 🎲 数字生成ロジック ---
def generate_numbers(df, logic="freq"):
    if df.empty:
        return []

    df = df.rename(columns={"数字１": "num1", "数字２": "num2", "数字３": "num3",
                            "数字４": "num4", "数字５": "num5", "数字６": "num6"})

    all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts()

    if logic == "freq":
        top_numbers = freq.head(20).index.tolist()
        return [sorted(random.sample(top_numbers, 6)) for _ in range(5)]
    elif logic == "least":
        low_numbers = freq.tail(20).index.tolist()
        return [sorted(random.sample(low_numbers, 6)) for _ in range(5)]
    elif logic == "random":
        return [sorted(random.sample(range(1, 44), 6)) for _ in range(5)]
    else:
        return []

# --- 📄 PDF生成関数 ---
def generate_pdf_report(recommendations, filename):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont('HeiseiKakuGo-W5', 14)
    c.drawString(50, height - 50, "ロト6 おすすめ数字 自動生成レポート")

    c.setFont('HeiseiKakuGo-W5', 12)
    for i, line in enumerate(recommendations):
        c.drawString(60, height - 100 - i * 20, f"{i+1}口目: {line}")

    c.save()

# --- Streamlit アプリ表示 ---
st.title("🎯 ロト6 おすすめ数字自動生成ツール")

# 月別CSV一覧を取得
csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]
months = sorted([f.replace(".csv", "") for f in csv_files], reverse=True)
selected_month = st.selectbox("📅 使用する月データを選択", ["全データを使用"] + months)

# ロジック選択
logic = st.selectbox("🧠 数字生成ロジックを選択", ["freq", "least", "random"])

# データ読み込み
if selected_month == "全データを使用":
    df_all = pd.concat([
        read_csv_with_chardet(os.path.join(csv_folder, f)) for f in csv_files
    ], ignore_index=True)
else:
    csv_path = os.path.join(csv_folder, f"{selected_month}.csv")
    df_all = read_csv_with_chardet(csv_path)

# 数字生成ボタン
if "recommendations" not in st.session_state:
    st.session_state.recommendations = generate_numbers(df_all, logic=logic)

if st.button("🔁 おすすめ数字を再生成"):
    st.session_state.recommendations = generate_numbers(df_all, logic=logic)

# 結果表示
st.markdown("### 🎉 おすすめ数字（5口）")
for i, nums in enumerate(st.session_state.recommendations, 1):
    st.write(f"{i}口目: {nums}")

# PDFダウンロード
pdf_filename = "loto6_recommendation.pdf"
generate_pdf_report(st.session_state.recommendations, pdf_filename)
with open(pdf_filename, "rb") as f:
    pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{pdf_filename}">📄 PDFでダウンロード</a>'
    st.markdown(href, unsafe_allow_html=True)
