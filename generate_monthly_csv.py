import pandas as pd
import os

# 元CSVを読み込み（SHIFT-JIS / cp932 対応）
df = pd.read_csv("LOTO6_ALL.csv", encoding="cp932")

# 「抽選日」列をdatetime型に変換（列名は必ず一致している必要があります）
df["抽選日"] = pd.to_datetime(df["抽選日"])

# 出力先フォルダを作成
output_folder = "data"
os.makedirs(output_folder, exist_ok=True)

# 年月単位でグループ化して保存（例: 2025-07.csv）
for (year, month), group in df.groupby([df["抽選日"].dt.year, df["抽選日"].dt.month]):
    filename = f"{year}-{month:02d}.csv"
    filepath = os.path.join(output_folder, filename)
    group.to_csv(filepath, index=False)

print("✅ 月別CSVの保存が完了しました。")
