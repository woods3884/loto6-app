import pandas as pd

df = pd.read_csv("loto6_past_100.csv", encoding="utf-8-sig")
print("✅ 列名一覧：")
for col in df.columns:
    print(f"- {col}（文字コード: {[hex(ord(c)) for c in col]}）")
