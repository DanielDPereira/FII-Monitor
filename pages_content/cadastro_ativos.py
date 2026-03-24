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
    "Fiagro",
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
        "Fiagro":               "#2D7D46",
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

def _fmt_brl(value, casas: int = 2) -> str:
    if value is None:
        return "N/A"
    texto = f"{float(value):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def _fmt_pct(value, casas: int = 2) -> str:
    if value is None:
        return "N/A"
    texto = f"{float(value):.{casas}f}".replace(".", ",")
    return f"{texto}%"


def _fmt_int(value) -> str:
    if value is None:
        return "N/A"
    return f"{int(value):,}".replace(",", ".")

def _metrica_customizada(label: str, valor: str, delta: str = None):
    """Renderiza uma métrica sem truncamento usando HTML puro em formato de card."""
    delta_html = ""
    if delta:
        cor_delta = "#4ade80" if "↑" in delta or "+" in delta else ("#f87171" if "↓" in delta or "-" in delta else "#a0a0b0")
        delta_html = f"<div style='color: {cor_delta}; font-size: 0.95rem; font-weight: 600; margin-top: 4px;'>{delta}</div>"
    
    st.markdown(
        f"""
        <div style="background: #1e1e2f; padding: 18px 20px; border-radius: 12px; margin-bottom: 16px; border: 1px solid #3d3d5c; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="color: #b0b0c0; font-size: 0.95rem; font-weight: 500; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
            <div style="color: #ffffff; font-size: 1.6rem; font-weight: 700;">{valor}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def _renderizar_modal_detalhes(ticker: str):
    """Renderiza um modal com detalhes do FII do yfinance - sem truncamento."""
    detalhes = db.obter_detalhes_fii(ticker)
    
    if not detalhes["ok"]:
        st.error(f"❌ {detalhes['erro']}")
        return
    
    dados = detalhes["dados"]
    
    st.markdown(f"## {dados['ticker']} — {dados['nome']}")
    st.divider()
    
    tab_resumo, tab_div, tab_fund = st.tabs(["📊 Resumo", "💰 Dividendos", "🏢 Fundamentos"])
    
    # ─── ABA 1: RESUMO (PREÇOS E VARIAÇÕES) ─────────────────────────────────
    with tab_resumo:
        col1, col2 = st.columns(2)
        with col1:
            delta_str = None
            if dados.get("variacao_1d") is not None:
                delta_str = f"↑ {_fmt_pct(dados['variacao_1d'])}" if dados["variacao_1d"] >= 0 else f"↓ {_fmt_pct(dados['variacao_1d'])}"
            _metrica_customizada("Valor Atual", _fmt_brl(dados["preco_atual"]), delta=delta_str)
            _metrica_customizada("Variação Mês", _fmt_pct(dados["variacao_1m"]))
            _metrica_customizada("Mínima (52 Semanas)", _fmt_brl(dados["min_52w"]))
        
        with col2:
            _metrica_customizada("Variação 12m", _fmt_pct(dados["variacao_52w"]))
            _metrica_customizada("Mínima (Mês Atual)", _fmt_brl(dados["min_mes"]))
            _metrica_customizada("Máxima (52 Semanas)", _fmt_brl(dados["max_52w"]))

    # ─── ABA 2: DIVIDENDOS ──────────────────────────────────────────────────
    with tab_div:
        col1, col2 = st.columns(2)
        with col1:
            _metrica_customizada("Últimos 12 Meses", _fmt_brl(dados["dividend_12m"], casas=4))
        with col2:
            _metrica_customizada("DY 12 Meses", _fmt_pct(dados["dy_12m"]))
            
    # ─── ABA 3: FUNDAMENTOS ─────────────────────────────────────────────────
    with tab_fund:
        col1, col2 = st.columns(2)
        with col1:
            _metrica_customizada("Valor Patrimonial/Cota", _fmt_brl(dados["book_value"]))
            p_vp_str = f"{dados['p_vp']:.2f}".replace(".", ",") if dados.get("p_vp") is not None else "N/A"
            _metrica_customizada("P/VP", p_vp_str)
            if dados.get("patrimonio"):
                _metrica_customizada("Patrimônio Líquido", _fmt_brl(dados["patrimonio"], casas=0))
                
        with col2:
            _metrica_customizada("Valor de Mercado", _fmt_brl(dados["market_cap"], casas=0))
            if dados.get("avg_volume"):
                _metrica_customizada("Liq. Média Diária", _fmt_int(dados["avg_volume"]))
            ifdados_cotas = dados.get("shares_outstanding")
            if ifdados_cotas:
                _metrica_customizada("Nº de Cotas", _fmt_int(ifdados_cotas))

    st.divider()
    st.caption("📊 Dados extraídos do yfinance. Atualizar para obter informações recentes.")


@st.dialog("Detalhes do ativo")
def _abrir_dialog_detalhes(ticker: str):
    _renderizar_modal_detalhes(ticker)


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
                
                # Botão para abrir modal
                if st.button(
                    "📊 Ver Detalhes",
                    key=f"btn_detalhes_{ativo['ticker']}",
                    use_container_width=True,
                ):
                    _abrir_dialog_detalhes(ativo["ticker"])


# ─── Tab: Novo ───────────────────────────────────────────────────────────────

def _tab_novo():
    st.subheader("Cadastrar Novo Ativo")
    st.caption("Informe apenas o ticker. O nome do ativo será buscado automaticamente no yfinance.")

    with st.form("form_novo_ativo", clear_on_submit=True):
        ticker = st.text_input(
            "Ticker *",
            placeholder="Ex: MXRF11",
            max_chars=12,
            help="Digite o ticker com ou sem .SA (ex.: MXRF11 ou MXRF11.SA).",
        )

        with st.container():
            setor = st.selectbox(
                "Setor",
                options=[""] + SETORES,
                format_func=lambda x: "Selecione um setor..." if x == "" else x,
            )

        submitted = st.form_submit_button("💾 Cadastrar Ativo", width="stretch", type="primary")

    if submitted:
        # Validações
        ticker = ticker.strip().upper()

        erros = []
        if not ticker:
            erros.append("O **Ticker** é obrigatório.")

        if erros:
            for e in erros:
                st.error(e)
        else:
            ativo_yf = db.consultar_ativo_yfinance(ticker)
            if not ativo_yf["ok"]:
                st.error(f"❌ {ativo_yf['erro']}")
                return

            ticker_validado = ativo_yf["ticker"]
            nome_ativo = ativo_yf["nome"]
            ok = db.inserir_ativo(
                ticker=ticker_validado,
                nome=nome_ativo,
                setor=setor if setor else "Outro",
            )
            if ok:
                st.success(
                    f"✅ Ativo **{ticker_validado}** cadastrado com sucesso! "
                    f"Nome identificado: **{nome_ativo}**."
                )
                st.balloons()
            else:
                st.error(
                    f"❌ O ticker **{ticker_validado}** já está cadastrado. "
                    "Use a aba **✏️ Editar** para alterá-lo."
                )


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

                salvar = st.form_submit_button("💾 Salvar Alterações", type="primary", width="stretch")

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
