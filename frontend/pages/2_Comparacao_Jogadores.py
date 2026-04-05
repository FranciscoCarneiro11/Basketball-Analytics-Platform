import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from utils import apply_theme, find_csv, col_pick, sidebar_nav

# Configuração da Página
st.set_page_config(page_title="Comparação · NBA", layout="wide")

apply_theme("comparacao")

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "outputs"

def safe_year_slider(player_name, df_player, cs_col, key):
    if not df_player.empty:
        min_y = int(df_player[cs_col].min())
        max_y = int(df_player[cs_col].max())
        if min_y < max_y:
            return st.slider(f"Épocas — {player_name}", min_y, max_y, (min_y, max_y), key=key)
        else:
            st.info(f"{player_name}: Dados apenas de {min_y}")
            return (min_y, min_y)
    return (1947, 2026)

# Load
@st.cache_data
def load_main():
    path = find_csv(DATA_DIR, ["dataset_nba_enriched.csv","dataset_nba.csv","dataset_consolidado.csv",])
    if path:
        return pd.read_csv(path, low_memory=False), path.name
    st.error("Ficheiro de dados não encontrado em outputs/")
    st.stop()

df, src = load_main()

# Colunas
CP = col_pick(df, ["player"])
CS = col_pick(df, ["season"])
CT = col_pick(df, ["team"])
CPOS = col_pick(df, ["pos"])
CPTS = col_pick(df, ["pts_per_game"])
CAST = col_pick(df, ["ast_per_game"])
CREB = col_pick(df, ["trb_per_game"])
CSTL = col_pick(df, ["stl_per_game"])
CBLK = col_pick(df, ["blk_per_game"])
CTOV = col_pick(df, ["tov_per_game"])
CFG = col_pick(df, ["fg_percent"])
C3P = col_pick(df, ["x3p_percent"])
CFT = col_pick(df, ["ft_percent"])
CPER = col_pick(df, ["per"])
CWS = col_pick(df, ["ws"])
CBPM = col_pick(df, ["bpm"])
CVORP = col_pick(df, ["vorp"])
CAS = col_pick(df, ["is_allstar"])
CHOF = col_pick(df, ["hof"])

# Métrica onde menor é melhor
LOWER_IS_BETTER = {"TOV"}

all_players = sorted(df[CP].dropna().unique()) if CP else []

# Sidebar
with st.sidebar:
    st.markdown("### NBA Analytics")
    st.markdown("---")
    st.page_link("Home.py", label="Visão Geral da Liga")
    st.page_link("pages/1_Perfil_Jogador.py", label="Perfil do Jogador")
    st.page_link("pages/2_Comparacao_Jogadores.py", label="Comparação de Jogadores")
    st.page_link("pages/3_Analise_Equipas.py", label="Análise de Equipas")
    st.page_link("pages/4_Rankings.py", label="Rankings & Talentos")
    st.markdown("---")

if not CP or not CS:
    st.error("Colunas não encontradas.")
    st.stop()

# Header
st.markdown('<p class="page-header">COMPARAÇÃO DE JOGADORES</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Head-to-Head · Médias de carreira ou por período</p>', unsafe_allow_html=True)

# Seleção de jogadores
ca, cvs, cb = st.columns([2, 0.5, 2])
with ca:
    sa = st.text_input("Jogador A", placeholder="Nome...", key="sa")
    matches_a = [p for p in all_players if sa.lower() in p.lower()] if sa else all_players
    player_a = st.selectbox("Selecione Jogador A", matches_a, key="pa", label_visibility="collapsed")
with cvs:
    st.markdown('<div class="vs" style="margin-top:48px">VS</div>', unsafe_allow_html=True)
with cb:
    sb = st.text_input("Jogador B", placeholder="Nome...", key="sb")
    matches_b = [p for p in all_players if sb.lower() in p.lower()] if sb else all_players
    idx_b = min(1, len(matches_b) - 1)
    player_b  = st.selectbox("Selecione Jogador B", matches_b, index=idx_b, key="pb", label_visibility="collapsed")

st.markdown("---")

# Filtros de época independentes
da_full = df[df[CP] == player_a]
db_full = df[df[CP] == player_b]

cf1, cf2 = st.columns(2)
with cf1:
    ra = safe_year_slider(player_a, da_full, CS, "ra")
with cf2:
    rb = safe_year_slider(player_b, db_full, CS, "rb")

da = da_full[(da_full[CS] >= ra[0]) & (da_full[CS] <= ra[1])]
db = db_full[(db_full[CS] >= rb[0]) & (db_full[CS] <= rb[1])]

# Definição das métricas
METRICS = [
    ("PTS", CPTS, "Estatísticas Base", False),
    ("AST", CAST, "Estatísticas Base", False),
    ("REB", CREB, "Estatísticas Base", False),
    ("STL", CSTL, "Estatísticas Base", False),
    ("BLK", CBLK, "Estatísticas Base", False),
    ("TOV", CTOV, "Estatísticas Base", False),
    ("FG%", CFG, "Eficiência", True),
    ("3P%", C3P, "Eficiência", True),
    ("FT%", CFT, "Eficiência", True),
    ("PER", CPER, "Métricas Avançadas", False),
    ("Win Shares", CWS, "Métricas Avançadas", False),
    ("BPM", CBPM, "Métricas Avançadas", False),
    ("VORP", CVORP, "Métricas Avançadas", False),
]
METRICS = [(l, c, g, p) for l, c, g, p in METRICS if c and c in df.columns]

# Calcular médias
def safe_mean(data, col):
    if col and col in data.columns:
        return data[col].mean()
    return np.nan

avga = {l: safe_mean(da, c) for l, c, _, _ in METRICS}
avgb = {l: safe_mean(db, c) for l, c, _, _ in METRICS}

# Formatar valor para apresentação
def fmt_val(val, is_pct):
    if pd.isna(val):
        return "—"
    if is_pct:
        display = val * 100 if val < 2.0 else val
        return f"{display:.1f}%"
    return f"{val:+.1f}" if val < 0 else f"{val:.1f}"

# Tabela comparativa 
st.markdown('<div class="section-title">Comparação Estatística</div>', unsafe_allow_html=True)
st.caption("O valor colorido indica o melhor resultado em cada categoria. Em Turnovers (TOV) menor é melhor.")

for group in ["Estatísticas Base", "Eficiência", "Métricas Avançadas"]:
    group_metrics = [(l, c, p) for l, c, g, p in METRICS if g == group]
    if not group_metrics:
        continue

    st.markdown(f"**{group}**")

    rows = []
    for lbl, col, is_pct in group_metrics:
        va = avga[lbl]
        vb = avgb[lbl]

        va_fmt = fmt_val(va, is_pct)
        vb_fmt = fmt_val(vb, is_pct)

        # Determinar vencedor
        winner = None
        if not pd.isna(va) and not pd.isna(vb) and va != vb:
            winner = "A" if (va < vb if lbl in LOWER_IS_BETTER else va > vb) else "B"
        
        indicator  = "◀" if winner == "A" else ("▶" if winner == "B" else "=")

        rows.append({"Métrica": lbl,player_a[:22]: va_fmt," ": indicator,player_b[:22]: vb_fmt, "winner": winner })

        # Negrito no vencedor, indicador central
        va_display = f"**{va_fmt}**" if winner == "A" else va_fmt
        vb_display = f"**{vb_fmt}**" if winner == "B" else vb_fmt

    df_display = pd.DataFrame(rows)
    
    col_a = player_a[:22]
    col_b = player_b[:22]

    def aplicar_estilo(row):
        estilos = ['', '', '', '', '']
        if row['winner'] == 'A':
            estilos[1] = 'color: #10B981; font-weight: bold; background-color: rgba(16, 185, 129, 0.05);'
        elif row['winner'] == 'B':
            estilos[3] = 'color: #10B981; font-weight: bold; background-color: rgba(16, 185, 129, 0.05);'
        return estilos

    st.dataframe(
        df_display.style.apply(aplicar_estilo, axis=1),
        column_config={
            "winner": None,  
            "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
            " ": st.column_config.TextColumn(" ", width="small")
        },
        use_container_width=True,
        hide_index=True, 
        height=35 * len(rows) + 38
    )

st.markdown("---")

# Mapa simplificado para gráficos
stat_map = {l: c for l, c, _, _ in METRICS}

# Radar + Barras 
cr, cb2 = st.columns([1.2, 1])

with cr:
    st.markdown('<div class="section-title">Radar Comparativo</div>', unsafe_allow_html=True)
    st.caption("Valores normalizados pelo percentil 95 da liga (escala 0–10).")

    radar_stats = ["PTS", "AST", "REB", "STL", "BLK"]
    radar_cols = [stat_map[l] for l in radar_stats if l in stat_map]
    radar_labels = [l for l in radar_stats if l in stat_map]

    league_ref = df[radar_cols].quantile(0.95)
    avga_s = pd.Series({c: avga[l] for l, c in zip(radar_labels, radar_cols)})
    avgb_s = pd.Series({c: avgb[l] for l, c in zip(radar_labels, radar_cols)})
    norm_a = ((avga_s[radar_cols] / league_ref) * 10).clip(0, 10).fillna(0).tolist()
    norm_b = ((avgb_s[radar_cols] / league_ref) * 10).clip(0, 10).fillna(0).tolist()

    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=norm_a + [norm_a[0]], theta=radar_labels + [radar_labels[0]],
        name=player_a, fill="toself",
        fillcolor="rgba(244,166,35,0.12)",
        line=dict(color="#F4A623", width=2),
        hovertemplate="<b>%{theta}</b>: %{r:.1f}/10<extra></extra>",
    ))
    fig_r.add_trace(go.Scatterpolar(
        r=norm_b + [norm_b[0]], theta=radar_labels + [radar_labels[0]],
        name=player_b, fill="toself",
        fillcolor="rgba(59,130,246,0.12)",
        line=dict(color="#3B82F6", width=2),
        hovertemplate="<b>%{theta}</b>: %{r:.1f}/10<extra></extra>",
    ))
    fig_r.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 10], color="#444", gridcolor="#1e1e1e"),
            angularaxis=dict(color="#888"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#888", family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                    x=0.5, xanchor="center", y=-0.12),
        margin=dict(l=40, r=40, t=40, b=60), height=420,
    )
    st.plotly_chart(fig_r, use_container_width=True)

with cb2:
    st.markdown('<div class="section-title">Barras Comparativas</div>', unsafe_allow_html=True)
    st.caption(f"Direita: {player_a} · Esquerda: {player_b}")

    bar_stats = ["PTS", "AST", "REB", "STL", "BLK"]
    bar_items = [(l, stat_map[l]) for l in bar_stats if l in stat_map]
    bar_labels = [l for l, _ in bar_items]
    vals_a = [float(avga.get(l, 0) or 0) for l, _ in bar_items]
    vals_b = [float(avgb.get(l, 0) or 0) for l, _ in bar_items]

    fig_b = go.Figure()
    fig_b.add_trace(go.Bar(
        y=bar_labels, x=vals_a, name=player_a,
        orientation="h", marker_color="#F4A623",
        text=[f"{v:.1f}" for v in vals_a], textposition="outside",
        hovertemplate="%{x:.1f}<extra></extra>",
    ))
    fig_b.add_trace(go.Bar(
        y=bar_labels, x=[-v for v in vals_b], name=player_b,
        orientation="h", marker_color="#3B82F6",
        text=[f"{v:.1f}" for v in vals_b], textposition="outside",
        customdata=vals_b,
        hovertemplate="%{customdata:.1f}<extra></extra>",
    ))
    fig_b.update_layout(
        barmode="relative",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#888", family="Inter"),
        xaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444",zeroline=True, zerolinecolor="#555"),
        yaxis=dict(showgrid=False, color="#999"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",x=0.5, xanchor="center", y=-0.15),
        margin=dict(l=0, r=0, t=10, b=60), height=380,
)
    st.plotly_chart(fig_b, use_container_width=True)

st.markdown("---")

# Evolução temporal comparativa 
st.markdown('<div class="section-title">Evolução ao Longo da Carreira</div>', unsafe_allow_html=True)
st.caption("Seleciona a estatística para comparar a evolução temporal de ambos os jogadores.")

evo_options = {l: (c, p) for l, c, _, p in METRICS}
evo_label = st.selectbox("Estatística", list(evo_options.keys()), key="evo_stat")
evo_col, is_pct_evo = evo_options[evo_label]

def prep_series(data, col, is_pct):
    s = data[col].copy()
    if is_pct and s.dropna().median() < 2.0:
        s = s * 100
    return s.round(2)

fig_ev = go.Figure()
fig_ev.add_trace(go.Scatter(
    x=da[CS],
    y=prep_series(da, evo_col, is_pct_evo),
    name=player_a,
    mode="lines+markers",
    line=dict(color="#F4A623", width=2),
    marker=dict(size=6),
    hovertemplate=f"<b>{player_a}</b> %{{x}}: %{{y:.1f}}<extra></extra>",
))
fig_ev.add_trace(go.Scatter(
    x=db[CS],
    y=prep_series(db, evo_col, is_pct_evo),
    name=player_b,
    mode="lines+markers",
    line=dict(color="#3B82F6", width=2),
    marker=dict(size=6),
    hovertemplate=f"<b>{player_b}</b> %{{x}}: %{{y:.1f}}<extra></extra>",
))

y_title = f"{evo_label} (%)" if is_pct_evo else evo_label
fig_ev.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#888", family="Inter"),
    xaxis=dict(showgrid=False, color="#444", type="category"),
    yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title=y_title),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#222", font_size=12, font_color="#eee", font_family="Inter"),
    margin=dict(l=0, r=0, t=10, b=0), height=280,
)
st.plotly_chart(fig_ev, use_container_width=True)