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
data_scope = st.radio("🎯 データの範囲を選択してください", ["選択した月のみ", "すべての月"])

if data_scope == "すべての月":
    df_list = []
    for m in months:
        path = os.path.join(csv_folder, f"{m}.csv")
        if os.path.exists(path):
            df_list.append(pd.read_csv(path))
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        current_month = selected_month  # PDFは選択月に基づく
    else:
        st.error("有効なCSVファイルがありません。")
        df = pd.DataFrame()
        current_month = selected_month
else:
    csv_path = os.path.join(csv_folder, f"{selected_month}.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        current_month = selected_month
    else:
        st.warning(f"⚠️ {csv_path} が存在しません。")
        df = pd.DataFrame()
        current_month = selected_month

if not df.empty:
    generate_pdf_report(df, current_month)
    pdf_filename = f"{current_month}_report.pdf"
    if os.path.exists(pdf_filename):
        with open(pdf_filename, "rb") as f:
            pdf_bytes = f.read()
            b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">📥 {pdf_filename} をダウンロード</a>'
            st.markdown(pdf_link, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ {pdf_filename} は見つかりません。")
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
data_scope = st.radio("🎯 データの範囲を選択してください", ["選択した月のみ", "すべての月"])

if data_scope == "すべての月":
    df_list = []
    for m in months:
        path = os.path.join(csv_folder, f"{m}.csv")
        if os.path.exists(path):
            df_list.append(pd.read_csv(path))
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        current_month = selected_month  # PDFは選択月に基づく
    else:
        st.error("有効なCSVファイルがありません。")
        df = pd.DataFrame()
        current_month = selected_month
else:
    csv_path = os.path.join(csv_folder, f"{selected_month}.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        current_month = selected_month
    else:
        st.warning(f"⚠️ {csv_path} が存在しません。")
        df = pd.DataFrame()
        current_month = selected_month

if not df.empty:
    generate_pdf_report(df, current_month)
    pdf_filename = f"{current_month}_report.pdf"
    if os.path.exists(pdf_filename):
        with open(pdf_filename, "rb") as f:
            pdf_bytes = f.read()
            b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">📥 {pdf_filename} をダウンロード</a>'
            st.markdown(pdf_link, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ {pdf_filename} は見つかりません。")
