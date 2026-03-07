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