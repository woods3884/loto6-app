import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib
import base64
import os
import random
from datetime import datetime
from collections import Counter
from itertools import combinations

# --- フォント設定 ---
font_path = "ipaexg.ttf"
font_prop = fm.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['font.family'] = font_prop.get_name()

# --- PDF保存用フォルダ作成 ---
os.makedirs("data", exist_ok=True)

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

    # 列名変換（日本語→英語）
    rename_dict = {
        "数字1": "num1", "数字2": "num2", "数字3": "num3",
        "数字4": "num4", "数字5": "num5", "数字6": "num6"
    }
    df = df.rename(columns=rename_dict)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    c.setFont('HeiseiKakuGo-W5', 14)
    c.drawString(50, height - 50, f"ロト6 数字出現レポート（{month}）")

    all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts().sort_values(ascending=False)
    c.setFont('HeiseiKakuGo-W5', 12)
    c.drawString(50, height - 90, "頻出数字トップ10：")
    for i, (num, count) in enumerate(freq.head(10).items()):
        c.drawString(60, height - 110 - i * 20, f"{i+1}位: {num}（{count}回）")

    c.save()

# --- 🎯 おすすめ数字生成ロジック ---
def generate_numbers(df_all, logic="頻出上位30個"):
    # 列名が「数字1〜6」の場合に「num1〜num6」へリネーム
    rename_dict = {
        "数字1": "num1", "数字2": "num2", "数字3": "num3",
        "数字4": "num4", "数字5": "num5", "数字6": "num6",
    }
    df_all = df_all.rename(columns=rename_dict)

    all_numbers = pd.Series(df_all[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts().sort_values(ascending=False)

    numbers = []
    if logic == "頻出上位30個":
        pool = list(freq.head(30).index)
    elif logic == "ランダム全数字":
        pool = list(range(1, 44))
    elif logic == "最近未出数字から":
        pool = list(freq.tail(30).index)
    else:
        pool = list(range(1, 44))

    for _ in range(5):
        numbers.append(sorted(random.sample(pool, 6)))

    return numbers

# --- Streamlit UI ---
st.title("🎯 ロト6 おすすめ数字自動生成ツール")

# 月別CSV一覧を収集
csv_folder = "data"
os.makedirs(csv_folder, exist_ok=True)
csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]
months = sorted([f.replace(".csv", "") for f in csv_files], reverse=True)

selected_month = st.selectbox("📅 使用するデータ（月）を選んでください", ["全期間"] + months)
logic = st.selectbox("🧠 数字生成ロジックを選択", ["頻出上位30個", "ランダム全数字", "最近未出数字から"])

if st.button("🔁 数字を再生成") or "recommendations" not in st.session_state:
    if selected_month == "全期間":
        df_list = []
        for month_file in csv_files:
            path = os.path.join(csv_folder, month_file)
            df = pd.read_csv(path)
            df_list.append(df)
        df_all = pd.concat(df_list, ignore_index=True)
    else:
        csv_path = os.path.join(csv_folder, f"{selected_month}.csv")
        df_all = pd.read_csv(csv_path)

    st.session_state.recommendations = generate_numbers(df_all, logic=logic)

# --- 表示 ---
st.markdown("### ✅ 今回のおすすめ数字（5口分）")
for i, nums in enumerate(st.session_state.recommendations, 1):
    st.write(f"**{i}口目**: {', '.join(map(str, nums))}")

# --- 📄 PDFレポートダウンロード ---
st.markdown("### 📄 PDFレポートダウンロード")
if selected_month != "全期間":
    df = pd.read_csv(os.path.join(csv_folder, f"{selected_month}.csv"))
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
