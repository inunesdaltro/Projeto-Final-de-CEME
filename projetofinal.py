
"""
projetofinal.py
─────────────────────────────
• Lê CSV, calcula S, fp, carga
• Gera 6 PNGs para o relatório:
    tabela_stats.png         
    tabela_nominais.png
    serie_temporal_color.png
    dispersao_potencia_fp_color.png
    histograma_potencia_color.png
    histograma_fp_color.png

"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ---------- CONFIGURAÇÕES ----------------
CSV_PATH = "bomba_centro_cirurgico.csv"

# Nomes de coluna conforme o arquivo CSV do usuário (corrigindo o KeyError)
COL_DATA = "data"
COL_POT_INCORRETA = "potencia" # Coluna com o valor errado de ~48kW
COL_VOLT = "tensao_saida"
COL_CORR = "corrente"

# Potência nominal de SAÍDA do motor é 15kW. A de ENTRADA é P_out / rendimento.
POTENCIA_NOMINAL_SAIDA_kW = 15.0
RENDIMENTO_NOMINAL = 0.924
POTENCIA_NOMINAL_ENTRADA_kW = POTENCIA_NOMINAL_SAIDA_kW / RENDIMENTO_NOMINAL # ~16.23 kW

# Cores e estilo para os gráficos
C_TURQ = "#36C3B9"; C_ROXO = "#8D36C3"; C_ROSA = "#F53D81"; C_CINZ = "#4C4C4C"
plt.rcParams.update({"font.size":10, "axes.grid":True, "grid.alpha":.25,
                     "axes.edgecolor":C_CINZ, "axes.labelcolor":C_CINZ,
                     "xtick.color":C_CINZ, "ytick.color":C_CINZ,
                     "figure.dpi":120})

# Dados de placa dos equipamentos
MOTOR = {"Potência":"15 kW (20 CV)","Tensão (estrela)":"440 V","Corrente":"26,3 A",
         "Fator de Potência":"0,81 (ind.)","Rendimento":"92,4 %","Rotação nominal":"1775 rpm",
         "Fator de serviço":"1,15","Carcaça":"160 M","Massa":"124 kg"}
BOMBA = {"Vazão bomba":"219,2 m³/h","Altura bomba":"29,8 m","Modelo bomba":"KSB Meganorm 125-315"}

# ---------- FUNÇÕES UTILITÁRIAS ------------
def print_step(msg):
    print(f"\n{'-'*len(msg)}\n{msg}\n{'-'*len(msg)}")

def save_table(df, fname, head_color, title="", scale=1.35):
    rows = len(df)
    fig_h = 0.5 + 0.35 * rows
    fig, ax = plt.subplots(figsize=(6, fig_h))
    ax.axis("off")
    tbl = ax.table(cellText=df.values, colLabels=df.columns, cellLoc="left", colLoc="left", loc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(9)
    tbl.scale(1, scale)
    for c in range(df.shape[1]):
        tbl[0, c].set_facecolor(head_color)
        tbl[0, c].set_text_props(color="white", weight="bold")
    for r in range(1, rows + 1):
        if r % 2 == 0:
            for c in range(df.shape[1]): tbl[r, c].set_facecolor("#F4F4F4")
    if title: fig.suptitle(title, fontsize=11, weight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ Tabela salva: {fname}")

def save_fig(fig, fname):
    fig.savefig(fname, dpi=300); plt.close(fig)
    print(f"✓ Gráfico salvo: {fname}")

# ---------- 1) LEITURA E LIMPEZA DOS DADOS ------------
print_step("1) Carregando e limpando CSV")
df = pd.read_csv(CSV_PATH)

# Trata o formato da data e converte as colunas numéricas
df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce", dayfirst=True)
for col in (COL_POT_INCORRETA, COL_VOLT, COL_CORR):
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")

df.dropna(subset=[COL_DATA, COL_POT_INCORRETA, COL_VOLT, COL_CORR], inplace=True)
print(f"Linhas válidas após limpeza: {len(df)}")

# ---------- 2) CORREÇÃO DA ANÁLISE E CÁLCULOS -----------
print_step("2) Corrigindo a análise e recalculando a potência")

# 2.1. Calcula a Potência Aparente (S) a partir da tensão e corrente medidas.
df["potencia_aparente_kVA"] = (np.sqrt(3) * df[COL_VOLT] * df[COL_CORR]) / 1000

# 2.2. Estima o fator de potência (fp) real do sistema.
df["fp_estimado"] = df[COL_POT_INCORRETA] / df["potencia_aparente_kVA"]
fp_medio_estimado = df["fp_estimado"].mean()
print(f"Fator de potência médio estimado: {fp_medio_estimado:.2f}")

# 2.3. Calcula a Potência Ativa (P) CORRIGIDA e a Carga.
df["potencia_ativa_kW_corrigida"] = df["potencia_aparente_kVA"] * fp_medio_estimado
df["carga_%_corrigida"] = 100 * df["potencia_ativa_kW_corrigida"] / POTENCIA_NOMINAL_ENTRADA_kW

# ---------- 3) GERAÇÃO DAS TABELAS PNG ------------
print_step("3) Gerando tabelas PNG com dados corrigidos")

# 3.1 Tabela de Estatísticas (Título ajustado)
stats_df = df[["potencia_ativa_kW_corrigida", "fp_estimado", "carga_%_corrigida"]].describe().loc[["mean", "std", "min", "max"]]
stats_df.index = ["Média", "Desvio-padrão", "Mínimo", "Máximo"]
stats_df.columns = ["Potência Ativa (kW)", "Fator de Potência", "Carga (%)"]
save_table(stats_df.round(2), "tabela_stats.png", C_ROXO, "Estatísticas de Operação", scale=1.6)

# 3.2 Tabela de Dados Nominais
nom_df = pd.DataFrame(list(MOTOR.items()) + list(BOMBA.items()), columns=["Parâmetro", "Valor"])
save_table(nom_df, "tabela_nominais.png", C_TURQ, "Valores Nominais — Motor e Bomba", scale=1.35)

# ---------- 4) GERAÇÃO DOS GRÁFICOS ------------
print_step("4) Gerando gráficos com dados corrigidos")

# 4.1 Série Temporal
fig, ax1 = plt.subplots(figsize=(9, 4))
ax1.plot(df[COL_DATA], df["potencia_ativa_kW_corrigida"], color=C_TURQ, lw=1.4)
ax1.set_ylabel("Potência Ativa (kW)", color=C_TURQ)
ax1.tick_params(axis='y', labelcolor=C_TURQ)

ax2 = ax1.twinx()
ax2.plot(df[COL_DATA], df["fp_estimado"], color=C_ROXO, ls="--", lw=1.2)
ax2.set_ylabel("Fator de Potência", color=C_ROXO)
ax2.tick_params(axis='y', labelcolor=C_ROXO); ax2.set_ylim(0, 1.05)

ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
fig.suptitle("Série Temporal – Potência Ativa e Fator de Potência", fontsize=11, weight="bold")
fig.tight_layout()
save_fig(fig, "serie_temporal_color.png")

# 4.2 Gráfico de Dispersão
fig = plt.figure(figsize=(6, 5))
plt.scatter(df["potencia_ativa_kW_corrigida"], df["fp_estimado"], color=C_ROSA, edgecolor="k", s=22, alpha=0.65)
plt.xlabel("Potência Ativa (kW)"); plt.ylabel("Fator de Potência")
plt.title("Dispersão – Potência Ativa vs. Fator de Potência", fontsize=11, weight="bold")
plt.grid(ls="--", alpha=0.3); plt.tight_layout()
save_fig(fig, "dispersao_potencia_fp_color.png")

# 4.3 Histograma da Potência Ativa
fig = plt.figure(figsize=(6, 4))
plt.hist(df["potencia_ativa_kW_corrigida"], bins=20, color=C_TURQ, edgecolor="black", alpha=0.85)
plt.axvline(df["potencia_ativa_kW_corrigida"].mean(), color=C_ROXO, ls="--",
            label=f"Média = {df['potencia_ativa_kW_corrigida'].mean():.2f} kW")
plt.title("Histograma da Potência Ativa", fontsize=11, weight="bold")
plt.xlabel("Potência Ativa (kW)"); plt.ylabel("Frequência")
plt.legend(); plt.tight_layout()
save_fig(fig, "histograma_potencia_color.png")

# 4.4 Histograma do Fator de Potência
fig = plt.figure(figsize=(6, 4))
plt.hist(df["fp_estimado"].dropna(), bins=20, color=C_ROXO, edgecolor="black", alpha=0.85)
plt.axvline(df["fp_estimado"].mean(), color=C_TURQ, ls="--",
            label=f"Média = {df['fp_estimado'].mean():.2f}")
plt.title("Histograma do Fator de Potência", fontsize=11, weight="bold")
plt.xlabel("Fator de Potência"); plt.ylabel("Frequência")
plt.legend(); plt.tight_layout()
save_fig(fig, "histograma_fp_color.png")

print_step("Processo concluído – 6 PNGs (com análise correta) gerados")
