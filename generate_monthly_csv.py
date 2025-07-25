def generate_pdf_report(df, month):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    # 📌 列名を num1～num6 にリネーム（元データが「数字１」などの場合）
    rename_dict = {
        "数字１": "num1",
        "数字２": "num2",
        "数字３": "num3",
        "数字４": "num4",
        "数字５": "num5",
        "数字６": "num6",
    }
    df = df.rename(columns=rename_dict)

    # すでにPDFが存在する場合はスキップ
    file_path = f"{month}_report.pdf"
    if os.path.exists(file_path):
        return

    # フォント登録
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

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
