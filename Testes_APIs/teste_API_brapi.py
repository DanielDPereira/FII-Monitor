import requests
import os
from dotenv import load_dotenv

load_dotenv()

def buscar_dados_fii(ticker):
    token = os.getenv('BrapiAPIToken')
    url = f"https://brapi.dev/api/quote/{ticker}"
    
    params = {
        'token': token,
        'range': '1d',
        'interval': '1d',
        'fundamental': 'true'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()['results'][0]
    else:
        return f"Erro {response.status_code}: {response.text}"

print(buscar_dados_fii("HGLG11"))

'''
{'symbol': 'HGLG11', 'shortName': 'HGLG11', 'longName': 'Patria Log - Fundo de Investimento Imobiliario - Responsabilidade Limitada Cotas', 'currency': 'BRL', 'regularMarketPrice': 158.33, 'regularMarketDayHigh': 158.9, 'regularMarketDayLow': 158.01, 'regularMarketDayRange': '158.01 - 158.9', 'regularMarketChange': 0.33, 'regularMarketChangePercent': 0.21, 'regularMarketTime': '2026-03-07T21:42:01.000Z', 'marketCap': None, 'regularMarketVolume': 108628, 'regularMarketPreviousClose': 158.75, 'regularMarketOpen': 158.2, 'fiftyTwoWeekRange': '149.48 - 163.3', 'fiftyTwoWeekLow': 149.48, 'fiftyTwoWeekHigh': 163.3, 'priceEarnings': None, 'earningsPerShare': None, 'logourl': 'https://icons.brapi.dev/icons/BRAPI.svg', 'usedInterval': '1d', 'usedRange': '1d', 'historicalDataPrice': [{'date': 1772831100, 'open': 158.2, 'high': 158.9, 'low': 158.01, 'close': 158.33, 'volume': 108561, 'adjustedClose': 158.33}], 'validRanges': ['1d', '2d', '5d', '7d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], 'validIntervals': ['1m', '2m', '5m', '15m', '30m', '60m', 
'90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']}
'''