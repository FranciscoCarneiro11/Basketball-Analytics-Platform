import streamlit as st
from pathlib import Path

# Tema base 
# As cores principais, fundo e tipografia são controladas por .streamlit/config.toml.
# Aqui ficam apenas as classes CSS personalizadas que o config.toml não consegue expressar.

# CSS partilhado por todas as páginas
_CSS_BASE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

  /* Tipografia e fundo global */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d0d0d;
    color: #f0f0f0;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #1e1e1e;
  }

  /* Cards de métrica */
  [data-testid="metric-container"] {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 16px;
  }
  [data-testid="metric-container"] label {
    color: #888 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F4A623 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2rem !important;
  }

  /* Título de secção com barra laranja à esquerda */
  .section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    color: #F4A623;
    border-left: 4px solid #F4A623;
    padding-left: 12px;
    margin: 28px 0 16px 0;
  }

  /* Cabeçalho de página */
  .page-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    color: #F4A623;
    line-height: 1;
    margin-bottom: 4px;
  }
  .page-sub {
    color: #666;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 32px;
  }

  /* Separador */
  hr { border-color: #1e1e1e !important; margin: 24px 0; }
</style>
"""

# CSS exclusivo de cada página
_CSS_HOME = """
<style>
  .data-badge {
    background: #111; border: 1px solid #222; border-radius: 8px;
    padding: 8px 14px; font-size: 0.78rem; color: #555; margin-bottom: 16px;
  }
  .data-badge span { color: #F4A623; font-weight: 600; }

  .player-card {
    background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
    padding: 14px 18px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 16px;
  }
  .player-rank { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #F4A623; min-width: 32px; }
  .player-name { font-weight: 600; font-size: 0.95rem; }
  .player-team { color: #888; font-size: 0.8rem; }
  .player-pts  { margin-left: auto; font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; color: #F4A623; }
</style>
"""

_CSS_PERFIL = """
<style>
  .badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; margin: 4px 4px 4px 0; letter-spacing: 0.05em;
  }
  .badge-allstar { background: rgba(244,166,35,0.15); border: 1px solid #F4A623; color: #F4A623; }
  .badge-hof     { background: rgba(255,215,0,0.12);  border: 1px solid gold;    color: gold; }

  .info-row  { display: flex; gap: 32px; flex-wrap: wrap; margin-bottom: 8px; }
  .info-item label { color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }
  .info-item p     { color: #f0f0f0; font-size: 0.95rem; font-weight: 500; margin: 2px 0 0 0; }
</style>
"""

_CSS_COMPARACAO = """
<style>
  .head-A { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #F4A623; margin: 0; }
  .head-B { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #3B82F6; margin: 0; }
  .vs     { font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #333; text-align: center; }
  .winner-badge {
    background: rgba(244,166,35,0.15); border: 1px solid #F4A623; color: #F4A623;
    padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; margin-left: 8px;
  }
</style>
"""

_CSS_EQUIPAS = """
<style>
  .stat-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; padding: 16px 20px; }
  .stat-card h4    { color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 0 0 6px 0; }
  .stat-card p     { color: #F4A623; font-family: 'Bebas Neue', sans-serif; font-size: 2rem; margin: 0; }
  .stat-card span  { color: #666; font-size: 0.8rem; }

  .playoffs-badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
  .playoffs-yes   { background: rgba(16,185,129,0.15); border: 1px solid #10B981; color: #10B981; }
  .playoffs-no    { background: rgba(239,68,68,0.1);   border: 1px solid #444;    color: #666; }
</style>
"""

_CSS_RANKINGS = """
<style>
  .rank-card {
    background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 14px;
  }
  .rank-num  { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: #F4A623; min-width: 36px; text-align: right; }
  .rank-name { font-weight: 600; font-size: 0.95rem; }
  .rank-sub  { color: #666; font-size: 0.78rem; margin-top: 2px; }
  .rank-val  { margin-left: auto; font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; color: #F4A623; white-space: nowrap; }

  .tier-star     { color: #F4A623; }
  .tier-starter  { color: #3B82F6; }
  .tier-rotation { color: #10B981; }
  .tier-bench    { color: #888; }
  .tier-fringe   { color: #444; }
</style>
"""

# Mapa página 
_PAGE_CSS = {
    "home":       _CSS_HOME,
    "perfil":     _CSS_PERFIL,
    "comparacao": _CSS_COMPARACAO,
    "equipas":    _CSS_EQUIPAS,
    "rankings":   _CSS_RANKINGS,
}


def apply_theme(page: str = "") -> None:
    
    #Aplica o tema global + CSS específico da página.
    st.markdown(_CSS_BASE, unsafe_allow_html=True)
    if page in _PAGE_CSS:
        st.markdown(_PAGE_CSS[page], unsafe_allow_html=True)


# Helpers partilhados 

def find_csv(data_dir: Path, names: list[str]) -> Path | None:
    # Da return do primeiro ficheiro CSV encontrado em data_dir, da lista names
    for n in names:
        p = data_dir / n
        if p.exists():
            return p
    return None


def col_pick(df, candidates: list[str]) -> str | None:
    # Da return o primeiro nome de coluna de candidates que existe em df
    for c in candidates:
        if c in df.columns:
            return c
    return None


def sidebar_nav() -> None:
    # Renderiza a navegação padrão na sidebar
    st.markdown("### NBA Analytics")
    st.markdown("---")
    st.page_link("Home.py", label="Visao Geral da Liga")
    st.page_link("pages/1_Perfil_Jogador.py", label="Perfil do Jogador")
    st.page_link("pages/2_Comparacao_Jogadores.py", label="Comparacao de Jogadores")
    st.page_link("pages/3_Analise_Equipas.py", label="Analise de Equipas")
    st.page_link("pages/4_Rankings.py", label="Rankings e Talentos")
    st.markdown("---")
    
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebarHeader"] { padding-top: 1rem; min-height: 0; }
        section[data-testid="stSidebar"] > div { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)