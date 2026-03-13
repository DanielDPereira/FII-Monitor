"""
Página: Cadastro de Ativos (FIIs)
"""

import streamlit as st
import sys
import os

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db

# ─── Setores comuns de FII ───────────────────────────────────────────────────
SETORES = [
    "Lajes Corporativas",
    "Shoppings",
    "Logística",
    "Residencial",
    "Recebíveis (CRI)",
    "Híbrido",
    "Agências Bancárias",
    "Hoteleiro",
    "Educacional",
    "Desenvolvimento",
    "Fundo de Fundos (FoF)",
    "Outro",
]


def _badge_setor(setor: str) -> str:
    """Retorna HTML de badge colorido para o setor."""
    colors = {
        "Lajes Corporativas":   "#4A90D9",
        "Shoppings":            "#E07B39",
        "Logística":            "#5CB85C",
        "Residencial":          "#9B59B6",
        "Recebíveis (CRI)":     "#F0AD4E",
        "Híbrido":              "#1ABC9C",
        "Agências Bancárias":   "#3498DB",
        "Hoteleiro":            "#E74C3C",
        "Educacional":          "#2ECC71",
        "Desenvolvimento":      "#8E44AD",
        "Fundo de Fundos (FoF)":"#16A085",
        "Outro":                "#95A5A6",
    }
    color = colors.get(setor, "#95A5A6")
    return (
        f'<span style="background:{color};color:white;padding:2px 8px;'
        f'border-radius:10px;font-size:0.78rem;font-weight:600;">{setor}</span>'
    )


def render():
    st.title("📋 Cadastro de Ativos")
    st.markdown(
        "Gerencie os **Fundos de Investimento Imobiliário (FIIs)** monitorados no sistema.",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Tabs principais ──────────────────────────────────────────────────────
    tab_lista, tab_novo, tab_editar, tab_excluir = st.tabs(
        ["📊 Ativos Cadastrados", "➕ Novo Ativo", "✏️ Editar Ativo", "🗑️ Excluir Ativo"]
    )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — Lista de ativos
    # ════════════════════════════════════════════════════════════════════════
    with tab_lista:
        _tab_lista()

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — Novo ativo
    # ════════════════════════════════════════════════════════════════════════
    with tab_novo:
        _tab_novo()

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — Editar ativo
    # ════════════════════════════════════════════════════════════════════════
    with tab_editar:
        _tab_editar()

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — Excluir ativo
    # ════════════════════════════════════════════════════════════════════════
    with tab_excluir:
        _tab_excluir()


# ─── Tab: Lista ──────────────────────────────────────────────────────────────

def _tab_lista():
    ativos = db.listar_ativos()

    if not ativos:
        st.info("Nenhum ativo cadastrado ainda. Use a aba **➕ Novo Ativo** para começar.", icon="📭")
        return

    # Métricas resumo
    col1, col2 = st.columns(2)
    setores_unicos = len({a["setor"] for a in ativos if a["setor"]})
    col1.metric("Total de FIIs", len(ativos))
    col2.metric("Setores", setores_unicos)

    st.markdown("---")

    # Filtros
    with st.expander("🔍 Filtros", expanded=False):
        f_setor = st.multiselect(
            "Filtrar por Setor",
            options=sorted({a["setor"] for a in ativos if a["setor"]}),
        )
        f_ticker = st.text_input("Buscar Ticker", placeholder="Ex: MXRF11")

    # Aplica filtros
    dados = ativos
    if f_setor:
        dados = [a for a in dados if a["setor"] in f_setor]
    if f_ticker:
        dados = [a for a in dados if f_ticker.upper() in a["ticker"]]

    if not dados:
        st.warning("Nenhum ativo encontrado com os filtros aplicados.")
        return

    # Exibe cards em grid
    cols_per_row = 3
    for i in range(0, len(dados), cols_per_row):
        row = dados[i : i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, ativo in zip(cols, row):
            with col:
                st.markdown(
                    f"""
                    <div style="
                        border:1px solid #2d2d2d;
                        border-radius:12px;
                        padding:16px 18px;
                        background:#1a1a2e;
                        margin-bottom:12px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    ">
                        <div style="font-size:1.3rem;font-weight:700;color:#e0e0e0;letter-spacing:1px;">
                            {ativo['ticker']}
                        </div>
                        <div style="font-size:0.88rem;color:#aaa;margin:4px 0 10px;">
                            {ativo['nome']}
                        </div>
                        {_badge_setor(ativo['setor']) if ativo['setor'] else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ─── Tab: Novo ───────────────────────────────────────────────────────────────

def _tab_novo():
    st.subheader("Cadastrar Novo FII")

    with st.form("form_novo_ativo", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])

        with col1:
            ticker = st.text_input(
                "Ticker *",
                placeholder="Ex: MXRF11",
                max_chars=6,
                help="Digite apenas o ticker base com 6 caracteres (ex.: MXRF11). O sufixo .SA é adicionado internamente.",
            )

        with col2:
            nome = st.text_input(
                "Nome do Fundo *",
                placeholder="Ex: Maxi Renda FII",
                help="Nome completo do fundo.",
            )

        with st.container():
            setor = st.selectbox(
                "Setor",
                options=[""] + SETORES,
                format_func=lambda x: "Selecione um setor..." if x == "" else x,
            )

        submitted = st.form_submit_button("💾 Cadastrar Ativo", use_container_width=True, type="primary")

    if submitted:
        # Validações
        ticker = ticker.strip().upper()
        nome = nome.strip()

        erros = []
        if not ticker:
            erros.append("O **Ticker** é obrigatório.")
        elif len(ticker) != 6:
            erros.append("O **Ticker** deve ter exatamente 6 caracteres (ex.: MXRF11).")
        if not nome:
            erros.append("O **Nome do Fundo** é obrigatório.")

        if erros:
            for e in erros:
                st.error(e)
        else:
            ok = db.inserir_ativo(
                ticker=ticker,
                nome=nome,
                setor=setor if setor else "Outro",
            )
            if ok:
                st.success(f"✅ FII **{ticker}** cadastrado com sucesso!")
                st.balloons()
            else:
                st.error(f"❌ O ticker **{ticker}** já está cadastrado. Use a aba **✏️ Editar** para alterá-lo.")


# ─── Tab: Editar ─────────────────────────────────────────────────────────────

def _tab_editar():
    st.subheader("Editar Ativo")

    ativos = db.listar_ativos()
    if not ativos:
        st.info("Nenhum ativo cadastrado para editar.", icon="📭")
        return

    tickers = [a["ticker"] for a in ativos]
    ticker_sel = st.selectbox("Selecione o Ticker", options=tickers, key="edit_select")

    if ticker_sel:
        ativo = db.buscar_ativo(ticker_sel)
        if ativo:
            with st.form("form_editar_ativo"):
                st.markdown(f"**Editando:** `{ativo['ticker']}`")

                nome_edit = st.text_input("Nome do Fundo *", value=ativo["nome"])

                setor_idx = 0
                opts = [""] + SETORES
                if ativo["setor"] in opts:
                    setor_idx = opts.index(ativo["setor"])
                setor_edit = st.selectbox("Setor", options=opts, index=setor_idx)

                salvar = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)

            if salvar:
                nome_edit = nome_edit.strip()
                if not nome_edit:
                    st.error("O **Nome do Fundo** é obrigatório.")
                else:
                    db.atualizar_ativo(
                        ticker=ticker_sel,
                        nome=nome_edit,
                        setor=setor_edit if setor_edit else "Outro",
                    )
                    st.success(f"✅ FII **{ticker_sel}** atualizado com sucesso!")
                    st.rerun()


# ─── Tab: Excluir ────────────────────────────────────────────────────────────

def _tab_excluir():
    st.subheader("Excluir Ativo")

    ativos = db.listar_ativos()
    if not ativos:
        st.info("Nenhum ativo cadastrado para excluir.", icon="📭")
        return

    tickers = [a["ticker"] for a in ativos]
    ticker_del = st.selectbox("Selecione o Ticker", options=tickers, key="del_select")

    if ticker_del:
        ativo = db.buscar_ativo(ticker_del)
        if ativo:
            st.markdown(
                f"""
                <div style="background:#2a1a1a;border:1px solid #7f1d1d;border-radius:10px;padding:16px;margin:12px 0;">
                    <strong style="color:#f87171;">⚠️ Atenção:</strong><br>
                    Você está prestes a excluir o FII <strong>{ativo['ticker']}</strong> — {ativo['nome']}.<br>
                    <small style="color:#aaa;">Esta ação também pode afetar transações e proventos vinculados a este ativo.</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

            confirmar = st.checkbox(f"Confirmo que desejo excluir **{ticker_del}** permanentemente")

            if st.button("🗑️ Excluir Ativo", type="primary", disabled=not confirmar):
                db.deletar_ativo(ticker_del)
                st.success(f"✅ FII **{ticker_del}** excluído com sucesso!")
                st.rerun()
