import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# フォント登録（日本語対応）
pdfmetrics.registerFont(TTFont("IPAexG", "ipaexg.ttf"))

# ファイル名を指定
DATA_FILE = "LOTO6_ALL.csv"

try:
    # ✅ ここを修正：cp932 で読み込む
    df = pd.read_csv(DATA_FILE, encoding="cp932")
    df.columns = [col.strip() for col in df.columns]

    # 列名変換
    rename_dict = {
        "抽選日": "抽せん日",
        "数字１": "数字1",
        "数字２": "数字2",
        "数字３": "数字3",
        "数字４": "数字4",
        "数字５": "数字5",
        "数字６": "数字6",
        "数字B": "ボーナス1",
    }
    df = df.rename(columns={k: v for k, v in rename_dict.items() if k in df.columns})

    # 必須列チェック
    required = ["抽せん日", "数字1", "数字2", "数字3", "数字4", "数字5", "数字6"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"❌ 列が不足しています: {col}")

    # 最新月の抽出
    df["抽せん日"] = pd.to_datetime(df["抽せん日"], errors="coerce")
    df = df.dropna(subset=["抽せん日"])
    latest_month = df["抽せん日"].max().strftime("%Y-%m")
    df_latest = df[df["抽せん日"].dt.strftime("%Y-%m") == latest_month]

    # PDF出力
    file_name = f"{latest_month}_report.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    c.setFont("IPAexG", 12)
    c.drawString(100, 800, f"ロト6レポート：{latest_month} 月分")
    y = 770

    for _, row in df_latest.iterrows():
        date_str = row["抽せん日"].strftime("%Y-%m-%d")
        numbers = " ".join(str(int(row[f"数字{i}"])) for i in range(1, 7))
        bonus = str(int(row["ボーナス1"])) if "ボーナス1" in row and not pd.isna(row["ボーナス1"]) else ""
        c.drawString(100, y, f"{date_str}： {numbers} （B:{bonus}）")
        y -= 20
        if y < 100:
            c.showPage()
            c.setFont("IPAexG", 12)
            y = 770

    c.save()
    print(f"✅ PDFレポートを生成しました：{file_name}")

except Exception as e:
    print("❌ エラーが発生しました：", e)
