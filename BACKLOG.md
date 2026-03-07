# 📊 Backlog do Projeto: FII-Monitor

## 🎯 Visão do Produto
O FII-Monitor é uma aplicação web desenvolvida em Python (Streamlit) e SQLite, voltada para investidores de Fundos Imobiliários (FIIs). O objetivo é gerenciar carteiras, analisar indicadores fundamentalistas, monitorar proventos e descobrir oportunidades de mercado.

---

## 🗺️ Épicos e User Stories (Histórias de Usuário)

### Épico 1: Gestão de Carteira (Portfolio Management)
**Objetivo**: Permitir que o usuário controle o que ele tem, quanto pagou e como está a evolução.
- [ ] **US 1.1**: Como usuário, quero cadastrar as cotas de FIIs que comprei (Ticker, Quantidade, Preço Médio, Data), para ter o registro da minha carteira.
- [ ] **US 1.2**: Como usuário, quero visualizar um dashboard com a posição atual da minha carteira (Valor Total Investido vs Valor Atual, Lucro/Prejuízo).
- [ ] **US 1.3**: Como usuário, quero ver um gráfico de pizza com a diversificação da minha carteira por **Setor** (Papel, Galpões, Shopping, etc.).
- [ ] **US 1.4**: Como usuário, quero registrar vendas de cotas para atualizar minha posição e calcular lucro/prejuízo de capital.

### Épico 2: Acompanhamento de Proventos (Dividendos)
**Objetivo**: Ter previsibilidade e controle sobre a renda passiva.
- [ ] **US 2.1**: Como usuário, quero visualizar um histórico de dividendos recebidos por mês através de um gráfico de barras.
- [ ] **US 2.2**: Como usuário, quero um calendário mostrando as datas "Com" (data limite para comprar e ter direito ao dividendo) e as datas de "Pagamento" dos FIIs da minha carteira.
- [ ] **US 2.3**: Como usuário, quero saber o meu "Dividend Yield On Cost" (DY sobre o meu preço médio) da carteira.

### Épico 3: Análise e Comparação de Fundos
**Objetivo**: Auxiliar a tomada de decisão para novos aportes.
- [ ] **US 3.1**: Como usuário, quero buscar um FII específico (ex: HGLG11) e ver seus dados gerais (P/VP, Último Rendimento, DY, Liquidez, Vacância).
- [ ] **US 3.2**: Como usuário, quero poder selecionar até 3 FIIs do mesmo setor e ver uma tabela comparativa lado a lado com seus indicadores.
- [ ] **US 3.3**: Como usuário, quero ver um gráfico do histórico de cotação e de pagamentos de dividendos de um FII nos últimos 12 meses, 3 anos e 5 anos.

### Épico 4: Oportunidades e Ferramentas Inteligentes
**Objetivo**: Insights proativos para melhorar a rentabilidade.
- [ ] **US 4.1**: Como usuário, quero ver um ranking de "Oportunidades" baseado em FIIs de bons fundamentos que estão com P/VP abaixo de 1 (com deságio).
- [ ] **US 4.2**: Como usuário, quero calcular o **"Magic Number"** de um fundo (quantas cotas preciso ter para comprar 1 nova cota só com os dividendos).
- [ ] **US 4.3**: Como usuário, quero uma sugestão de rebalanceamento: baseado na porcentagem que defini para cada setor, o app me diz onde devo aportar neste mês.

### Épico 5: Infraestrutura e Integração de Dados
**Objetivo**: Base técnica sustentável (Streamlit + SQLite + APIs).
- [ ] **US 5.1**: Modelar e criar o banco de dados SQLite (tabelas: `usuarios`, `transacoes`, `ativos_cache`).
- [ ] **US 5.2**: Integrar com as APIs para atualizar as cotações e rendimentos sempre que o painel for aberto.
- [ ] **US 5.3**: Criar uma rotina (cache) para não sobrecarregar as APIs, atualizando os dados fundamentalistas apenas 1x ao dia.

---

## 💡 Próximos Passos (MVP)
Para a primeira versão (MVP - Minimum Viable Product), recomendo focar apenas no **Épico 1** (Cadastro e Listagem básica da carteira) e **Épico 5**, garantindo que o fluxo técnico do SQLite + Streamlit funcione perfeitamente antes de partir para telas de gráficos complexos.
