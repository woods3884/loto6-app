import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib
import base64
import os
import random
import chardet
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# --- フォント設定 ---
font_path = "ipaexg.ttf"
font_prop = fm.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['font.family'] = font_prop.get_name()

# --- フォルダ作成 ---
os.makedirs("data", exist_ok=True)

# --- chardetでCSV読み込み ---
def read_csv_with_chardet(path):
    with open(path, "rb") as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
    return pd.read_csv(path, encoding=encoding)

# --- おすすめ数字自動生成ロジック ---
def generate_numbers(df, logic="frequency"):
    numbers_pool = range(1, 44)
    if logic == "frequency":
        all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
        freq = all_numbers.value_counts().sort_values(ascending=False)
        top_numbers = list(freq.head(20).index)
        return [sorted(random.sample(top_numbers, 6)) for _ in range(5)]
    else:
        return [sorted(random.sample(numbers_pool, 6)) for _ in range(5)]

# --- PDFレポート生成 ---
def generate_pdf_report(df, month):
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    file_path = f"{month}_report.pdf"
    if os.path.exists(file_path):
        return
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

# --- Streamlit UI ---
st.title("🎯 ロト6 出現数字分析＆おすすめ生成")

# --- 月選択とCSV読込 ---
csv_folder = "data"
csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]
months = sorted([f.replace(".csv", "") for f in csv_files], reverse=True)
selected_month = st.selectbox("📅 表示したい月を選んでください", months)
csv_path = os.path.join(csv_folder, f"{selected_month}.csv")

if os.path.exists(csv_path):
    df = read_csv_with_chardet(csv_path)
    generate_pdf_report(df, selected_month)

    st.subheader("📄 PDFレポート")
    pdf_filename = f"{selected_month}_report.pdf"
    if os.path.exists(pdf_filename):
        with open(pdf_filename, "rb") as f:
            b64_pdf = base64.b64encode(f.read()).decode("utf-8")
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">📥 ダウンロード：{pdf_filename}</a>'
            st.markdown(href, unsafe_allow_html=True)

    # --- おすすめ数字生成 ---
    st.subheader("🎲 おすすめ数字自動生成")
    logic = st.selectbox("ロジックを選択", ["frequency", "random"])
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = generate_numbers(df, logic=logic)

    if st.button("🔁 再生成"):
        st.session_state.recommendations = generate_numbers(df, logic=logic)

    for i, nums in enumerate(st.session_state.recommendations):
        st.write(f"{i+1}口目: {nums}")
else:
    st.warning("CSVファイルが見つかりませんでした。")
