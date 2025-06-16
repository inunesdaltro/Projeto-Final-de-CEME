
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

# ---------- CONFIG ----------------
CSV = "bomba_centro_cirurgico.csv"
COL_DATA, COL_POT, COL_VOLT, COL_CORR = "data", "potencia", "tensao_saida", "corrente"
P_EL_NOM = 15 / 0.924        # 16,24 kW

C_TURQ = "#36C3B9"; C_ROXO = "#8D36C3"; C_ROSA = "#F53D81"; C_CINZ = "#4C4C4C"
plt.rcParams.update({"font.size":10,"axes.grid":True,"grid.alpha":.25,
                     "axes.edgecolor":C_CINZ,"axes.labelcolor":C_CINZ,
                     "xtick.color":C_CINZ,"ytick.color":C_CINZ,
                     "figure.dpi":120})

# Valores de placa
MOTOR = {"Potência":"15 kW (20 CV)","Tensão (estrela)":"440 V","Corrente":"26,3 A",
         "Fator de Potência":"0,81 (ind.)","Rendimento":"92,4 %","Rotação nominal":"1775 rpm",
         "Fator de serviço":"1,15","Carcaça":"160 M","Massa":"124 kg"}
BOMBA = {"Vazão bomba":"219,2 m³/h","Altura bomba":"29,8 m","Modelo bomba":"KSB Meganorm 125-315"}

# ---------- UTILIDADES ------------
def print_step(msg): print(f"\n{'-'*len(msg)}\n{msg}\n{'-'*len(msg)}")

def save_table(df, fname, head_color, title="", scale=1.35):
    """Tabela PNG com escala ajustável de linha."""
    rows = len(df)
    fig_h = 0.5 + 0.35*rows          # Altura proporcional ao nº de linhas
    fig, ax = plt.subplots(figsize=(6, fig_h))
    ax.axis("off")
    tbl = ax.table(cellText=df.values,
                   colLabels=df.columns,
                   cellLoc="left", colLoc="left",
                   loc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(9)
    tbl.scale(1, scale)              # <-- controla altura das linhas

    for c in range(df.shape[1]):
        tbl[0, c].set_facecolor(head_color)
        tbl[0, c].set_text_props(color="white", weight="bold")
    for r in range(1, rows+1):
        if r % 2 == 0:
            for c in range(df.shape[1]): tbl[r, c].set_facecolor("#F4F4F4")

    if title: fig.suptitle(title, fontsize=11, weight="bold", y=.98)
    plt.tight_layout(rect=[0,0,1,0.95])
    fig.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close(fig); print("✓", fname)

def save_fig(fig, fname):
    fig.savefig(fname, dpi=300); plt.close(fig); print("✓", fname)

# ---------- 1) LEITURA ------------
print_step("1) Carregando CSV")
df = pd.read_csv(CSV)
df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce", dayfirst=True)
for col in (COL_POT,COL_VOLT,COL_CORR):
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")
df.dropna(subset=[COL_DATA,COL_POT,COL_VOLT,COL_CORR], inplace=True)
print("Linhas válidas:", len(df))

# ---------- 2) CÁLCULOS -----------
print_step("2) Cálculo de S, fp e carga")
df["S_kVA"]  = np.sqrt(3)*df[COL_VOLT]*df[COL_CORR]/1000
df["fp"]     = np.where(df["S_kVA"]>0, df[COL_POT]/df["S_kVA"], np.nan)
df["carga_%"]= 100*df[COL_POT]/P_EL_NOM

# ---------- 3) TABELAS ------------
print_step("3) Gerando tabelas PNG")

# 3.1 Estatísticas (linhas maiores: scale=1.6)
stats = df[[COL_POT,"fp","carga_%"]].describe().loc[["mean","std","min","max"]]
stats.index   = ["Média","Desv.-padrão","Mínimo","Máximo"]
stats.columns = ["Potência (kW)","fp","Carga (%)"]
save_table(stats, "tabela_stats.png", C_ROXO, "Estatísticas de operação", scale=1.6)

# 3.2 Nominais motor e bomba
nom_df = pd.DataFrame(list(MOTOR.items())+list(BOMBA.items()), columns=["Parâmetro","Valor"])
save_table(nom_df, "tabela_nominais.png", C_TURQ, "Valores nominais — motor e bomba", scale=1.35)

# ---------- 4) GRÁFICOS ------------
print_step("4) Gerando gráficos")

# Série temporal
fig, ax1 = plt.subplots(figsize=(9,4))
ax1.plot(df[COL_DATA], df[COL_POT], color=C_TURQ, lw=1.4)
ax1.set_ylabel("Potência (kW)", color=C_TURQ); ax1.tick_params(labelcolor=C_TURQ)
ax2 = ax1.twinx()
ax2.plot(df[COL_DATA], df["fp"], color=C_ROXO, ls="--", lw=1.2)
ax2.set_ylabel("fp", color=C_ROXO); ax2.tick_params(labelcolor=C_ROXO); ax2.set_ylim(0,1.1)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
fig.suptitle("Série temporal – Potência e fp", fontsize=11, weight="bold")
fig.tight_layout(); save_fig(fig, "serie_temporal_color.png")

# Dispersão
fig = plt.figure(figsize=(6,5))
plt.scatter(df[COL_POT], df["fp"], color=C_ROSA, edgecolor="k", s=22, alpha=.65)
plt.xlabel("Potência (kW)"); plt.ylabel("fp")
plt.title("Dispersão – Potência × fp", fontsize=11, weight="bold")
plt.grid(ls="--", alpha=.3); plt.tight_layout()
save_fig(fig, "dispersao_potencia_fp_color.png")

# Hist potência
fig = plt.figure(figsize=(6,4))
plt.hist(df[COL_POT], bins=20, color=C_TURQ, edgecolor="black", alpha=.85)
plt.axvline(df[COL_POT].mean(), color=C_ROXO, ls="--",
            label=f"Média = {df[COL_POT].mean():.2f} kW")
plt.title("Histograma da Potência ativa", fontsize=11, weight="bold")
plt.xlabel("Potência (kW)"); plt.ylabel("Frequência")
plt.legend(); plt.tight_layout()
save_fig(fig, "histograma_potencia_color.png")

# Hist fp
fig = plt.figure(figsize=(6,4))
plt.hist(df["fp"].dropna(), bins=20, color=C_ROXO, edgecolor="black", alpha=.85)
plt.axvline(df["fp"].mean(), color=C_TURQ, ls="--",
            label=f"Média = {df['fp'].mean():.2f}")
plt.title("Histograma do fator de potência", fontsize=11, weight="bold")
plt.xlabel("fp"); plt.ylabel("Frequência")
plt.legend(); plt.tight_layout()
save_fig(fig, "histograma_fp_color.png")

print_step("Processo concluído – 6 PNGs gerados")
