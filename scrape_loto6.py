import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_loto6_data(n=100):
    base_url = "https://www.mizuhobank.co.jp/retail/takarakuji/loto6/backnumber/index.html"
    results = []

    for page in range(1, (n // 10) + 2):  # 1ページに10回分
        url = f"{base_url}?page={page}"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        
        tables = soup.select("table.typeTK")  # 当選番号が入っているテーブルを取得
        for table in tables:
            rows = table.select("tr")[1:]  # ヘッダ行を除く
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    date = cols[0].text.strip()
                    numbers = cols[1].text.strip().split(" ")
                    bonus = cols[2].text.strip()
                    if len(numbers) == 6:
                        results.append({
                            "抽せん日": date,
                            "本数字": numbers,
                            "ボーナス数字": bonus
                        })
                if len(results) >= n:
                    break
            if len(results) >= n:
                break
        if len(results) >= n:
            break

    df = pd.DataFrame(results)
    return df

# 実行テスト
if __name__ == "__main__":
    df = fetch_loto6_data(100)
    print(df.head())
    df.to_csv("loto6_past_100.csv", index=False, encoding="utf-8-sig")
