import os
import pandas as pd

# 入力CSVファイルと保存フォルダ
INPUT_FILE = "loto6_past_100.csv"
OUTPUT_DIR = "monthly_data"

# 保存先フォルダを作成（存在しない場合）
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    # CSV読み込み
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    # 日付を自動判別して変換（ハイフンでもスラッシュでもOK）
    df["抽選日"] = pd.to_datetime(df["抽選日"], errors="coerce")

    # 年・月ごとに分割して保存
    for (year, month), group in df.groupby([df["抽選日"].dt.year, df["抽選日"].dt.month]):
        filename = f"{year}-{month:02d}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        group.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"✅ 保存しました：{filepath}")

except Exception as e:
    print("エラーが発生しました：", e)
