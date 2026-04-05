import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from utils import apply_theme, find_csv, col_pick, sidebar_nav

# Configuração da Página
st.set_page_config(page_title="Perfil do Jogador · NBA", layout="wide")

apply_theme("perfil")

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "outputs"

# Load
@st.cache_data
def load_main():
    path = find_csv(DATA_DIR, [
        "dataset_nba_enriched.csv",
        "dataset_nba.csv",
        "dataset_consolidado.csv",
    ])
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
CAGE = col_pick(df, ["age"])
CPTS = col_pick(df, ["pts_per_game"])
CAST = col_pick(df, ["ast_per_game"])
CREB = col_pick(df, ["trb_per_game"])
CSTL = col_pick(df, ["stl_per_game"])
CBLK = col_pick(df, ["blk_per_game"])
CTOV = col_pick(df, ["tov_per_game"])
CMPG = col_pick(df, ["mp_per_game"])
CFG = col_pick(df, ["fg_percent"])
C3P = col_pick(df, ["x3p_percent"])
CFT = col_pick(df, ["ft_percent"])
CPER = col_pick(df, ["per"])
CWS = col_pick(df, ["ws"])
CBPM = col_pick(df, ["bpm"])
CVORP = col_pick(df, ["vorp"])
CAS = col_pick(df, ["is_allstar"])
CHOF = col_pick(df, ["hof"])
CHGT = col_pick(df, ["height_cm"])
CWGT = col_pick(df, ["weight_kg"])

# Colunas de draft 
CDRAFT = col_pick(df, ["draft_pick"])
CLOTTERY = col_pick(df, ["is_lottery_pick"])

# Percentagens 
PCT_STATS = ["FG%", "3P%", "FT%"]

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
st.markdown('<p class="page-header">PERFIL DO JOGADOR</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Carreira · Estatísticas · Conquistas</p>', unsafe_allow_html=True)

# Search 
search = st.text_input("Procurar jogador", placeholder="Ex: LeBron James...")
if search:
    matches = [p for p in all_players if search.lower() in p.lower()]
    if not matches:
        st.warning("Nenhum jogador encontrado.")
        st.stop()
else:
    matches = all_players

player = st.selectbox("Selecionar jogador", matches, label_visibility="collapsed")

pdata = df[df[CP] == player].sort_values(CS)
if pdata.empty:
    st.info("Sem dados para este jogador.")
    st.stop()

# Badges
is_as = bool(pdata[CAS].any())  if CAS  else False
is_hof = bool(pdata[CHOF].max() == 1) if CHOF else False

badges = ""
if is_as:  badges += '<span class="badge badge-allstar">All-Star</span>'
if is_hof: badges += '<span class="badge badge-hof">Hall of Fame</span>'
if badges:
    st.markdown(badges, unsafe_allow_html=True)

st.markdown("---")

# Informação de Carreira
st.markdown('<div class="section-title">Informação de Carreira</div>', unsafe_allow_html=True)

career_start = int(pdata[CS].min())
career_end = int(pdata[CS].max())
seasons_n = int(pdata[CS].nunique())
teams = [t for t in pdata[CT].unique() if str(t) not in ["2TM", "3TM"]] if CT else ["—"]
pos_val = pdata[CPOS].mode()[0] if CPOS and not pdata[CPOS].dropna().empty else "—"
height_val = f"{pdata[CHGT].dropna().iloc[0]:.0f} cm" if CHGT and not pdata[CHGT].dropna().empty else "—"
weight_val = f"{pdata[CWGT].dropna().iloc[0]:.0f} kg" if CWGT and not pdata[CWGT].dropna().empty else "—"
allstar_n = int(pdata[CAS].sum()) if CAS else 0

# Info de draft
draft_str = "—"
if CDRAFT is not None:
    draft_pick_val = pdata[CDRAFT].dropna()
    if not draft_pick_val.empty:
        pick = int(draft_pick_val.iloc[0])
        if pick == 99:
            draft_str = "Não draftado"
        else:
            draft_str = f"#{pick}"
            if CLOTTERY is not None and not pdata[CLOTTERY].dropna().empty:
                if bool(pdata[CLOTTERY].dropna().iloc[0]):
                    draft_str += " (Lottery Pick)"

st.markdown(f"""
<div class="info-row">
  <div class="info-item"><label>Posição</label><p>{pos_val}</p></div>
  <div class="info-item"><label>Altura</label><p>{height_val}</p></div>
  <div class="info-item"><label>Peso</label><p>{weight_val}</p></div>
  <div class="info-item"><label>Draft</label><p>{draft_str}</p></div>
  <div class="info-item"><label>Início</label><p>{career_start}</p></div>
  <div class="info-item"><label>Última época</label><p>{career_end}</p></div>
  <div class="info-item"><label>Épocas</label><p>{seasons_n}</p></div>
  <div class="info-item"><label>All-Stars</label><p>{allstar_n}</p></div>
  <div class="info-item"><label>Equipas</label><p>{" · ".join(str(t) for t in teams[:5])}</p></div>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# Métricas base
stat_cols = [
    (CPTS, "PTS"), (CAST, "AST"), (CREB, "REB"),
    (CSTL, "STL"), (CBLK, "BLK"), (CTOV, "TOV"), (CMPG, "MIN"),
]
stat_cols = [(c, l) for c, l in stat_cols if c]

cols = st.columns(len(stat_cols))
for i, (c, l) in enumerate(stat_cols):
    cols[i].metric(l, f"{pdata[c].mean():.1f}")

# Percentagens de lançamento
pct_cols = [(CFG, "FG%"), (C3P, "3P%"), (CFT, "FT%")]
pct_cols = [(c, l) for c, l in pct_cols if c]

if pct_cols:
    st.markdown("**Eficiência de lançamento (médias de carreira)**")
    pct_c = st.columns(len(pct_cols))
    for i, (c, l) in enumerate(pct_cols):
        val = pdata[c].mean()
        if not pd.isna(val) and val < 2.0:
            val = val * 100
        pct_c[i].metric(l, f"{val:.1f}%")

# Métricas avançadas
adv_cols = [(CPER, "PER"), (CWS, "Win Shares"), (CBPM, "BPM"), (CVORP, "VORP")]
adv_cols = [(c, l) for c, l in adv_cols if c]
if adv_cols:
    st.markdown("**Métricas avançadas (médias de carreira)**")
    adv_c = st.columns(len(adv_cols))
    for i, (c, l) in enumerate(adv_cols):
        adv_c[i].metric(l, f"{pdata[c].mean():.2f}")

# Legenda
with st.expander("Legenda das siglas"):
    st.markdown("""
| Sigla | Significado |
|-------|-------------|
| PTS | Pontos por jogo |
| AST | Assistências por jogo |
| REB | Ressaltos por jogo |
| STL | Roubos de bola por jogo |
| BLK | Blocos por jogo |
| TOV | Perdas de bola por jogo |
| MIN | Minutos por jogo |
| FG% | Percentagem de lançamentos de campo |
| 3P% | Percentagem de lançamentos de 3 pontos |
| FT% | Percentagem de lances livres |
| PER | Player Efficiency Rating — eficiência global por minuto (média da liga = 15.0) |
| WS | Win Shares — estimativa de vitórias contribuídas na época |
| BPM | Box Plus/Minus — contribuição por 100 posses vs média da liga |
| VORP | Value Over Replacement Player — valor acima de um jogador de substituição |
""")

st.markdown("---")

# Linha Temporal de Stats
st.markdown('<div class="section-title">Linha Temporal de Stats</div>', unsafe_allow_html=True)
st.caption("As percentagens de lançamento (FG%, 3P%, FT%) usam o eixo direito do gráfico por terem uma escala diferente das restantes estatísticas.")

all_seasons = sorted(pdata[CS].unique())
if len(all_seasons) > 1:
    s_range = st.select_slider(
        "Selecionar épocas:",
        options=all_seasons,
        value=(all_seasons[0], all_seasons[-1]),
    )
    plot_df = pdata[(pdata[CS] >= s_range[0]) & (pdata[CS] <= s_range[1])]
else:
    st.info(f"Época única disponível: {all_seasons[0]}")
    plot_df = pdata

# Mapa completo
all_stat_map = {l: c for c, l in stat_cols}
for c, l in pct_cols:
    all_stat_map[l] = c

sel = st.multiselect(
    "Estatísticas a mostrar:",
    list(all_stat_map.keys()),
    default=[l for _, l in stat_cols[:2]],
)

colors = ["#F4A623", "#3B82F6", "#10B981", "#EF4444", "#A78BFA", "#F97316", "#06B6D4"]

if sel:
    sel_pct = [l for l in sel if l in PCT_STATS]
    sel_volume = [l for l in sel if l not in PCT_STATS]
    use_dual = bool(sel_pct) and bool(sel_volume)

    if use_dual:
        fig_t = make_subplots(specs=[[{"secondary_y": True}]])
    else:
        fig_t = go.Figure()

    for color_idx, lbl in enumerate(sel):
        c   = all_stat_map[lbl]
        col = plot_df[c].copy()

        if lbl in PCT_STATS and col.dropna().median() < 2.0:
            col = col * 100

        trace = go.Scatter(
            x=plot_df[CS],
            y=col.round(2),
            name=lbl,
            mode="lines+markers",
            line=dict(color=colors[color_idx % len(colors)], width=2),
            marker=dict(size=6),
            hovertemplate=f"<b>{lbl}</b>: %{{y:.1f}}<extra></extra>",
        )

        if use_dual:
            fig_t.add_trace(trace, secondary_y=(lbl in PCT_STATS))
        else:
            fig_t.add_trace(trace)

    layout_common = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#888", family="Inter"),
        xaxis=dict(showgrid=False, color="#444", type="category"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#222", font_size=12, font_color="#eee", font_family="Inter"),
        margin=dict(l=0, r=0, t=10, b=0), height=300,
    )

    if use_dual:
        fig_t.update_layout(**layout_common)
        fig_t.update_yaxes(showgrid=True, gridcolor="#1e1e1e", color="#444", title_text="Estatísticas", secondary_y=False,)
        fig_t.update_yaxes(showgrid=False, color="#F4A623", title_text="Percentagem (%)", ticksuffix="%", secondary_y=True,)
    else:
        y_title = "%" if (sel_pct and not sel_volume) else "Valor"
        layout_common["yaxis"] = dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title=y_title)
        fig_t.update_layout(**layout_common)

    st.plotly_chart(fig_t, use_container_width=True)

st.markdown("---")

# Radar + Tabela
col_rad, col_tab = st.columns([1, 1])

with col_rad:
    st.markdown('<div class="section-title">Perfil de Jogo</div>', unsafe_allow_html=True)
    st.caption("Valores normalizados pelo percentil 95 da liga (escala 0–10).")

    radar_cols = [c for c, _ in stat_cols if c != CMPG]
    radar_labels = [l for c, l in stat_cols if c != CMPG]

    league_max = df[radar_cols].quantile(0.95)
    player_avg = pdata[radar_cols].mean()
    norm = ((player_avg / league_max) * 10).clip(0, 10).fillna(0).tolist()

    fig_r = go.Figure(go.Scatterpolar(
        r=norm + [norm[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        fillcolor="rgba(244,166,35,0.15)",
        line=dict(color="#F4A623", width=2),
        marker=dict(size=6),
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
        margin=dict(l=40, r=40, t=40, b=40), height=380,
    )
    st.plotly_chart(fig_r, use_container_width=True)

with col_tab:
    st.markdown('<div class="section-title">Todas as Épocas</div>', unsafe_allow_html=True)

    tab_stat_cols = stat_cols + [(c, l) for c, l in pct_cols]
    display_cols = [CS, CT] + [c for c, _ in tab_stat_cols]
    display_cols = [c for c in display_cols if c and c in pdata.columns]

    rename_map = {
        CS: "Época", CT: "Equipa",
        CPTS: "PTS", CAST: "AST", CREB: "REB",
        CSTL: "STL", CBLK: "BLK", CTOV: "TOV", CMPG: "MIN",
        CFG: "FG%", C3P: "3P%", CFT: "FT%",
    }
    rename_map = {k: v for k, v in rename_map.items() if k}

    tbl = pdata[display_cols].rename(columns=rename_map).set_index("Época").round(3)

    for col_pct in ["FG%", "3P%", "FT%"]:
        if col_pct in tbl.columns and tbl[col_pct].dropna().median() < 2.0:
            tbl[col_pct] = (tbl[col_pct] * 100).round(1)

    st.dataframe(tbl, use_container_width=True, height=380)