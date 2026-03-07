import yfinance as yf

fii = yf.Ticker("MXRF11.SA")

print(fii.info)

hist = fii.history(period="5y")

print(hist)

print(fii.dividends)

#Output
'''
{'address1': 'Avenida Paulista 1111 2 Andar Parte Bela Vista', 'address2': 'Bela 
Vista', 'city': 'Sao Paulo', 'state': 'SP', 'zip': '1311920', 'country': 'Brazil', 'phone': '55 11 3232 7603', 'fax': '55 11 4009 7047', 'industry': 'REIT - Diversified', 'industryKey': 'reit-diversified', 'industryDisp': 'REIT - Diversified', 'sector': 'Real Estate', 'sectorKey': 'real-estate', 'sectorDisp': 'Real Estate', 'longBusinessSummary': 'Maxi Renda Fundo De Investimento Imobiliaro - FII specializes in real estate investments.', 'companyOfficers': [], 'executiveTeam': [], 
'maxAge': 86400, 'priceHint': 2, 'previousClose': 9.69, 'open': 9.72, 'dayLow': 9.7, 'dayHigh': 9.76, 'regularMarketPreviousClose': 9.69, 'regularMarketOpen': 9.72, 'regularMarketDayLow': 9.7, 'regularMarketDayHigh': 9.76, 'dividendRate': 1.2, 'dividendYield': 12.3, 'exDividendDate': 1772409600, 'beta': -0.027, 'trailingPE': 13.942858, 'volume': 1589790, 'regularMarketVolume': 1589790, 'averageVolume': 1810438, 'averageVolume10days': 1804053, 'averageDailyVolume10Day': 1804053, 'bid': 9.76, 'ask': 9.77, 'bidSize': 0, 'askSize': 0, 'marketCap': 4268295168, 'nonDilutedMarketCap': 4237682127, 'fiftyTwoWeekLow': 8.99, 'fiftyTwoWeekHigh': 9.99, 
'allTimeHigh': 14.78167, 'allTimeLow': 7.413515, 'priceToSalesTrailing12Months': 
13.746965, 'fiftyDayAverage': 9.6122, 'twoHundredDayAverage': 9.55995, 'trailingAnnualDividendRate': 1.38, 'trailingAnnualDividendYield': 0.14241487, 'currency': 
'BRL', 'tradeable': False, 'profitMargins': 0.88521004, 'sharesOutstanding': 437325297, 'heldPercentInsiders': 0.0, 'heldPercentInstitutions': 0.03346, 'impliedSharesOutstanding': 437325297, 'bookValue': 9.926, 'priceToBook': 0.9832763, 'lastFiscalYearEnd': 1703980800, 'nextFiscalYearEnd': 1735603200, 'mostRecentQuarter': 
1688083200, 'earningsQuarterlyGrowth': 0.494, 'netIncomeToCommon': 274849984, 'trailingEps': 0.7, 'lastSplitFactor': '10:1', 'lastSplitDate': 1494979200, '52WeekChange': 0.07964599, 'SandP52WeekChange': 0.20045388, 'lastDividendValue': 0.1, 'lastDividendDate': 1772409600, 'quoteType': 'EQUITY', 'currentPrice': 9.76, 'recommendationKey': 'none', 'quickRatio': 0.757, 'currentRatio': 0.998, 'totalRevenue': 310489984, 'revenuePerShare': 1.081, 'returnOnAssets': 0.103690006, 'returnOnEquity': 0.107030004, 'grossProfits': 299996992, 'operatingCashflow': -25428000, 'earningsGrowth': 0.494, 'revenueGrowth': 0.454, 'grossMargins': 0.96621, 'ebitdaMargins': 0.0, 'operatingMargins': 0.9424, 'financialCurrency': 'BRL', 'symbol': 'MXRF11.SA', 'language': 'en-US', 'region': 'US', 'typeDisp': 'Equity', 'quoteSourceName': 'Delayed Quote', 'triggerable': False, 'customPriceAlertConfidence': 'LOW', 'longName': 'Maxi Renda Fundo De Investimento Imobiliaro - FII', 'regularMarketChangePercent': 0.72240096, 'regularMarketPrice': 9.76, 'shortName': 'FII MAXI RENCI', 'regularMarketChange': 0.07000065, 'regularMarketDayRange': '9.7 - 9.76', 
'fullExchangeName': 'São Paulo', 'averageDailyVolume3Month': 1810438, 'fiftyTwoWeekLowChange': 0.77000046, 'fiftyTwoWeekLowChangePercent': 0.08565078, 'fiftyTwoWeekRange': '8.99 - 9.99', 'fiftyTwoWeekHighChange': -0.22999954, 'fiftyTwoWeekHighChangePercent': -0.023022978, 'fiftyTwoWeekChangePercent': 7.964599, 'epsTrailingTwelveMonths': 0.7, 'fiftyDayAverageChange': 0.14780045, 'fiftyDayAverageChangePercent': 0.01537634, 'twoHundredDayAverageChange': 0.20005035, 'twoHundredDayAverageChangePercent': 0.02092588, 'sourceInterval': 15, 'exchangeDataDelayedBy': 15, 
'hasPrePostMarketData': False, 'firstTradeDateMilliseconds': 1407330000000, 'cryptoTradeable': False, 'corporateActions': [], 'regularMarketTime': 1772831220, 'exchange': 'SAO', 'messageBoardId': 'finmb_217515368', 'exchangeTimezoneName': 'America/Sao_Paulo', 'exchangeTimezoneShortName': 'BRT', 'gmtOffSetMilliseconds': -10800000, 'market': 'br_market', 'esgPopulated': False, 'marketState': 'CLOSED', 'trailingPegRatio': None}
                               Open      High  ...  Dividends  Stock Splits
Date                                           ...
2021-03-08 00:00:00-03:00  6.404656  6.483651  ...        0.0           0.0      
2021-03-09 00:00:00-03:00  6.441117  6.459347  ...        0.0           0.0      
2021-03-10 00:00:00-03:00  6.343889  6.398578  ...        0.0           0.0      
2021-03-11 00:00:00-03:00  6.356042  6.374271  ...        0.0           0.0      
2021-03-12 00:00:00-03:00  6.319583  6.325659  ...        0.0           0.0      

[5 rows x 7 columns]
Date
2017-11-01 00:00:00-02:00    0.059074
2017-12-01 00:00:00-02:00    0.059074
2022-05-02 00:00:00-03:00    0.108303
2022-06-01 00:00:00-03:00    0.108303
2022-07-01 00:00:00-03:00    0.098457
2022-08-01 00:00:00-03:00    0.118148
2022-09-01 00:00:00-03:00    0.108303
2022-10-03 00:00:00-03:00    0.098457
2022-11-01 00:00:00-03:00    0.098457
2022-12-01 00:00:00-03:00    0.078766
2023-01-02 00:00:00-03:00    0.098457
2023-02-01 00:00:00-03:00    0.108303
2023-03-01 00:00:00-03:00    0.118148
2023-04-03 00:00:00-03:00    0.118148
2023-05-02 00:00:00-03:00    0.118148
2023-06-01 00:00:00-03:00    0.118148
2023-07-03 00:00:00-03:00    0.118907
2023-08-01 00:00:00-03:00    0.118907
2023-09-01 00:00:00-03:00    0.108998
2023-10-02 00:00:00-03:00    0.108998
2023-11-01 00:00:00-03:00    0.108998
2023-12-01 00:00:00-03:00    0.109829
2024-01-02 00:00:00-03:00    0.109829
2024-02-01 00:00:00-03:00    0.099845
2024-03-01 00:00:00-03:00    0.099845
2024-04-01 00:00:00-03:00    0.099845
2024-05-02 00:00:00-03:00    0.099845
2024-06-03 00:00:00-03:00    0.099845
2024-07-01 00:00:00-03:00    0.100000
2024-08-01 00:00:00-03:00    0.100000
2024-09-02 00:00:00-03:00    0.090000
2024-10-01 00:00:00-03:00    0.090000
2024-11-01 00:00:00-03:00    0.090000
2024-12-02 00:00:00-03:00    0.100000
2025-01-02 00:00:00-03:00    0.100000
2025-02-03 00:00:00-03:00    0.090000
2025-03-05 00:00:00-03:00    0.090000
2025-04-01 00:00:00-03:00    0.090000
2025-05-02 00:00:00-03:00    0.100000
2025-06-02 00:00:00-03:00    0.100000
2025-07-01 00:00:00-03:00    0.100000
2025-08-01 00:00:00-03:00    0.100000
2025-09-01 00:00:00-03:00    0.100000
2025-10-01 00:00:00-03:00    0.100000
2025-11-03 00:00:00-03:00    0.100000
2025-12-01 00:00:00-03:00    0.100000
2026-01-02 00:00:00-03:00    0.100000
2026-02-02 00:00:00-03:00    0.100000
2026-03-02 00:00:00-03:00    0.100000
Name: Dividends, dtype: float64'''