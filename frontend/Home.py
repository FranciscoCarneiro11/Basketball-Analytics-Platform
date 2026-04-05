import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from utils import apply_theme, find_csv, col_pick, sidebar_nav

# Configuração da Página  
st.set_page_config(
    page_title="NBA Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS 
apply_theme("home")

# Paths 
DATA_DIR = Path(__file__).parent.parent / "outputs"

# Helpers 
def find_csv(names):
    for n in names:
        p = DATA_DIR / n
        if p.exists():
            return p
    return None

def col_pick(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

# Funcao para identificar a era 
def identificar_era(ano_fim):
    if ano_fim <= 1954:
        return "Early Years", "Periodo sem relogio de 24s. Jogo lento e focado no poste baixo."
    elif ano_fim <= 1979:
        return "Pre-3pt Era", "Introducao do Shot Clock e fusao com a ABA. Ritmo acelerado."
    elif ano_fim <= 1994:
        return "Golden Era", "Expansao global e dominio das grandes estrelas (Magic, Bird, Jordan)."
    elif ano_fim <= 2004:
        return "Dead Ball Era", "Defesas fisicas extremas e regras que dificultavam a marcacao de pontos."
    elif ano_fim <= 2014:
        return "Hybrid Era", "Inicio da analise de dados e transicao para o jogo de perimetro."
    else:
        return "3-Point Revolution", "Dominio absoluto do triplo e foco total em eficiencia e espaco."

# Load data 
@st.cache_data
def load_main():
    path = find_csv([
        "dataset_nba_enriched.csv", 
        "dataset_nba.csv",         
        "dataset_consolidado.csv",  
    ])
    if path:
        return pd.read_csv(path, low_memory=False), path.name
    st.error("Ficheiro de dados nao encontrado!")
    st.stop()

@st.cache_data
def load_teams():
    path = find_csv(["team_summaries.csv", "Team Summaries.csv"])
    if path:
        return pd.read_csv(path, low_memory=False)
    return None

df, src = load_main()
teams_df = load_teams()

CP = col_pick(df, ["player"])
CS = col_pick(df, ["season"])
CT = col_pick(df, ["team"])
CPOS = col_pick(df, ["pos"])
CPTS = col_pick(df, ["pts_per_game"])
C3A = col_pick(df, ["x3pa_per_game"])
C3P = col_pick(df, ["x3p_percent"])
CAS = col_pick(df, ["is_allstar"])
CHOF = col_pick(df, ["hof"])
CPER = col_pick(df, ["per"])
CWS = col_pick(df, ["ws"])
CBPM = col_pick(df, ["bpm"])
CTS = col_pick(df, ["ts_percent"])
CUSG = col_pick(df, ["usg_percent"])

# Sidebar 
with st.sidebar:
    st.markdown("### NBA Analytics")
    st.markdown("---")
    st.markdown("**Navegação**")
    st.page_link("Home.py", label="Visão Geral da Liga")
    st.page_link("pages/1_Perfil_Jogador.py", label="Perfil do Jogador")
    st.page_link("pages/2_Comparacao_Jogadores.py", label="Comparação de Jogadores")
    st.page_link("pages/3_Analise_Equipas.py", label="Análise de Equipas")
    st.page_link("pages/4_Rankings.py", label="Rankings & Talentos")
    st.markdown("---")

    if CS:
        s_range = st.slider("Épocas", int(df[CS].min()), int(df[CS].max()), (1947, int(df[CS].max())))
    else:
        s_range = (1947, 2026)

# Guard 
missing = [n for n, c in [("player", CP), ("season", CS), ("pts_per_game", CPTS)] if c is None]
if missing:
    st.error(f"Colunas nao encontradas: **{', '.join(missing)}**")
    st.info(f"Colunas no CSV: `{', '.join(df.columns.tolist())}`")
    st.stop()

# Dataframe filtrado pelo slider 
df_f = df[(df[CS] >= s_range[0]) & (df[CS] <= s_range[1])].copy()

# HEADER
st.markdown('<p class="page-header">VISAO GERAL DA LIGA</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">NBA · Historical Analytics Dashboard · 1947–2026</p>', unsafe_allow_html=True)

# Metrics 
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Jogadores únicos", f"{df_f[CP].nunique():,}")
c2.metric("Épocas cobertas", f"{df_f[CS].nunique()}")
c3.metric("Equipas", f"{df_f[CT].nunique():,}" if CT else "—")
c4.metric("All-Stars", f"{int(df_f[CAS].sum()):,}" if CAS else "—")
c5.metric("Hall of Fame", f"{int(df_f[CHOF].sum()):,}" if CHOF else "—")
st.markdown("---")

# Linha temporal pontuacao 
st.markdown('<div class="section-title">Pontuação Média por Epoca</div>', unsafe_allow_html=True)
avg_pts = df_f.groupby(CS)[CPTS].mean().reset_index()

ERAS = [
    (1947, 1954, "Early Years", "rgba(88,  130, 180, 0.18)", "#5882B4"),
    (1955, 1979, "Pre-3pt Era", "rgba(120, 180, 140, 0.18)", "#78B48C"),
    (1980, 1994, "Golden Era", "rgba(244, 166,  35, 0.22)", "#F4A623"),
    (1995, 2004, "Dead Ball Era", "rgba(200,  80,  80, 0.18)", "#C85050"),
    (2005, 2014, "Hybrid Era", "rgba(150, 100, 200, 0.18)", "#9664C8"),
    (2015, 2026, "3-Point Revolution", "rgba( 30, 200, 180, 0.18)", "#1EC8B4"),
]

fig = go.Figure()
y_max = avg_pts[CPTS].max() * 1.15

for (ano_ini, ano_fim, nome, cor_fill, cor_borda) in ERAS:
    x0 = max(ano_ini, s_range[0])
    x1 = min(ano_fim, s_range[1])
    if x0 >= x1:
        continue
    fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=y_max, fillcolor=cor_fill, line=dict(color=cor_borda, width=0.5, dash="dot"), layer="below",)
    fig.add_annotation(x=(x0 + x1) / 2, y=y_max * 0.02, text=nome, showarrow=False, font=dict(color=cor_borda, size=10, family="Inter"), xanchor="center", yanchor="bottom",)
    
fig.add_trace(go.Scatter(
    x=avg_pts[CS],
    y=avg_pts[CPTS].round(2),
    mode="lines",
    line=dict(color="#F4A623", width=2.5),
    hovertemplate="<b>%{x}</b><br>Media: %{y:.1f} pts/jogo<extra></extra>",
))

eventos = {1980: "Linha 3pts", 1999: "Lockout", 2004: "Novas regras", 2016: "Era Curry/Warriors"}
for ano, label in eventos.items():
    if s_range[0] <= ano <= s_range[1]:
        fig.add_vline(x=ano, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1)
        fig.add_annotation(x=ano, y=avg_pts[CPTS].min() * 0.97, text=label, showarrow=False,
            font=dict(color="rgba(255,255,255,0.4)", size=9),
            textangle=-90, xanchor="right",
        )

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#888", family="Inter"),
    xaxis=dict(showgrid=False, color="#444"),
    yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Pontos/jogo", range=[0, y_max]),
    margin=dict(l=0, r=0, t=30, b=0), height=300, showlegend=False,
)
st.plotly_chart(fig, width="stretch")

# 3 pontos + Top 5
col_l, col_r = st.columns([1.6, 1])

with col_l:
    st.markdown('<div class="section-title">Evolução do Jogo de 3 Pontos</div>', unsafe_allow_html=True)
    if C3A and C3P:
        df_3pts = df_f[df_f[CS] >= 1980]
        fg3 = df_3pts.groupby(CS).agg(a3=(C3A, "mean"), p3=(C3P, "mean")).reset_index()

        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(
            go.Bar(x=fg3[CS], y=fg3["a3"].round(2), name="Tentativas/jogo",
                   marker_color="rgba(244,166,35,0.3)",
                   hovertemplate="<b>%{x}</b><br>Tentativas: %{y:.2f}<extra></extra>"), secondary_y=False)
        fig3.add_trace(
            go.Scatter(x=fg3[CS], y=(fg3["p3"] * 100).round(1), name="% Acerto",
                       line=dict(color="#F4A623", width=2),
                       hovertemplate="<b>%{x}</b><br>Acerto: %{y:.1f}%<extra></extra>"),
            secondary_y=True)
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888", family="Inter"),
            xaxis=dict(showgrid=False, color="#444"),
            yaxis=dict(showgrid=True, gridcolor="#1e1e1e", title="Tentativas/jogo", color="#444"),
            yaxis2=dict(showgrid=False, color="#F4A623", title="% Acerto", ticksuffix="%"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            hoverlabel=dict(bgcolor="#222", font_size=12, font_color="#eee", font_family="Inter"),
            margin=dict(l=0, r=0, t=10, b=0), height=300,
        )
        st.plotly_chart(fig3, width="stretch")
    else:
        st.info("Colunas de 3 pontos nao encontradas no dataset.")

with col_r:
    st.markdown('<div class="section-title">Lideres de Pontuação</div>', unsafe_allow_html=True)
    anos_disponiveis = sorted(df_f[CS].unique(), reverse=True)
    ano_selecionado = st.selectbox("Selecionar Época", anos_disponiveis, label_visibility="collapsed")

    CEFF = col_pick(df, ["scoring_efficiency"])
    CVORP = col_pick(df, ["vorp"])

    opcoes_labels = ["Pontuacao", "Eficiencia", "Impacto (BPM)"]
    opcoes_cols = [CPTS, CEFF, CBPM]
    opcoes_fmt = ["{:.1f} pts", "{:.2f} eff", "{:.1f} BPM"]

    # Filtrar opcoes disponiveis
    opcoes_validas = [
        (l, c, f) for l, c, f in zip(opcoes_labels, opcoes_cols, opcoes_fmt) if c is not None
    ]

    metrica_label = st.radio(
        "Ordenar por",
        [o[0] for o in opcoes_validas],
        horizontal=True,
        label_visibility="collapsed",
    )

    metrica_col, metrica_fmt = next( (c, f) for l, c, f in opcoes_validas if l == metrica_label)

    # Top 5 pela metrica selecionada
    df_ano = df_f[df_f[CS] == ano_selecionado].copy()
    top5 = (df_ano.groupby(CP)[metrica_col].mean().nlargest(5).reset_index())

    for rank, (_, row) in enumerate(top5.iterrows(), 1):
        team_val = ""
        if CT:
            t = df_ano[df_ano[CP] == row[CP]][CT].values
            team_val = t[0] if len(t) > 0 else ""

        valor_fmt = metrica_fmt.format(row[metrica_col])

        st.markdown(f"""
        <div class="player-card">
          <span class="player-rank">#{rank}</span>
          <div>
            <div class="player-name">{row[CP]}</div>
            <div class="player-team">{team_val} · {int(ano_selecionado)}</div>
          </div>
          <span class="player-pts">{valor_fmt}</span>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# KPI Eficiencia vs Media Historica
st.markdown('<div class="section-title">Eficiência da Era vs Média Histórica</div>', unsafe_allow_html=True)
st.caption("Comparação entre a eficiência média do periodo selecionado e a média historica de toda a liga.")

def is_decimal_col(df, col):
    if col is None:
        return False
    med = df[col].dropna().median()
    return med < 2.0

metricas = [
    ("PER", CPER, 15.0, False, "Player Efficiency Rating. Média historica da liga = 15.0 (por definicao)."),
    ("Win Shares", CWS, None, False, "Contributo estimado para as vitórias da equipa."),
    ("True Shoot %", CTS, None, True,  "Eficiência real de lançamento contando 2pts, 3pts e lances livres."),
    ("Usage Rate %", CUSG, None, True,  "Percentagem de posse usada pelo jogador quando em campo."),
]

kpi_cols = st.columns(4)

for i, (label, col, ref_fixo, is_pct, tooltip) in enumerate(metricas):
    if col is None:
        kpi_cols[i].info(f"{label}: coluna nao encontrada")
        continue

    escala = 100.0 if (is_pct and is_decimal_col(df, col)) else 1.0

    media_hist = df[col].mean() * escala
    media_era  = df_f[col].mean() * escala
    ref = ref_fixo if ref_fixo else media_hist
    delta = media_era - ref
    delta_pct  = (delta / ref) * 100 if ref != 0 else 0
    sinal = "▲" if delta >= 0 else "▼"
    cor_delta  = "#10B981" if delta >= 0 else "#EF4444"

    # Formatar valor apresentado
    if is_pct:
        val_era  = f"{media_era:.1f}%"
        val_hist = f"{ref:.1f}%"
    else:
        val_era  = f"{media_era:.1f}"
        val_hist = f"{ref:.1f}"

    kpi_cols[i].markdown(f"""
    <div style="background:#111; border:1px solid #222; border-radius:8px; padding:14px 16px;">
        <div style="color:#888; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">{label}</div>
        <div style="color:#fff; font-size:1.6rem; font-weight:700; line-height:1;">{val_era}</div>
        <div style="margin-top:8px; font-size:0.8rem; color:{cor_delta};">
            {sinal} {abs(delta_pct):.1f}% vs hist. ({val_hist})
        </div>
        <div style="margin-top:4px; font-size:0.7rem; color:#555; font-style:italic;">{tooltip}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Distribuicao por posicao 
if CPOS and CPER:
    st.markdown('<div class="section-title">PER Médio por Posição</div>', unsafe_allow_html=True)
    st.caption("""
        O **PER (Player Efficiency Rating)** é uma métrica de produtividade por minuto criada por John Hollinger. 
        Reune todos os contributos positivos e negativos de um jogador num unico numero. 
        *Nota: A media da liga e fixada historicamente em 15.0.*
    """)

    pos_order = ["PG", "SG", "SF", "PF", "C"]
    df_pos = df_f[df_f[CPOS].isin(pos_order)]
    per_pos = df_pos.groupby(CPOS)[CPER].mean().reindex(pos_order).round(2)
    cores = ["#F4A623", "#3B82F6", "#10B981", "#EF4444", "#A78BFA"]

    fig_pos = go.Figure(go.Bar(
        x=per_pos.index, y=per_pos.values,
        marker_color=cores, text=per_pos.values.round(1),
        textposition="outside", textfont=dict(color="#888"),
        hovertemplate="<b>%{x}</b><br>PER: %{y:.1f}<extra></extra>",
    ))
    fig_pos.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#888", family="Inter"),
        xaxis=dict(showgrid=False, color="#444"),
        yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="PER medio"),
        margin=dict(l=0, r=0, t=30, b=0), height=250, showlegend=False,
    )
    st.plotly_chart(fig_pos, width="stretch")