import yfinance as yf
import pandas as pd

fii = yf.Ticker("MXRF11.SA")

# Histórico completo
hist = fii.history(period="max")
print(hist.head())

# Dividendos
div = fii.dividends

# Agrupar dividendos por mês (fim do mês)
div_mensal = div.resample("ME").sum()

print(div_mensal)

'''
(.venv) PS C:\Users\Daniel\Documents\.Projetos\FII-Monitor\Testes_APIs> python .\teste_yfinance.py
                               Open      High  ...  Dividends  Stock Splits
Date                                           ...
2014-08-06 00:00:00-03:00  4.936393  4.941794  ...        0.0           0.0     
2014-08-07 00:00:00-03:00  4.895583  4.895583  ...        0.0           0.0     
2014-08-08 00:00:00-03:00  4.852369  4.948396  ...        0.0           0.0     
2014-08-11 00:00:00-03:00  4.921389  4.921389  ...        0.0           0.0     
2014-08-12 00:00:00-03:00  4.891379  4.921388  ...        0.0           0.0     

[5 rows x 7 columns]
Date
2017-11-30 00:00:00-02:00    0.059074
2017-12-31 00:00:00-02:00    0.059074
2018-01-31 00:00:00-02:00    0.000000
2018-02-28 00:00:00-03:00    0.000000
2018-03-31 00:00:00-03:00    0.000000
                               ...
2025-11-30 00:00:00-03:00    0.100000
2025-12-31 00:00:00-03:00    0.100000
2026-01-31 00:00:00-03:00    0.100000
2026-02-28 00:00:00-03:00    0.100000
2026-03-31 00:00:00-03:00    0.100000
Freq: ME, Name: Dividends, Length: 101, dtype: float64

'''
