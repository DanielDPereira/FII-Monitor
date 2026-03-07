import fundamentus
import pandas as pd

df_mercado = fundamentus.get_resultado_raw()

print("Total de ativos:", len(df_mercado))

ticker = "PETR4"

if ticker in df_mercado.index:
    dados_ativo = df_mercado.loc[ticker]

    print(dados_ativo)
else:
    print("Ticker não encontrado.")

print([i for i in df_mercado.index if i.endswith("11")][:20])