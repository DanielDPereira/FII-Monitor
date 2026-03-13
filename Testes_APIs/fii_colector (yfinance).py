import yfinance as yf
import pandas as pd
from pathlib import Path


def get_fii_data(ticker: str):

    print(f"Coletando dados de {ticker}...")

    ticker_yf = yf.Ticker(ticker)

    # =========================
    # HISTÓRICO DIÁRIO
    # =========================

    hist = ticker_yf.history(
        period="max",
        interval="1d",
        auto_adjust=False,
        actions=True
    )

    if hist.empty:
        raise ValueError("Nenhum dado retornado.")

    price_history = hist.reset_index()

    price_history = price_history.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
        "Dividends": "dividends"
    })

    price_history["ticker"] = ticker

    price_history = price_history[
        [
            "ticker",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "dividends"
        ]
    ]

    # =========================
    # HISTÓRICO MENSAL (PREÇOS)
    # =========================

    hist_monthly = hist.resample("ME").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    })

    monthly_prices = hist_monthly.reset_index()

    monthly_prices = monthly_prices.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    monthly_prices["ticker"] = ticker

    monthly_prices = monthly_prices[
        [
            "ticker",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    ]

    # =========================
    # DIVIDENDOS DIÁRIOS
    # =========================

    dividends = ticker_yf.dividends

    dividends_df = dividends.reset_index()

    dividends_df = dividends_df.rename(columns={
        "Date": "date",
        "Dividends": "dividend"
    })

    dividends_df["ticker"] = ticker

    dividends_df = dividends_df[
        [
            "ticker",
            "date",
            "dividend"
        ]
    ]

    # =========================
    # DIVIDENDOS MENSAIS
    # =========================

    dividends_monthly = dividends.resample("ME").sum()

    dividends_monthly_df = dividends_monthly.reset_index()

    dividends_monthly_df = dividends_monthly_df.rename(columns={
        "Date": "date",
        "Dividends": "dividend"
    })

    dividends_monthly_df["ticker"] = ticker

    dividends_monthly_df = dividends_monthly_df[
        [
            "ticker",
            "date",
            "dividend"
        ]
    ]

    # =========================
    # INFORMAÇÕES DO ATIVO
    # =========================

    info = ticker_yf.info

    price = info.get("regularMarketPrice")

    market_cap = info.get("marketCap")

    avg_volume = info.get("averageVolume")

    dividend_yield = info.get("dividendYield")

    book_value = info.get("bookValue")

    # =========================
    # CÁLCULO P/VP
    # =========================

    p_vp = None
    if price and book_value:
        p_vp = price / book_value

    # =========================
    # DY 12 MESES
    # =========================

    dividend_12m = dividends.tail(12).sum()

    dy_12m = None
    if price:
        dy_12m = dividend_12m / price

    metrics = pd.DataFrame([{
        "ticker": ticker,
        "price": price,
        "book_value": book_value,
        "p_vp": p_vp,
        "dividend_yield_api": dividend_yield,
        "dividend_12m": dividend_12m,
        "dy_12m": dy_12m,
        "market_cap": market_cap,
        "avg_volume": avg_volume
    }])

    return {
        "price_history": price_history,
        "monthly_prices": monthly_prices,
        "dividends": dividends_df,
        "dividends_monthly": dividends_monthly_df,
        "metrics": metrics
    }


def save_data(data, output_dir="data"):

    path = Path(output_dir)
    path.mkdir(exist_ok=True)

    data["price_history"].to_csv(path / "price_history.csv", index=False)
    data["monthly_prices"].to_csv(path / "monthly_prices.csv", index=False)
    data["dividends"].to_csv(path / "dividends.csv", index=False)
    data["dividends_monthly"].to_csv(path / "dividends_monthly.csv", index=False)
    data["metrics"].to_csv(path / "metrics.csv", index=False)

    print("Arquivos salvos em:", path.resolve())


if __name__ == "__main__":

    ticker = "HGLG11.SA"

    data = get_fii_data(ticker)

    save_data(data)

    print("\nResumo dos dados coletados:\n")

    print("Histórico diário:", len(data["price_history"]), "linhas")
    print("Preços mensais:", len(data["monthly_prices"]), "linhas")
    print("Dividendos:", len(data["dividends"]), "linhas")
    print("Dividendos mensais:", len(data["dividends_monthly"]), "linhas")

    print("\nMétricas atuais:")
    print(data["metrics"])