import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import random

# 日本語フォントの登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

# データフォルダの指定
data_folder = "data"

# ページタイトル
st.title("📄 PDFレポートダウンロード")

# 月の選択肢を取得
def get_available_months():
    if not os.path.exists(data_folder):
        return []
    files = os.listdir(data_folder)
    months = [f.replace(".csv", "") for f in files if f.endswith(".csv")]
    months.sort(reverse=True)
    return months

# PDFレポート生成関数
def generate_pdf_report(df, selected_month):
    file_name = f"report_{selected_month}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    c.setFont("HeiseiKakuGo-W5", 12)

    # 見出し
    c.drawString(100, 800, f"ロト6 {selected_month} 出現数字レポート")

    # 列名リネーム
    rename_dict = {
        "数字１": "num1",
        "数字２": "num2",
        "数字３": "num3",
        "数字４": "num4",
        "数字５": "num5",
        "数字６": "num6",
    }
    df = df.rename(columns=rename_dict)

    # 頻出数字の集計
    all_numbers = pd.Series(df[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts().sort_index()

    y = 760
    for num, count in freq.items():
        c.drawString(100, y, f"{int(num):02d}：{count}回")
        y -= 20

    c.save()
    return file_name

# 月選択
months = get_available_months()
selected_month = st.selectbox("📅 表示したい月を選んでください", months)

if selected_month:
    csv_path = os.path.join(data_folder, f"{selected_month}.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding="cp932")
        pdf_file = generate_pdf_report(df, selected_month)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label=f"📥 {selected_month} report.pdf をダウンロード",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )
    else:
        st.warning(f"⚠️ {csv_path} は存在しません。")
else:
    st.info("🔽 月を選択するとPDFが生成されます")

# --------------------------------------------
# 🔁 おすすめ数字自動生成
# --------------------------------------------
st.markdown("""
---
## 🎯 過去すべての出現傾向からおすすめ数字を自動生成
""")

# 過去すべてのCSVを結合
def load_all_data():
    all_dfs = []
    for file in os.listdir(data_folder):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(data_folder, file), encoding="cp932")
            all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

# ロジック選択肢
def generate_numbers(df_all, logic="頻出順"):
    all_numbers = pd.Series(df_all[[f"num{i}" for i in range(1, 7)]].values.ravel())
    freq = all_numbers.value_counts().sort_values(ascending=False)
    top_numbers = list(freq.index)
    if logic == "頻出順":
        return [sorted(random.sample(top_numbers[:20], 6)) for _ in range(5)]
    elif logic == "ランダム":
        return [sorted(random.sample(range(1, 44), 6)) for _ in range(5)]
    else:
        return [sorted(random.sample(top_numbers[:30], 6)) for _ in range(5)]

# ロジック選択
logic = st.selectbox("🔢 ロジックを選んでください", ["頻出順", "ランダム"])

# 数字生成とPDFボタン
if 'recommendations' not in st.session_state:
    df_all = load_all_data()
    rename_dict = {
        "数字１": "num1",
        "数字２": "num2",
        "数字３": "num3",
        "数字４": "num4",
        "数字５": "num5",
        "数字６": "num6",
    }
    df_all = df_all.rename(columns=rename_dict)
    st.session_state.recommendations = generate_numbers(df_all, logic=logic)

if st.button("🔁 数字を再生成する"):
    df_all = load_all_data()
    rename_dict = {
        "数字１": "num1",
        "数字２": "num2",
        "数字３": "num3",
        "数字４": "num4",
        "数字５": "num5",
        "数字６": "num6",
    }
    df_all = df_all.rename(columns=rename_dict)
    st.session_state.recommendations = generate_numbers(df_all, logic=logic)

if 'recommendations' in st.session_state:
    st.subheader("🎉 おすすめ数字（5口分）")
    for idx, row in enumerate(st.session_state.recommendations, 1):
        st.write(f"第{idx}口：{' '.join(f'{n:02d}' for n in row)}")
