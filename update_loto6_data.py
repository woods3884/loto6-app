import pandas as pd

INPUT_FILE = "LOTO6_ALL.csv"
OUTPUT_FILE = "loto6_past_100.csv"

try:
    # 読み込み（Shift_JIS or CP932で試行）
    df = pd.read_csv(INPUT_FILE, encoding="cp932")

    # 必要な列だけ抽出
    df_selected = df[["抽選日", "数字１", "数字２", "数字３", "数字４", "数字５", "数字６", "数字B"]].copy()

    # 日付型に変換
    df_selected["抽選日"] = pd.to_datetime(df_selected["抽選日"], errors="coerce")

    # 本数字・ボーナス数字列を作成
    df_selected["本数字"] = df_selected[["数字１", "数字２", "数字３", "数字４", "数字５", "数字６"]].astype(int).astype(str).agg(" ".join, axis=1)
    df_selected["ボーナス数字"] = df_selected["数字B"].astype(int).astype(str)

    # 最新の100件のみ抽出
    df_latest = df_selected.sort_values("抽選日", ascending=False).head(100).reset_index(drop=True)

    # 必要な列だけ出力
    df_output = df_latest[["抽選日", "本数字", "ボーナス数字"]]

    # CSV出力
    df_output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"✅ データを更新しました：{OUTPUT_FILE}")

except Exception as e:
    print("エラーが発生しました：", e)
