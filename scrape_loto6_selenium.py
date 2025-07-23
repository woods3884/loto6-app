import pandas as pd

# 非公式サイトから取得した元データのファイル名
INPUT_FILE = "LOTO6_ALL.csv"

# Streamlitアプリが読み込むファイル名
OUTPUT_FILE = "loto6_past_100.csv"

# CSVを読み込み
try:
    df = pd.read_csv(INPUT_FILE, encoding="utf-8")

    # 必要な列だけを選択（列名は実データに応じて変更してください）
    # 例：回, 抽選日, 数字1～6, ボーナス数字
    df_selected = df.iloc[:, [1, 2, 3, 4, 5, 6, 7, 8]]  # 抽選日と数字列を抽出
    df_selected.columns = ["抽せん日", "数字1", "数字2", "数字3", "数字4", "数字5", "数字6", "ボーナス数字"]

    # 本数字を結合して1列にする
    df_selected["本数字"] = df_selected[["数字1", "数字2", "数字3", "数字4", "数字5", "数字6"]].astype(str).agg(" ".join, axis=1)

    # 必要な列だけに整理
    df_output = df_selected[["抽せん日", "本数字", "ボーナス数字"]]

    # 最新100件に絞る（上位100件）
    df_output = df_output.head(100)

    # 出力
    df_output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"{OUTPUT_FILE} を出力しました（最新100件）")
    print(df_output.head())

except Exception as e:
    print("エラーが発生しました：", e)
