import yfinance as yf

fii = yf.Ticker("MXRF11.SA")

print(fii.info)

hist = fii.history(period="5y")

print(hist.head())

print(fii.dividends)