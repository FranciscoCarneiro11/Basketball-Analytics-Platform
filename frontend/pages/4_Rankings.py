import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from utils import apply_theme, find_csv, col_pick, sidebar_nav

# Configurações da página 
st.set_page_config(page_title="Rankings & Talentos · NBA", layout="wide")

apply_theme("rankings")

# Paths 
DATA_DIR = Path(__file__).parent.parent.parent / "outputs"

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

# Load 
@st.cache_data
def load_main():
    path = find_csv(["dataset_nba_enriched.csv", "dataset_nba.csv", "dataset_consolidado.csv"])
    if path:
        return pd.read_csv(path, low_memory=False), path.name
    st.error("Dataset não encontrado.")
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
CMPG = col_pick(df, ["mp_per_game"])
CFG = col_pick(df, ["fg_percent"])
CPER = col_pick(df, ["per"])
CWS = col_pick(df, ["ws"])
CBPM = col_pick(df, ["bpm"])
CVORP = col_pick(df, ["vorp"])
CAS = col_pick(df, ["is_allstar"])
CHOF = col_pick(df, ["hof"])
CTIER = col_pick(df, ["player_tier"])
CDRAFT = col_pick(df, ["draft_pick"])
CEXP = col_pick(df, ["experience"])
CHGT = col_pick(df, ["height_cm"])
CWGT = col_pick(df, ["weight_kg"])
CCAREER_AS = col_pick(df, ["career_allstar_count"])
CBEST_MVP = col_pick(df, ["best_mvp_share"])

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

    season_min = int(df[CS].min())
    season_max = int(df[CS].max())
    s_range = st.slider("Épocas", season_min, season_max, (1990, season_max))

    min_games = st.slider("Mínimo de jogos (por época)", 0, 82, 30, step=5)

    if CPOS:
        pos_options = ["Todas"] + sorted(df[CPOS].dropna().unique().tolist())
        pos_filter = st.selectbox("Posição", pos_options)
    else:
        pos_filter = "Todas"

# Filtro base 
df_f = df[(df[CS] >= s_range[0]) & (df[CS] <= s_range[1])].copy()
if "g" in df_f.columns:
    df_f = df_f[df_f["g"] >= min_games]
if pos_filter != "Todas" and CPOS:
    df_f = df_f[df_f[CPOS] == pos_filter]
    
def hex_to_rgba(hex_color, alpha=0.75):
    h = hex_color.lstrip('#').ljust(6, '0')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# Header 
st.markdown('<p class="page-header">RANKINGS & TALENTOS</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Histórico · Médias de carreira · Descoberta de talentos</p>', unsafe_allow_html=True)

# Tabs 
tab1, tab2, tab3, tab4 = st.tabs(["Rankings Históricos", "Melhores da Época", "Descoberta de Talentos", "Distribuição por Tier"])

# Rankings Históricos
with tab1:
    st.markdown('<div class="section-title">Rankings de Carreira</div>', unsafe_allow_html=True)
    st.caption(f"Período: {s_range[0]}–{s_range[1]} · Mínimo {min_games} jogos/época · {pos_filter}")

    # Agregar por jogador
    agg_dict = {}
    if CPTS: agg_dict["PTS"] = (CPTS, "mean")
    if CAST: agg_dict["AST"] = (CAST, "mean")
    if CREB: agg_dict["REB"] = (CREB, "mean")
    if CWS: agg_dict["WS"] = (CWS, "sum")
    if CBPM: agg_dict["BPM"] = (CBPM, "mean")
    if CPER: agg_dict["PER"] = (CPER, "mean")
    if CVORP: agg_dict["VORP"] = (CVORP, "sum")
    if CAS: agg_dict["AllStars"] = (CAS, "sum")
    if CS: agg_dict["Épocas"] = (CS, "nunique")
    if CT: agg_dict["Equipa"] = (CT, "last")
    if CPOS: agg_dict["Pos"] = (CPOS, lambda x: x.mode()[0] if not x.mode().empty else "—")

    career = df_f.groupby(CP).agg(**agg_dict).reset_index()
    career = career[career["Épocas"] >= 3]  # mínimo 3 épocas no período

    # Métrica de ranking seleccionável
    rank_metric_options = {k: k for k in ["PTS","AST","REB","WS","BPM","PER","VORP","AllStars"] if k in career.columns}
    if not rank_metric_options:
        st.warning("Sem métricas disponíveis para ranking.")
    else:
        col_metric, col_n = st.columns([2, 1])
        with col_metric:
            rank_by = st.selectbox("Ordenar por", list(rank_metric_options.keys()), index=0)
        with col_n:
            top_n = st.slider("Top N", 5, 50, 15, step=5)

        top_players = career.nlargest(top_n, rank_by)

        # Gráfico de barras 
        fig_rank = go.Figure(go.Bar(
            y=top_players[CP].tolist()[::-1],
            x=top_players[rank_by].round(2).tolist()[::-1],
            orientation="h",
            marker=dict(
                color=top_players[rank_by].tolist()[::-1],
                colorscale=[[0, "#1a1a1a"], [1, "#F4A623"]],
                showscale=False,
            ),
            text=[f"{v:.1f}" for v in top_players[rank_by].round(1).tolist()[::-1]],
            textposition="outside",
            textfont=dict(color="#888", size=10),
            hovertemplate="<b>%{y}</b><br>" + rank_by + ": %{x:.1f}<extra></extra>",
        ))
        fig_rank.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888", family="Inter"),
            xaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444"),
            yaxis=dict(showgrid=False, color="#ccc", tickfont=dict(size=11)),
            margin=dict(l=0, r=60, t=10, b=0),
            height=max(300, top_n * 28),
        )
        st.plotly_chart(fig_rank, use_container_width=True)
        
        st.caption("Nota: comparações de pontuação entre eras diferentes devem ter em conta o ritmo de jogo de cada época. Jogadores modernos beneficiam de um pace mais elevado — métricas como BPM, PER e Win Shares são mais justas para comparações históricas.")

        # Cards dos top 5
        st.markdown('<div class="section-title">Top 5 Detalhado</div>', unsafe_allow_html=True)
        top5 = career.nlargest(5, rank_by).reset_index(drop=True)
        for i, row in top5.iterrows():
            pos_txt = f" · {row['Pos']}" if "Pos" in row and pd.notna(row.get("Pos")) else ""
            team_txt = f" · {row['Equipa']}" if "Equipa" in row and pd.notna(row.get("Equipa")) else ""
            epochs_txt = f"{int(row['Épocas'])} épocas" if "Épocas" in row else ""
            pts_txt = f" · {row['PTS']:.1f} PPG" if "PTS" in row else ""
            ws_txt = f" · {row['WS']:.0f} WS" if "WS" in row else ""
            st.markdown(f"""
            <div class="rank-card">
              <span class="rank-num">#{i+1}</span>
              <div>
                <div class="rank-name">{row[CP]}</div>
                <div class="rank-sub">{epochs_txt}{pos_txt}{team_txt}{pts_txt}{ws_txt}</div>
              </div>
              <span class="rank-val">{row[rank_by]:.1f} {rank_by}</span>
            </div>""", unsafe_allow_html=True)

        # Tabela completa
        with st.expander("Tabela completa"):
            show_c = [CP] + [c for c in ["PTS","AST","REB","WS","BPM","PER","VORP","AllStars","Épocas","Pos","Equipa"] if c in career.columns]
            st.dataframe(
                career.nlargest(100, rank_by)[show_c].reset_index(drop=True).round(2),
                use_container_width=True, height=400
            )

# Melhores da Época
with tab2:
    st.markdown('<div class="section-title">Melhores Jogadores de uma Época</div>', unsafe_allow_html=True)

    epoch_sel = st.selectbox("Selecionar época", sorted(df[CS].unique(), reverse=True), key="epoch_tab2")

    epoch_df = df[df[CS] == epoch_sel].copy()
    
    if CT in epoch_df.columns:
        multi = epoch_df[epoch_df[CT].isin(["2TM", "3TM"])]
        single = epoch_df[~epoch_df[CP].isin(multi[CP])]
        epoch_df = pd.concat([single, multi]).drop_duplicates(subset=[CP])
    if "g" in epoch_df.columns:
        epoch_df = epoch_df[epoch_df["g"] >= 20]
    if pos_filter != "Todas" and CPOS:
        epoch_df = epoch_df[epoch_df[CPOS] == pos_filter]

    if epoch_df.empty:
        st.warning("Sem dados para esta época com os filtros seleccionados.")
    else:
        stat_options2 = {l: c for l, c in [
            ("Pontos/jogo", CPTS), ("Assistências/jogo", CAST), ("Ressaltos/jogo", CREB),
            ("Roubos/jogo", CSTL), ("Blocos/jogo", CBLK), ("PER", CPER),
            ("Win Shares", CWS), ("BPM", CBPM), ("VORP", CVORP),
        ] if c}

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            stat_lbl = st.selectbox("Estatística", list(stat_options2.keys()), key="stat_ep")
        with col_s2:
            top_n2 = st.slider("Top N", 5, 30, 10, key="topn_ep")
        with col_s3:
            st.markdown("&nbsp;")

        stat_col2 = stat_options2[stat_lbl]
        top_epoch = epoch_df.nlargest(top_n2, stat_col2)[[CP, CPOS, CT, stat_col2] + 
                    [c for c in [CPTS, CPER, CWS] if c and c != stat_col2]]
        top_epoch = top_epoch.dropna(subset=[stat_col2])

        # Barras
        fig_ep = go.Figure(go.Bar(
            y=top_epoch[CP].tolist()[::-1],
            x=top_epoch[stat_col2].round(2).tolist()[::-1],
            orientation="h",
            marker=dict(color="#F4A623", opacity=0.8),
            text=[f"{v:.1f}" for v in top_epoch[stat_col2].round(1).tolist()[::-1]],
            textposition="auto",
            textfont=dict(color="#888", size=10),
            hovertemplate="<b>%{y}</b><br>" + stat_lbl + ": %{x:.1f}<extra></extra>",
        ))
        fig_ep.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888", family="Inter"),
            xaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444"),
            yaxis=dict(showgrid=False, color="#ccc"),
            margin=dict(l=0, r=60, t=10, b=0),
            height=max(280, top_n2 * 28),
        )
        st.plotly_chart(fig_ep, use_container_width=True)

        # Tabela 
        st.markdown(f"**Detalhes — Top {top_n2} em {stat_lbl} ({epoch_sel})**")
        rename_ep = {CP:"Jogador", CPOS:"Pos", CT:"Equipa", CPTS:"PTS", CPER:"PER", CWS:"WS"}
        disp_cols = [c for c in [CP, CPOS, CT, stat_col2] +
                     [c2 for c2 in [CPTS, CPER, CWS] if c2 and c2 != stat_col2]
                     if c and c in top_epoch.columns]
        tbl_ep = top_epoch[disp_cols].rename(columns=rename_ep).reset_index(drop=True).round(2)
        tbl_ep.index = tbl_ep.index + 1
        st.dataframe(tbl_ep, use_container_width=True, height=340)

# Descoberta de Talentos
with tab3:
    st.markdown('<div class="section-title">Filtro de Talentos</div>', unsafe_allow_html=True)
    st.caption("Encontra jogadores que satisfazem múltiplos critérios em simultâneo.")

    # Filtros customizáveis
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        min_pts = st.number_input("Mínimo PTS/jogo", 0.0, 50.0, 15.0, step=0.5) if CPTS else 0.0
    with col_f2:
        min_ast = st.number_input("Mínimo AST/jogo", 0.0, 20.0, 0.0, step=0.5) if CAST else 0.0
    with col_f3:
        min_per = st.number_input("Mínimo PER", 0.0, 40.0, 15.0, step=0.5) if CPER else 0.0
    with col_f4:
        min_bpm = st.number_input("Mínimo BPM", -10.0, 20.0, 0.0, step=0.5) if CBPM else -10.0

    col_f5, col_f6, col_f7, col_f8 = st.columns(4)
    with col_f5:
        max_age = st.number_input("Máximo de idade", 18, 45, 28) if CAGE else 45
    with col_f6:
        only_as = st.checkbox("Apenas All-Stars") if CAS else False
    with col_f7:
        min_ws = st.number_input("Mínimo Win Shares", 0.0, 25.0, 0.0, step=0.5) if CWS else 0.0
    with col_f8:
        min_mpg = st.number_input("Mínimo MIN/jogo", 0.0, 48.0, 20.0, step=1.0) if CMPG else 0.0

    talent_df = df_f.copy()
    if CPTS: talent_df = talent_df[talent_df[CPTS]  >= min_pts]
    if CAST: talent_df = talent_df[talent_df[CAST]  >= min_ast]
    if CPER: talent_df = talent_df[talent_df[CPER]  >= min_per]
    if CBPM: talent_df = talent_df[talent_df[CBPM]  >= min_bpm]
    if CAGE: talent_df = talent_df[talent_df[CAGE]  <= max_age]
    if CWS: talent_df = talent_df[talent_df[CWS]   >= min_ws]
    if CMPG: talent_df = talent_df[talent_df[CMPG]  >= min_mpg]
    if only_as and CAS:
        talent_df = talent_df[talent_df[CAS].astype(bool)]

    st.markdown(f"**{talent_df[CP].nunique() if CP else 0} jogadores únicos encontrados** ({len(talent_df):,} registos no período selecionado)")

    if not talent_df.empty:
        # Scatter pts vs bpm
        if CPTS and CBPM:
            st.markdown('<div class="section-title">Scatter: Pontuação vs BPM</div>', unsafe_allow_html=True)

            scatter_data = talent_df.dropna(subset=[CPTS, CBPM])
            fig_sc = go.Figure(go.Scatter(
                x=scatter_data[CPTS],
                y=scatter_data[CBPM],
                mode="markers",
                text=scatter_data[CP] + " (" + scatter_data[CS].astype(str) + ")",
                marker=dict(
                    size=8,
                    color=scatter_data[CPER] if CPER else "#F4A623",
                    colorscale="YlOrRd",
                    showscale=True,
                    colorbar=dict(title="PER", tickfont=dict(color="#888")),
                    opacity=0.75,
                    line=dict(color="#111", width=0.5)
                ),
                hovertemplate="<b>%{text}</b><br>PTS: %{x:.1f}<br>BPM: %{y:.1f}<extra></extra>",
            ))
            fig_sc.add_hline(y=0, line_dash="dash", line_color="#333", line_width=1)
            fig_sc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888", family="Inter"),
                xaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Pontos/jogo"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="BPM"),
                margin=dict(l=0, r=0, t=20, b=0), height=420,
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        # Tabela de resultados
        st.markdown('<div class="section-title">Resultados</div>', unsafe_allow_html=True)
        disp_c = [c for c in [CP, CS, CT, CPOS, CAGE, CPTS, CAST, CREB, CSTL, CBLK, CPER, CWS, CBPM] if c]
        rename_t = {CP:"Jogador", CS:"Época", CT:"Equipa", CPOS:"Pos", CAGE:"Idade",
                    CPTS:"PTS", CAST:"AST", CREB:"REB", CSTL:"STL", CBLK:"BLK",
                    CPER:"PER", CWS:"WS", CBPM:"BPM"}
        sort_by_t = "PTS" if "PTS" in [rename_t.get(c) for c in disp_c] else disp_c[0]
        tbl_talent = talent_df[disp_c].rename(columns=rename_t)\
            .sort_values(sort_by_t, ascending=False)\
            .reset_index(drop=True).round(2)
        tbl_talent.index = tbl_talent.index + 1
        st.dataframe(tbl_talent, use_container_width=True, height=420)

# Distribuição por Tier
with tab4:
    st.markdown('<div class="section-title">Distribuição por Tier de Jogador</div>', unsafe_allow_html=True)

    if CTIER:
        tier_order  = ["Star", "Starter", "Rotation", "Bench", "Fringe"]
        tier_colors = {"Star":"#F4A623", "Starter":"#3B82F6", "Rotation":"#10B981", "Bench":"#888", "Fringe":"#444"}

        tier_df = df_f[df_f[CTIER].isin(tier_order)].copy()

        if tier_df.empty:
            st.warning("Sem dados no intervalo seleccionado.")
        else:
            # Contagem por tier
            tier_counts = tier_df[CTIER].value_counts().reindex(tier_order, fill_value=0)

            col_pie, col_bar = st.columns([1, 1.5])
            with col_pie:
                fig_pie = go.Figure(go.Pie(
                    labels=tier_order,
                    values=tier_counts.values,
                    marker_colors=[tier_colors[t] for t in tier_order],
                    hole=0.5,
                    textinfo="label+percent",
                    textfont=dict(size=11),
                    hovertemplate="<b>%{label}</b><br>%{value:,} épocas (%{percent})<extra></extra>",
                ))
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#888", family="Inter"),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=0, r=0, t=20, b=0), height=320,
                    showlegend=False,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_bar:
                # Média de pts por tier
                pts_by_tier = tier_df.groupby(CTIER)[CPTS].mean().reindex(tier_order) if CPTS else None
                per_by_tier = tier_df.groupby(CTIER)[CPER].mean().reindex(tier_order) if CPER else None

                if pts_by_tier is not None:
                    fig_tier = go.Figure()
                    fig_tier.add_trace(go.Bar(
                        x=tier_order,
                        y=pts_by_tier.values.round(1),
                        name="PTS/jogo",
                        marker_color=[tier_colors[t] for t in tier_order],
                        opacity=0.85,
                        text=[f"{v:.1f}" for v in pts_by_tier.values.round(1)],
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>PTS: %{y:.1f}<extra></extra>",
                    ))
                    if per_by_tier is not None:
                        fig_tier.add_trace(go.Scatter(
                            x=tier_order, y=per_by_tier.values.round(1),
                            name="PER médio", yaxis="y2",
                            mode="lines+markers",
                            line=dict(color="#fff", width=1.5, dash="dot"),
                            marker=dict(size=7),
                        ))
                    fig_tier.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#888", family="Inter"),
                        xaxis=dict(showgrid=False, color="#444"),
                        yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="PTS/jogo"),
                        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                    color="#888", title="PER"),
                        legend=dict(bgcolor="rgba(0,0,0,0)"),
                        margin=dict(l=0, r=40, t=10, b=0), height=320,
                    )
                    st.plotly_chart(fig_tier, use_container_width=True)

            st.markdown("---")

            # Evolução dos tiers ao longo do tempo
            st.markdown('<div class="section-title">Evolução dos Tiers por Época</div>', unsafe_allow_html=True)

            tier_by_season = (
                tier_df.groupby([CS, CTIER]).size()
                .unstack(fill_value=0)
                .reindex(columns=[t for t in tier_order if t in tier_df[CTIER].unique()], fill_value=0)
            )

            fig_stack = go.Figure()
            for tier in tier_order:
                if tier not in tier_by_season.columns:
                    continue
                fig_stack.add_trace(go.Scatter(
                    x=tier_by_season.index,
                    y=tier_by_season[tier],
                    name=tier,
                    stackgroup="one",
                    mode="none",
                    fillcolor=hex_to_rgba(tier_colors[tier]),
                    hovertemplate=f"<b>{tier}</b> %{{x}}: %{{y}} jogadores<extra></extra>",
                ))
            fig_stack.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888", family="Inter"),
                xaxis=dict(showgrid=False, color="#444"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Nº de jogadores"),
                legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                            x=0.5, xanchor="center", y=-0.12),
                margin=dict(l=0, r=0, t=10, b=60), height=320,
            )
            st.plotly_chart(fig_stack, use_container_width=True)

            # Taxa de All-Star por tier
            if CAS:
                st.markdown('<div class="section-title">Taxa de All-Star por Tier</div>', unsafe_allow_html=True)
                as_rate = tier_df.groupby(CTIER)[CAS].apply(
                    lambda x: pd.to_numeric(x, errors="coerce").mean() * 100
                ).reindex(tier_order).fillna(0)

                fig_as = go.Figure(go.Bar(
                    x=tier_order, y=as_rate.values.round(1),
                    marker_color=[tier_colors[t] for t in tier_order],
                    opacity=0.85,
                    text=[f"{v:.1f}%" for v in as_rate.values.round(1)],
                    textposition="outside",
                    hovertemplate="<b>%{x}</b><br>%{y:.1f}% All-Stars<extra></extra>",
                ))
                fig_as.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#888", family="Inter"),
                    xaxis=dict(showgrid=False, color="#444"),
                    yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444",
                               title="% All-Star", ticksuffix="%"),
                    margin=dict(l=0, r=0, t=30, b=0), height=280,
                    showlegend=False,
                )
                st.plotly_chart(fig_as, use_container_width=True)

    else:
        if CPER and CP:
            st.markdown("**Distribuição do PER — todos os jogadores no período seleccionado**")
            per_data = df_f[CPER].dropna()
            fig_hist = go.Figure(go.Histogram(
                x=per_data, nbinsx=60,
                marker_color="#F4A623", opacity=0.75,
                hovertemplate="PER: %{x:.1f}<br>Contagem: %{y}<extra></extra>",
            ))
            fig_hist.add_vline(x=15, line_dash="dash", line_color="#888", annotation_text="Média liga (15)", annotation_font_color="#666")
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888", family="Inter"),
                xaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="PER"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Frequência"),
                margin=dict(l=0, r=0, t=20, b=0), height=320,
            )
            st.plotly_chart(fig_hist, use_container_width=True)