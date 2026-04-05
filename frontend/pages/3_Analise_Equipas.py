import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
from utils import apply_theme, find_csv, col_pick, sidebar_nav

# Configurações da página 
st.set_page_config(page_title="Análise de Equipas · NBA", layout="wide")

apply_theme("equipas")

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
def load_teams():
    path = find_csv(["team_summaries.csv", "Team Summaries.csv"])
    if path:
        df = pd.read_csv(path, low_memory=False)
        # Filtrar só NBA
        if "lg" in df.columns:
            df = df[df["lg"] == "NBA"]
        return df, path.name
    return None, None

@st.cache_data
def load_players():
    path = find_csv(["dataset_nba.csv", "dataset_consolidado.csv"])
    if path:
        return pd.read_csv(path, low_memory=False)
    return None

teams_df, src = load_teams()
players_df    = load_players()

if teams_df is None:
    st.error("CSV não encontrado.")
    st.stop()

# Colunas
CT = col_pick(teams_df, ["team", "abbreviation"])
CS = col_pick(teams_df, ["season"])
CW = col_pick(teams_df, ["w"])
CL = col_pick(teams_df, ["l"])
CORT = col_pick(teams_df, ["o_rtg"])
CDRT = col_pick(teams_df, ["d_rtg"])
CNRT = col_pick(teams_df, ["n_rtg"])
CPAC = col_pick(teams_df, ["pace"])
CPLO = col_pick(teams_df, ["playoffs"])
CSRS = col_pick(teams_df, ["srs"])
CATT = col_pick(teams_df, ["attend_g"])

if not CT or not CS:
    st.error("Colunas não encontradas.")
    st.stop()

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

    all_teams = sorted(teams_df[CT].dropna().unique())
    team_sel  = st.selectbox("Equipa", all_teams, index=all_teams.index("LAL") if "LAL" in all_teams else 0)

    season_min = int(teams_df[CS].min())
    season_max = int(teams_df[CS].max())
    s_range = st.slider("Épocas", season_min, season_max, (1990, season_max))

    st.markdown("---")

# Header 
st.markdown('<p class="page-header">ANÁLISE DE EQUIPAS</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Histórico · Performance · Comparação entre Franquias</p>', unsafe_allow_html=True)

# Tabs 
tab1, tab2, tab3 = st.tabs(["Perfil da Equipa", "Comparação de Equipas", "Liga por Época"])

# Perfil da Equipa
with tab1:
    tdata = teams_df[ (teams_df[CT] == team_sel) & (teams_df[CS] >= s_range[0]) & (teams_df[CS] <= s_range[1])].sort_values(CS)

    if tdata.empty:
        st.warning(f"Sem dados para {team_sel} no intervalo seleccionado.")
    else:
        # Metrics 
        total_seasons = len(tdata)
        total_wins = int(tdata[CW].sum()) if CW else 0
        total_losses = int(tdata[CL].sum()) if CL else 0
        win_pct = total_wins / max(total_wins + total_losses, 1)
        playoff_pct = tdata[CPLO].mean() * 100 if CPLO else 0
        best_nrtg = tdata[CNRT].max() if CNRT else None
        avg_pace = tdata[CPAC].mean() if CPAC else None

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Épocas", total_seasons)
        c2.metric("Vitórias", f"{total_wins:,}")
        c3.metric("Win %", f"{win_pct:.1%}")
        c4.metric("Playoffs %", f"{playoff_pct:.0f}%")
        if best_nrtg is not None:
            c5.metric("Melhor Net RTG", f"{best_nrtg:+.1f}")

        st.markdown("---")

        # Win/Loss por época 
        st.markdown('<div class="section-title">Vitórias & Derrotas por Época</div>', unsafe_allow_html=True)

        if CW and CL:
            fig_wl = go.Figure()
            fig_wl.add_trace(go.Bar(
                x=tdata[CS], y=tdata[CW], name="Vitórias",
                marker_color="#10B981", opacity=0.85,
                hovertemplate="<b>%{x}</b><br>Vitórias: %{y}<extra></extra>",
            ))
            fig_wl.add_trace(go.Bar(
                x=tdata[CS], y=tdata[CL], name="Derrotas",
                marker_color="#EF4444", opacity=0.7,
                hovertemplate="<b>%{x}</b><br>Derrotas: %{y}<extra></extra>",
            ))
            
            # Marcar épocas de playoffs
            if CPLO:
                playoff_seasons = tdata[tdata[CPLO] == True][CS].tolist()
                for s in playoff_seasons:
                    fig_wl.add_vline(x=s, line_color="rgba(244,166,35,0.15)", line_width=8)

            fig_wl.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888", family="Inter"),
                xaxis=dict(showgrid=False, color="#444"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=10, b=0), height=280,
                annotations=[dict(
                    text="Fundo dourado = época de playoffs",
                    x=0.01, y=0.98, xref="paper", yref="paper",
                    showarrow=False, font=dict(color="#555", size=10)
                )]
            )
            st.plotly_chart(fig_wl, use_container_width=True)

        # Ratings ofensivo/defensivo 
        if CORT and CDRT:
            st.markdown('<div class="section-title">Offensive Rating vs Defensive Rating</div>', unsafe_allow_html=True)
            st.caption("O_RTG = pontos marcados/100 posses · D_RTG = pontos sofridos/100 posses · Net RTG = diferença")

            fig_rtg = go.Figure()
            fig_rtg.add_trace(go.Scatter(
                x=tdata[CS], y=tdata[CORT].round(1), name="O_RTG (ataque)",
                mode="lines+markers", line=dict(color="#F4A623", width=2), marker=dict(size=5),
                hovertemplate="<b>%{x}</b><br>O_RTG: %{y:.1f}<extra></extra>",
            ))
            fig_rtg.add_trace(go.Scatter(
                x=tdata[CS], y=tdata[CDRT].round(1), name="D_RTG (defesa)",
                mode="lines+markers", line=dict(color="#3B82F6", width=2), marker=dict(size=5),
                hovertemplate="<b>%{x}</b><br>D_RTG: %{y:.1f}<extra></extra>",
            ))
            if CNRT:
                fig_rtg.add_trace(go.Scatter(
                    x=tdata[CS], y=tdata[CNRT].round(1), name="Net RTG",
                    mode="lines", line=dict(color="#10B981", width=1.5, dash="dot"),
                    hovertemplate="<b>%{x}</b><br>Net RTG: %{y:+.1f}<extra></extra>",
                ))
            fig_rtg.add_hline(y=0 if CNRT else tdata[CORT].mean(),
                              line_dash="dash", line_color="#333", line_width=1)
            fig_rtg.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888", family="Inter"),
                xaxis=dict(showgrid=False, color="#444"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=10, b=0), height=260,
            )
            st.plotly_chart(fig_rtg, use_container_width=True)

        # Pace 
        if CPAC:
            st.markdown('<div class="section-title">Ritmo de Jogo (Pace)</div>', unsafe_allow_html=True)
            st.caption("Pace = posses por 48 minutos. Mais alto = jogo mais rápido.")

            league_pace = teams_df[(teams_df[CS] >= s_range[0]) & (teams_df[CS] <= s_range[1])].groupby(CS)[CPAC].mean()

            fig_pace = go.Figure()
            fig_pace.add_trace(go.Scatter(
                x=league_pace.index, y=league_pace.values.round(1),
                name="Média da liga", mode="lines",
                line=dict(color="#333", width=1.5, dash="dot"),
            ))
            fig_pace.add_trace(go.Scatter(
                x=tdata[CS], y=tdata[CPAC].round(1), name=team_sel,
                mode="lines+markers", line=dict(color="#F4A623", width=2), marker=dict(size=5),
                fill="tonexty", fillcolor="rgba(244,166,35,0.05)",
            ))
            fig_pace.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888", family="Inter"),
                xaxis=dict(showgrid=False, color="#444"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Pace"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=10, b=0), height=220,
            )
            st.plotly_chart(fig_pace, use_container_width=True)

        # Roster da epoca
        if players_df is not None:
            CP_p = col_pick(players_df, ["player"])
            CS_p = col_pick(players_df, ["season"])
            CT_p = col_pick(players_df, ["team"])

            if CT_p and CS_p:
                abrev_row = teams_df[teams_df[CT] == team_sel]["abbreviation"].unique()
                abrev = abrev_row[0] if len(abrev_row) > 0 else team_sel
                
                roster_full = players_df[(players_df[CT_p] == team_sel) | (players_df[CT_p] == abrev)]

                if not roster_full.empty:
                    latest_s = int(roster_full[CS_p].max())
                    
                    # Filtramos para esse ano especifico
                    roster = roster_full[roster_full[CS_p] == latest_s].copy()

                    if not roster.empty:
                        st.markdown(f'<div class="section-title">Plantel — Epoca {latest_s}</div>', unsafe_allow_html=True)
                        
                        CPTS_p = col_pick(players_df, ["pts_per_game"])
                        CAST_p = col_pick(players_df, ["ast_per_game"])
                        CREB_p = col_pick(players_df, ["trb_per_game"])
                        CPER_p = col_pick(players_df, ["per"])
                        CPOS_p = col_pick(players_df, ["pos"])

                        display_cols = [c for c in [CP_p, CPOS_p, CPTS_p, CAST_p, CREB_p, CPER_p] if c]
                        rename = {CP_p:"Jogador", CPOS_p:"Pos", CPTS_p:"PTS", CAST_p:"AST", CREB_p:"REB", CPER_p:"PER"}
                        
                        st.dataframe(
                            roster[display_cols].rename(columns=rename).sort_values("PTS", ascending=False).reset_index(drop=True).round(1),
                            use_container_width=True, 
                            height=320,
                            hide_index=True
                        )

        # Tabela histórica completa 
        st.markdown('<div class="section-title">Registo Historico Detalhado</div>', unsafe_allow_html=True)
        show_cols = [c for c in [CS, CW, CL, CORT, CDRT, CNRT, CPAC, CPLO, CSRS] if c]
        rename_h = {CS:"Epoca", CW:"V", CL:"D", CORT:"O_RTG", CDRT:"D_RTG", CNRT:"Net_RTG", CPAC:"Pace", CPLO:"Playoffs", CSRS:"SRS"}
        
        tbl = tdata[show_cols].rename(columns=rename_h).sort_values("Epoca", ascending=False).copy()
        
        # Estilo para a tabela
        def style_historical(row):
            styles = [''] * len(row)
            
            if "Playoffs" in row and (row["Playoffs"] is True or row["Playoffs"] == 1):
                styles = ['background-color: rgba(244, 166, 35, 0.05);'] * len(row)
            
            if "Net_RTG" in row and row["Net_RTG"] > 0:
                idx = list(row.index).index("Net_RTG")
                styles[idx] += 'color: #10B981; font-weight: bold;'
                
            return styles

        st.dataframe(
            tbl.style.apply(style_historical, axis=1),
            column_config={
                "Playoffs": st.column_config.CheckboxColumn("Playoffs"),
                "Epoca": st.column_config.NumberColumn("Epoca", format="%d")
            },
            use_container_width=True, height=400, hide_index=True
        )


# Comparação de Equipas
with tab2:
    st.markdown('<div class="section-title">Comparar duas equipas</div>', unsafe_allow_html=True)

    ca2, cb2 = st.columns(2)
    with ca2:
        team_a = st.selectbox("Equipa A", all_teams, index=all_teams.index("LAL") if "LAL" in all_teams else 0, key="ta2")
    with cb2:
        team_b = st.selectbox("Equipa B", all_teams, index=all_teams.index("BOS") if "BOS" in all_teams else 1, key="tb2")

    s2_range = st.slider("Épocas (comparação)", season_min, season_max, (1990, season_max), key="s2")

    da2 = teams_df[(teams_df[CT] == team_a) & (teams_df[CS] >= s2_range[0]) & (teams_df[CS] <= s2_range[1])]
    db2 = teams_df[(teams_df[CT] == team_b) & (teams_df[CS] >= s2_range[0]) & (teams_df[CS] <= s2_range[1])]

    # Métricas resumo lado a lado
    compare_stats = []
    if CW: compare_stats.append(("Vitórias totais", int(da2[CW].sum()), int(db2[CW].sum()),   False))
    if CPLO: compare_stats.append(("Épocas playoffs", int(da2[CPLO].sum()), int(db2[CPLO].sum()), False))
    if CORT: compare_stats.append(("O_RTG médio", round(da2[CORT].mean(),1), round(db2[CORT].mean(),1), False))
    if CDRT: compare_stats.append(("D_RTG médio", round(da2[CDRT].mean(),1), round(db2[CDRT].mean(),1), True))
    if CNRT: compare_stats.append(("Net RTG médio", round(da2[CNRT].mean(),2), round(db2[CNRT].mean(),2), False))
    if CPAC: compare_stats.append(("Pace médio", round(da2[CPAC].mean(),1), round(db2[CPAC].mean(),1), False))

    if compare_stats:
        st.markdown(f"**{team_a}** vs **{team_b}** — {s2_range[0]}–{s2_range[1]}")
        col_a, col_m, col_b = st.columns([2, 1, 2])
        with col_a:
            st.markdown(f"### {team_a}")
        with col_m:
            st.markdown("### &nbsp;", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"### {team_b}")

        for label, va, vb, lower_better in compare_stats:
            ca_c, cm_c, cb_c = st.columns([2, 1, 2])
            better_a = (va > vb) if not lower_better else (va < vb)
            color_a  = "#F4A623" if better_a else "#555"
            color_b  = "#3B82F6" if not better_a else "#555"
            ca_c.markdown(f"<p style='color:{color_a};font-family:Bebas Neue,sans-serif;font-size:1.6rem;margin:4px 0'>{va}</p><p style='color:#666;font-size:0.75rem;text-transform:uppercase'>{label}</p>", unsafe_allow_html=True)
            cm_c.markdown(f"<p style='color:#333;text-align:center;font-size:0.8rem;margin-top:10px'>{label}</p>", unsafe_allow_html=True)
            cb_c.markdown(f"<p style='color:{color_b};font-family:Bebas Neue,sans-serif;font-size:1.6rem;margin:4px 0'>{vb}</p>", unsafe_allow_html=True)

    st.markdown("---")

    # Win shares ao longo do tempo — linha dupla
    if CW:
        st.markdown('<div class="section-title">Vitórias por Época</div>', unsafe_allow_html=True)
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Scatter(
            x=da2[CS], y=da2[CW], name=team_a,
            mode="lines+markers", line=dict(color="#F4A623", width=2), marker=dict(size=5),
        ))
        fig_cmp.add_trace(go.Scatter(
            x=db2[CS], y=db2[CW], name=team_b,
            mode="lines+markers", line=dict(color="#3B82F6", width=2), marker=dict(size=5),
        ))
        fig_cmp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888", family="Inter"),
            xaxis=dict(showgrid=False, color="#444"),
            yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Vitórias"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=10, b=0), height=280,
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

    # Net RTG comparado
    if CNRT:
        st.markdown('<div class="section-title">Net Rating Comparativo</div>', unsafe_allow_html=True)
        fig_nrt = go.Figure()
        fig_nrt.add_trace(go.Bar(
            x=da2[CS], y=da2[CNRT].round(1), name=team_a,
            marker_color="rgba(244,166,35,0.7)",
            hovertemplate="<b>%{x}</b><br>Net RTG: %{y:+.1f}<extra></extra>",
        ))
        fig_nrt.add_trace(go.Bar(
            x=db2[CS], y=db2[CNRT].round(1), name=team_b,
            marker_color="rgba(59,130,246,0.7)",
            hovertemplate="<b>%{x}</b><br>Net RTG: %{y:+.1f}<extra></extra>",
        ))
        fig_nrt.add_hline(y=0, line_dash="dash", line_color="#333", line_width=1)
        fig_nrt.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888", family="Inter"),
            xaxis=dict(showgrid=False, color="#444"),
            yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Net RTG"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=10, b=0), height=260,
        )
        st.plotly_chart(fig_nrt, use_container_width=True)

# Liga por Época
with tab3:
    st.markdown('<div class="section-title">Distribuição da Liga numa Época</div>', unsafe_allow_html=True)

    epoch_sel = st.selectbox("Selecionar época", sorted(teams_df[CS].unique(), reverse=True), key="epoch_tab3")

    epoch_data = teams_df[teams_df[CS] == epoch_sel].copy()

    if epoch_data.empty:
        st.warning("Sem dados para esta época.")
    else:
        # O_RTG vs D_RTG
        if CORT and CDRT:
            st.markdown(f"**Offensive Rating vs Defensive Rating — {epoch_sel}**")
            st.caption("Canto superior esquerdo = melhor (muito ataque, pouca defesa sofrida). Tamanho do ponto = vitórias.")

            epoch_data["win_size"] = epoch_data[CW].fillna(20) if CW else 20
            epoch_data["playoffs_label"] = epoch_data[CPLO].map({True: "Playoffs", False: "Regular Season", 1: "Playoffs", 0: "Regular Season"}) if CPLO else "—"

            fig_scatter = go.Figure()
            for plo_val, color, sym in [("Playoffs", "#F4A623", "star"), ("Regular Season", "#3B82F6", "circle")]:
                sub = epoch_data[epoch_data["playoffs_label"] == plo_val]
                if sub.empty:
                    continue
                fig_scatter.add_trace(go.Scatter(
                    x=sub[CDRT], y=sub[CORT],
                    mode="markers+text",
                    name=plo_val,
                    text=sub[CT],
                    textposition="top center",
                    textfont=dict(size=9, color="#666"),
                    marker=dict(size=sub["win_size"] / 4 + 8, color=color, opacity=0.75, symbol=sym, line=dict(color="#222", width=1)),
                    hovertemplate="<b>%{text}</b><br>O_RTG: %{y:.1f}<br>D_RTG: %{x:.1f}<extra></extra>",
                ))

            # Linhas de médias da liga
            avg_ort = epoch_data[CORT].mean()
            avg_drt = epoch_data[CDRT].mean()
            fig_scatter.add_hline(y=avg_ort, line_dash="dot", line_color="#333", line_width=1)
            fig_scatter.add_vline(x=avg_drt, line_dash="dot", line_color="#333", line_width=1)

            fig_scatter.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888", family="Inter"),
                xaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Defensive Rating (menor = melhor defesa)"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444", title="Offensive Rating (maior = melhor ataque)"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=20, b=0), height=500,
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Tabela da época 
        st.markdown(f'<div class="section-title">Classificação — {epoch_sel}</div>', unsafe_allow_html=True)

        show_cols2 = [c for c in [CT, CW, CL, CORT, CDRT, CNRT, CPAC, CPLO, CSRS] if c]
        rename2    = {CT:"Equipa", CW:"V", CL:"D", CORT:"O_RTG", CDRT:"D_RTG", CNRT:"Net_RTG", CPAC:"Pace", CPLO:"Playoffs", CSRS:"SRS"}
        tbl2 = epoch_data[show_cols2].rename(columns=rename2)
        if "Playoffs" in tbl2.columns:
            tbl2["Playoffs"] = tbl2["Playoffs"].map({True:"✅", False:"—", 1:"✅", 0:"—"})
        sort_col = "V" if "V" in tbl2.columns else tbl2.columns[1]
        st.dataframe(
            tbl2.sort_values(sort_col, ascending=False).reset_index(drop=True).round(2),
            use_container_width=True, height=500,
        )