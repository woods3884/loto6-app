import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# データ読み込み（過去すべて）
DATA_DIR = "data"
all_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
all_files.sort()
df_all = pd.concat([pd.read_csv(os.path.join(DATA_DIR, f), encoding="cp932") for f in all_files])

# --- 列名を統一 ---
rename_dict = {
    "数字１": "num1",
    "数字２": "num2",
    "数字３": "num3",
    "数字４": "num4",
    "数字５": "num5",
    "数字６": "num6",
}
df_all = df_all.rename(columns=rename_dict)

# --- ページ設定 ---
st.set_page_config(page_title="ロト6分析ツール", layout="centered")

st.title("📊 ロト6 出現数字分析ツール")

# --- PDF レポート ダウンロード ---
st.header("📄 PDFレポートダウンロード")
month_list = sorted([f.replace(".csv", "") for f in all_files])
selected_month = st.selectbox("📅 表示したい月を選んでください", month_list)

pdf_path = f"reports/{selected_month}_report.pdf"
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as f:
        st.download_button(f"{selected_month} のレポートをダウンロード", f, file_name=os.path.basename(pdf_path))
else:
    st.warning(f"{pdf_path} は存在しません。")

# --- 過去すべてからおすすめ数字を生成 ---
st.header("🎯 過去すべての出現傾向からおすすめ数字を自動生成")

def generate_numbers(df, logic="random"):
    all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts().sort_values(ascending=False)

    recommendations = []
    for _ in range(5):  # 5口生成
        if logic == "random":
            numbers = sorted(random.sample(range(1, 44), 6))
        elif logic == "high_freq":
            numbers = sorted(freq.head(6).index.tolist())
        else:
            numbers = sorted(random.sample(range(1, 44), 6))
        recommendations.append(numbers)
    return recommendations

logic = st.selectbox("ロジックを選択", ["random", "high_freq"])
if st.button("🔁 おすすめ数字を再生成"):
    st.session_state.recommendations = generate_numbers(df_all, logic=logic)

if "recommendations" not in st.session_state:
    st.session_state.recommendations = generate_numbers(df_all)

for i, nums in enumerate(st.session_state.recommendations, 1):
    st.write(f"**口{i}：** {' '.join(map(str, nums))}")

# --- PDF 保存 ---
def save_recommendation_pdf(numbers_list):
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/recommendation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

    c.setFont("HeiseiKakuGo-W5", 16)
    c.drawString(100, 800, "ロト6おすすめ数字（過去全データから）")

    for i, nums in enumerate(numbers_list, 1):
        c.drawString(100, 780 - i * 30, f"{i}口目： {' '.join(map(str, nums))}")

    c.save()
    return filename

if st.button("📥 PDF保存"):
    pdf_file = save_recommendation_pdf(st.session_state.recommendations)
    with open(pdf_file, "rb") as f:
        st.download_button("おすすめ数字PDFをダウンロード", f, file_name=os.path.basename(pdf_file))
