import yfinance as yf
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

def get_fii_fundamentals(ticker):

    try:
        fii = yf.Ticker(f"{ticker}.SA")
        info = fii.info

        price = info.get("regularMarketPrice")

        dividends = fii.dividends.tail(12)
        dividend_sum = dividends.sum()

        dy = dividend_sum / price if price else None

        return {
            "ticker": ticker,
            "price": price,
            "pvp": info.get("priceToBook"),
            "dy_12m": dy,
            "dividend_12m": dividend_sum,
            "liquidez_media": info.get("averageVolume"),
            "liquidez_10d": info.get("averageVolume10days"),
            "market_cap": info.get("marketCap"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow")
        }

    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return None


fiis = ["HGLG11", "KNRI11", "XPLG11", "MXRF11"]

data = [get_fii_fundamentals(f) for f in fiis]
data = [d for d in data if d is not None]

df = pd.DataFrame(data)

df["dy_12m"] = df["dy_12m"] * 100

#df = df.sort_values("dy_12m", ascending=False).reset_index(drop=True)

print(df.to_string())

'''
   ticker   price       pvp     dy_12m  dividend_12m  liquidez_media  liquidez_10d  market_cap  52w_high  52w_low
0  HGLG11  158.33  1.000575   8.337018         13.20           96084         81507  5349586944    163.30   149.48
1  KNRI11  167.67  1.046727   7.294090         12.23           40604         49212  4735740928    168.55   129.00
2  XPLG11  102.78       NaN   9.573847          9.84           53117         62794  3043648000    106.76    91.39
3  MXRF11    9.76  0.983276  12.192623          1.19         1810438       1804053  4268295168      9.99     8.99
'''