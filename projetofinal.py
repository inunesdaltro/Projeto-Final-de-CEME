import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# --- Paleta de Cores e Estilos ---
COR_TEAL = '#36C3B9'
COR_ROXO = '#8D36C3'
COR_ROSA = '#F53D80'
COR_CINZA = '#4C4C4C'
plt.style.use('seaborn-v0_8-whitegrid')

# --- Configurações Iniciais e Verificadas ---
TENSAO_LINHA = 380
POTENCIA_NOMINAL_SAIDA_KW = 15.0
# Eficiência nominal do motor em plena carga (valor típico para WEG W22 15kW).
# Essencial para o cálculo correto da potência de entrada nominal.
EFICIENCIA_NOMINAL_MOTOR = 0.928
# Fator de potência nominal do motor em plena carga.
FP_NOMINAL_MOTOR = 0.81

# --- Função Auxiliar para Gerar Tabelas Coloridas ---
def gerar_tabela_imagem(data, titulo, nome_arquivo, col_widths=None):
    """Renderiza um DataFrame do pandas como uma imagem PNG estilizada e colorida."""
    plt.style.use('default') # Desliga a grade de fundo para a imagem da tabela
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.axis('off')
    ax.set_title(titulo, fontweight='bold', fontsize=16, color=COR_CINZA, pad=20)
    
    table = ax.table(cellText=data.values,
                     colLabels=data.columns,
                     cellLoc='center',
                     loc='center',
                     colWidths=col_widths)

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.4)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(COR_CINZA)
        if row == 0:  # Cabeçalho
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(COR_ROXO)
        else:  # Células de dados
            cell.set_text_props(color=COR_CINZA)
            cell.set_facecolor('#f5f5f5' if row % 2 == 0 else 'white')

    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Tabela colorida '{nome_arquivo}' gerada com sucesso.")
    plt.style.use('seaborn-v0_8-whitegrid') # Restaura o estilo para os gráficos

try:
    # --- Carregamento, Preparação e Cálculos ---
    df_completo = pd.read_csv('bomba_centro_cirurgico.csv')
    df = df_completo[['data', 'corrente', 'potencia']].copy()
    df.rename(columns={'data': 'datetime', 'corrente': 'corrente_A', 'potencia': 'potencia_kW'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df['potencia_kW'] = pd.to_numeric(df['potencia_kW'], errors='coerce')
    df['corrente_A'] = pd.to_numeric(df['corrente_A'], errors='coerce')
    df.dropna(inplace=True)
    if df.empty: raise ValueError("DataFrame vazio após limpeza.")

    # Cálculos elétricos verificados
    df['potencia_aparente_kVA'] = (np.sqrt(3) * TENSAO_LINHA * df['corrente_A']) / 1000
    df['fator_potencia'] = (df['potencia_kW'] / df['potencia_aparente_kVA']).clip(upper=1.0)
    df.dropna(subset=['fator_potencia'], inplace=True)
    
    # Cálculo de carregamento corrigido e preciso
    potencia_entrada_nominal_kw = POTENCIA_NOMINAL_SAIDA_KW / EFICIENCIA_NOMINAL_MOTOR
    df['carga_%'] = (df['potencia_kW'] / potencia_entrada_nominal_kw) * 100

except Exception as e:
    print(f"Ocorreu um erro: {e}")
    exit()

# --- GERAÇÃO DAS TABELAS ---
dados_nominais = {
    'Componente': ['Motor Elétrico', 'Bomba Centrífuga'],
    'Fabricante': ['WEG', 'KSB'],
    'Modelo': ['W22 Plus', 'Meganorm'],
    'Potência': ['15 kW (20 CV)', 'N/A'],
    'Tensão': ['380V (Triângulo)', 'N/A'],
    'FP Nominal': [f'{FP_NOMINAL_MOTOR}', 'N/A']
}
df_nominais = pd.DataFrame(dados_nominais)
gerar_tabela_imagem(df_nominais, 'Dados Nominais dos Equipamentos', 'tabela_nominais.png', col_widths=[0.25, 0.25, 0.2, 0.2, 0.25, 0.15])

stats = df[['potencia_kW', 'fator_potencia', 'carga_%']].describe().loc[['mean', 'std', 'min', 'max']]
stats = stats.rename(index={'mean': 'Média', 'std': 'Desvio Padrão', 'min': 'Mínimo', 'max': 'Máximo'},
                     columns={'potencia_kW': 'Potência (kW)', 'fator_potencia': 'Fator de Potência', 'carga_%': 'Carga (%)'})
gerar_tabela_imagem(stats.round(2), 'Estatísticas Descritivas das Medições', 'tabela_stats.png')


# --- GERAÇÃO DOS GRÁFICOS ---
print("Gerando gráficos...")

# Gráfico 3: Série Temporal
df_resampled = df.set_index('datetime').resample('D').mean()
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.set_title('Série Temporal de Potência e Fator de Potência (Médias Diárias)', fontsize=16, fontweight='bold', color=COR_CINZA)
ax1.set_xlabel('Data', fontsize=12, color=COR_CINZA)
ax1.set_ylabel('Potência Ativa (kW)', fontsize=12, color=COR_TEAL)
ax1.plot(df_resampled.index, df_resampled['potencia_kW'], color=COR_TEAL, marker='o')
ax1.tick_params(axis='y', labelcolor=COR_TEAL)
ax1.tick_params(axis='x', colors=COR_CINZA)
ax2 = ax1.twinx()
ax2.set_ylabel('Fator de Potência', fontsize=12, color=COR_ROXO)
ax2.plot(df_resampled.index, df_resampled['fator_potencia'], color=COR_ROXO, marker='^', linestyle='--')
ax2.tick_params(axis='y', labelcolor=COR_ROXO)
ax2.set_ylim(0.5, 1)
fig.tight_layout()
plt.savefig('serie_temporal_color.png', dpi=300)
plt.close(fig)

# Gráfico 4: Dispersão
df_filtrado = df[df['potencia_kW'] > 1.0]
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(df_filtrado['potencia_kW'], df_filtrado['fator_potencia'], alpha=0.6, c=df_filtrado['fator_potencia'], cmap=LinearSegmentedColormap.from_list("custom", [COR_ROXO, COR_TEAL]))
ax.set_title('Fator de Potência vs. Carga do Motor (em Operação)', fontsize=16, fontweight='bold', color=COR_CINZA)
ax.set_xlabel('Potência Ativa (kW)', color=COR_CINZA)
ax.set_ylabel('Fator de Potência', color=COR_CINZA)
ax.tick_params(colors=COR_CINZA)
cbar = fig.colorbar(scatter, label='Fator de Potência')
cbar.ax.yaxis.label.set_color(COR_CINZA)
cbar.ax.tick_params(colors=COR_CINZA)
z = np.polyfit(df_filtrado['potencia_kW'], df_filtrado['fator_potencia'], 2)
p = np.poly1d(z)
xp = np.linspace(df_filtrado['potencia_kW'].min(), df_filtrado['potencia_kW'].max(), 100)
ax.plot(xp, p(xp), color=COR_ROSA, linestyle="--", linewidth=2.5, label="Linha de Tendência")
ax.legend()
plt.tight_layout()
plt.savefig('dispersao_potencia_fp_color.png', dpi=300)
plt.close(fig)

# Gráfico 5: Histograma da Potência
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['potencia_kW'], bins=30, color=COR_ROXO, edgecolor='white')
ax.axvline(df['potencia_kW'].mean(), color=COR_TEAL, linestyle='--', linewidth=2.5, label=f'Potência Média: {df["potencia_kW"].mean():.2f} kW')
ax.set_title('Distribuição da Potência Ativa Consumida', fontsize=16, fontweight='bold', color=COR_CINZA)
ax.set_xlabel('Potência Ativa (kW)', color=COR_CINZA)
ax.set_ylabel('Frequência de Ocorrências', color=COR_CINZA)
ax.tick_params(colors=COR_CINZA)
ax.legend()
plt.tight_layout()
plt.savefig('histograma_potencia_color.png', dpi=300)
plt.close(fig)

# Gráfico 6: Histograma do Fator de Potência
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['fator_potencia'], bins=30, color=COR_TEAL, edgecolor='white')
ax.axvline(df['fator_potencia'].mean(), color=COR_ROXO, linestyle='--', linewidth=2.5, label=f'FP Médio: {df["fator_potencia"].mean():.2f}')
ax.set_title('Distribuição do Fator de Potência', fontsize=16, fontweight='bold', color=COR_CINZA)
ax.set_xlabel('Fator de Potência', color=COR_CINZA)
ax.set_ylabel('Frequência de Ocorrências', color=COR_CINZA)
ax.tick_params(colors=COR_CINZA)
ax.legend()
plt.tight_layout()
plt.savefig('histograma_fp_color.png', dpi=300)
plt.close(fig)

print("Todos os gráficos foram gerados com sucesso.")
print("\n--- Script concluído. ---")
