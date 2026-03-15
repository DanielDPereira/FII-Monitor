"""
Página: Carteira e Transações
"""

from datetime import date, datetime
import streamlit as st
import sys
import os

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db


TIPOS_TRANSACAO = ["COMPRA", "VENDA"]


def _fmt_brl(valor):
    if valor is None:
        return "-"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_pct(valor):
    if valor is None:
        return "-"
    return f"{valor:.2f}%"


def _fmt_datetime_br(ts: str | None) -> str:
    if not ts:
        return "Sem atualização de mercado ainda."
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return ts


def render():
    st.title("📈 Carteira")
    st.markdown("Acompanhe posição consolidada e registre suas operações.")
    st.divider()

    tab_resumo, tab_transacao, tab_historico = st.tabs(
        ["📊 Posição Atual", "➕ Registrar Transação", "🧾 Histórico"]
    )

    with tab_resumo:
        _tab_resumo()

    with tab_transacao:
        _tab_transacao()

    with tab_historico:
        _tab_historico()


def _tab_resumo():
    col_btn_1, col_btn_2 = st.columns([1, 3])
    with col_btn_1:
        if st.button("🔄 Atualizar dados", width="stretch"):
            ativos = db.listar_ativos()
            tickers = [a["ticker"] for a in ativos]
            if not tickers:
                st.warning("Cadastre ao menos um ativo para atualizar dados de mercado.")
            else:
                with st.spinner("Buscando dados no yfinance..."):
                    try:
                        counters = db.atualizar_dados_mercado_yfinance(tickers)
                        proventos_count = db.sincronizar_proventos_automaticos()
                        st.success(
                            "Atualização concluída "
                            f"(tickers: {counters['tickers_processados']}, "
                            f"eventos de dividendos: {counters['fii_dividends']}, "
                            f"proventos calculados: {proventos_count})."
                        )
                    except Exception as exc:
                        st.error(f"Falha ao atualizar dados de mercado: {str(exc)}")

    with col_btn_2:
        ultima_atualizacao = db.obter_ultima_atualizacao_mercado()
        st.caption(f"Última atualização de mercado: {_fmt_datetime_br(ultima_atualizacao)}")

    db.sincronizar_proventos_automaticos()
    resumo = db.resumo_carteira()
    posicoes = db.calcular_posicoes_carteira()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Ativos em Carteira", resumo["ativos_em_carteira"])
    col2.metric("Custo Total", _fmt_brl(resumo["custo_total"]))
    col3.metric("Valor Atual", _fmt_brl(resumo["valor_atual_total"]))
    col4.metric("Proventos Acumulados", _fmt_brl(resumo["proventos_acumulados_total"]))

    pl_total = resumo["pl_total"]
    delta_total = None
    if resumo["custo_total"] > 0:
        delta_total = _fmt_pct((pl_total / resumo["custo_total"]) * 100)
    col5.metric("Resultado Total", _fmt_brl(pl_total), delta=delta_total)

    #st.caption("Preço Atual = preço unitário da cota. Valor Atual = preço unitário multiplicado pela quantidade em carteira.")

    st.markdown("---")

    if not posicoes:
        st.info("Nenhuma posição em carteira. Registre compras na aba de transações.", icon="📭")
        return

    tabela = []
    for p in posicoes:
        pl_pct = None
        if p["custo_posicao"] > 0 and p["pl_nao_realizado"] is not None:
            pl_pct = (p["pl_nao_realizado"] / p["custo_posicao"]) * 100

        tabela.append(
            {
                "Ticker": p["ticker"],
                "Nome": p["nome"],
                "Setor": p["setor"],
                "Qtd": p["quantidade"],
                "Preço Médio": _fmt_brl(p["preco_medio"]),
                "Custo": _fmt_brl(p["custo_posicao"]),
                "Preço Atual": _fmt_brl(p["preco_atual"]),
                "Valor Atual": _fmt_brl(p["valor_atual"]),
                "Proventos Acumulados": _fmt_brl(p["proventos_acumulados"]),
                "Resultado": _fmt_brl(p["pl_nao_realizado"]),
                "Resultado %": _fmt_pct(pl_pct),
            }
        )

    st.dataframe(tabela, width="stretch", hide_index=True)


def _tab_transacao():
    st.subheader("Registrar Compra ou Venda")

    ativos = db.listar_ativos()
    if not ativos:
        st.warning("Cadastre ao menos um ativo antes de lançar transações.")
        return

    opcoes_ativos = [a["ticker"] for a in ativos]

    with st.form("form_transacao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.selectbox("Ticker", options=opcoes_ativos)
            tipo = st.radio("Tipo", options=TIPOS_TRANSACAO, horizontal=True)
        with col2:
            data_tx = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            quantidade = st.number_input("Quantidade", min_value=1, step=1)

        preco_unitario = st.number_input(
            "Preço Unitário (R$)",
            min_value=0.01,
            step=0.01,
            format="%.2f",
        )

        enviar = st.form_submit_button("💾 Salvar Transação", width="stretch", type="primary")

    if enviar:
        try:
            ok = db.inserir_transacao(
                ticker=ticker,
                data=data_tx.isoformat(),
                tipo=tipo,
                quantidade=int(quantidade),
                preco_unitario=float(preco_unitario),
            )
            if ok:
                st.success(f"Transação de {tipo} para {ticker} registrada com sucesso.")
                st.rerun()
            else:
                st.error("Não foi possível salvar: o ativo informado não existe.")
        except ValueError as exc:
            st.error(f"Não foi possível salvar a transação: {str(exc)}")


def _tab_historico():
    st.subheader("Histórico de Transações")

    transacoes = db.listar_transacoes(limite=1000)
    ativos = db.listar_ativos()
    if not transacoes:
        st.info("Nenhuma transação registrada ainda.", icon="🧾")
        return

    tabela = []
    for tx in transacoes:
        tabela.append(
            {
                "ID": tx["id"],
                "Data": tx["data"],
                "Ticker": tx["ticker"],
                "Tipo": tx["tipo"],
                "Quantidade": tx["quantidade"],
                "Preço Unitário": _fmt_brl(tx["preco_unitario"]),
                "Valor Total": _fmt_brl(tx["valor_total"]),
            }
        )

    st.dataframe(tabela, width="stretch", hide_index=True)

    st.markdown("---")
    st.markdown("### Editar Transação")

    ids = [tx["id"] for tx in transacoes]
    tx_edit_id = st.selectbox("Selecionar ID para editar", options=ids, key="edit_tx_id")
    transacao = db.buscar_transacao(tx_edit_id)

    if transacao:
        tickers = [a["ticker"] for a in ativos]
        ticker_index = tickers.index(transacao["ticker"]) if transacao["ticker"] in tickers else 0
        tipo_index = TIPOS_TRANSACAO.index(transacao["tipo"]) if transacao["tipo"] in TIPOS_TRANSACAO else 0

        with st.form(f"form_editar_transacao_{tx_edit_id}"):
            col1, col2 = st.columns(2)
            with col1:
                ticker_edit = st.selectbox("Ticker", options=tickers, index=ticker_index)
                tipo_edit = st.radio("Tipo", options=TIPOS_TRANSACAO, index=tipo_index, horizontal=True)
            with col2:
                data_edit = st.date_input(
                    "Data",
                    value=date.fromisoformat(transacao["data"]),
                    format="DD/MM/YYYY",
                )
                quantidade_edit = st.number_input(
                    "Quantidade",
                    min_value=1,
                    step=1,
                    value=int(transacao["quantidade"]),
                )

            preco_edit = st.number_input(
                "Preço Unitário (R$)",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                value=float(transacao["preco_unitario"]),
            )

            salvar_edicao = st.form_submit_button(
                "💾 Atualizar Transação",
                width="stretch",
                type="primary",
            )

        if salvar_edicao:
            try:
                ok = db.atualizar_transacao(
                    transacao_id=tx_edit_id,
                    ticker=ticker_edit,
                    data=data_edit.isoformat(),
                    tipo=tipo_edit,
                    quantidade=int(quantidade_edit),
                    preco_unitario=float(preco_edit),
                )
                if ok:
                    st.success("Transação atualizada com sucesso.")
                    st.rerun()
                else:
                    st.error("Não foi possível atualizar: o ativo informado não existe.")
            except ValueError as exc:
                st.error(f"Não foi possível atualizar a transação: {str(exc)}")

    st.markdown("---")
    st.caption("Exclusão de transação é permanente e altera os cálculos da carteira.")

    tx_id = st.selectbox("Selecionar ID para excluir", options=ids)
    confirmar = st.checkbox("Confirmo exclusão da transação selecionada")

    if st.button("🗑️ Excluir Transação", disabled=not confirmar):
        db.deletar_transacao(tx_id)
        st.success("Transação excluída com sucesso.")
        st.rerun()
