import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(page_title="ロト6分析ツール", layout="centered")
st.title("🎯 ロト6 過去100回 当選番号分析アプリ")

# CSV読み込み
try:
    df = pd.read_csv("loto6_past_100.csv")

    # 🔍 デバッグ表示：読み込んだCSVの先頭5件
    st.subheader("🔍 読み込んだCSVの先頭5件")
    st.write(df.head())

    # 全出現数字リストを作成
    all_numbers = []
    for nums in df["本数字"]:
        numbers = str(nums).replace("　", " ").replace(",", " ").split()
        all_numbers.extend(numbers)

    # 頻出数字ランキング
    counter = Counter(all_numbers)
    ranking = counter.most_common()

    st.subheader("📈 頻出数字ランキング（上位10）")
    st.table(pd.DataFrame(ranking[:10], columns=["数字", "出現回数"]))

    # 未出数字の表示（1〜43）
    all_set = set(str(i) for i in range(1, 44))
    appeared_set = set(all_numbers)
    missing = sorted(all_set - appeared_set, key=lambda x: int(x))

    st.subheader("❌ 未出数字一覧（過去100回）")
    st.write(", ".join(missing))

    # 奇数／偶数バランス
    odd_count = sum(1 for n in all_numbers if int(n) % 2 == 1)
    even_count = len(all_numbers) - odd_count

    st.subheader("⚖️ 奇数／偶数の出現バランス")
    fig, ax = plt.subplots()
    ax.bar(["奇数", "偶数"], [odd_count, even_count])
    ax.set_ylabel("出現数")
    st.pyplot(fig)

except Exception as e:
    st.error(f"エラーが発生しました：{e}")
