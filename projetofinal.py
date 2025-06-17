import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap

# --- 1. CONFIGURAÇÕES E PALETA DE CORES ---
COR_TEAL = '#36C3B9'
COR_ROXO = '#8D36C3'
COR_ROSA = '#F53D80'
COR_CINZA = '#4C4C4C'
COR_CINZA_CLARO = '#F0F0F0'
plt.style.use('seaborn-v0_8-whitegrid')
cmap_custom = LinearSegmentedColormap.from_list("custom_gradient", [COR_ROXO, COR_ROSA, COR_TEAL])

# --- 2. CONSTANTES ---
POTENCIA_NOMINAL_SAIDA_KW = 15.0
EFICIENCIA_NOMINAL_MOTOR = 0.928

# --- 3. FUNÇÕES ESPECIALIZADAS E FINAIS PARA GERAR TABELAS ---

def gerar_tabela_estatisticas(data, titulo, nome_arquivo):
    """Função especialista para a tabela de ESTATÍSTICAS, com layout manual e testado."""
    plt.style.use('default')
    
    data_para_tabela = data.reset_index().rename(columns={'index': 'Métrica'})
    data_str = data_para_tabela.map(lambda x: f'{x:.2f}' if isinstance(x, (int, float)) else x)

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.axis('off')
    ax.set_title(titulo, fontweight='bold', fontsize=18, color=COR_CINZA, pad=25)

    col_widths = [0.26, 0.1, 0.15, 0.15, 0.1, 0.1, 0.1, 0.12]

    table = ax.table(cellText=data_str.values, colLabels=data_str.columns,
                     colWidths=col_widths, cellLoc='center', loc='center')
    
    table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1.0, 2.0)
    
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('white'); cell.set_linewidth(1.5)
        if row == 0:
            cell.set_text_props(weight='bold', color='white'); cell.set_facecolor(COR_CINZA)
        else:
            if col == 0:
                cell.set_text_props(weight='bold', color='white'); cell.set_facecolor(COR_ROXO)
            else:
                cell.set_facecolor(COR_CINZA_CLARO if row % 2 != 0 else 'white')

    plt.tight_layout(pad=1.0); plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight'); plt.close(fig)
    print(f"Tabela '{nome_arquivo}' gerada com sucesso.")


def gerar_tabela_nominais(data, titulo, nome_arquivo):
    """Função especialista para a tabela de DADOS NOMINAIS, com layout manual e testado."""
    plt.style.use('default')
    
    data_para_tabela = data.reset_index().rename(columns={'index': 'Parâmetro'})
    data_str = data_para_tabela.map(lambda x: f'{x:.2f}' if isinstance(x, (int, float)) else x)

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis('off'); ax.set_title(titulo, fontweight='bold', fontsize=18, color=COR_CINZA, pad=25)
    
    col_widths = [0.6, 0.4]

    table = ax.table(cellText=data_str.values, colLabels=data_str.columns,
                     colWidths=col_widths, cellLoc='center', loc='center')
    
    table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1, 1.8)
    
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('white'); cell.set_linewidth(1.5)
        if row == 0:
            cell.set_text_props(weight='bold', color='white'); cell.set_facecolor(COR_CINZA)
        else:
            if col == 0:
                cell.set_text_props(weight='bold', color='white'); cell.set_facecolor(COR_ROXO)
            else:
                cell.set_facecolor(COR_CINZA_CLARO if row % 2 != 0 else 'white')

    plt.tight_layout(pad=1.0); plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight'); plt.close(fig)
    print(f"Tabela '{nome_arquivo}' gerada com sucesso.")


# --- 4. FLUXO PRINCIPAL DE ANÁLISE ---
try:
    df = pd.read_csv('bomba_centro_cirurgico.csv')
except FileNotFoundError:
    print("Erro: Arquivo 'bomba_centro_cirurgico.csv' não encontrado."); exit()

df.rename(columns={'potencia': 'potencia_ativa_kW', 'corrente': 'corrente_A', 'data': 'data_hora'}, inplace=True)
df['data_hora'] = pd.to_datetime(df['data_hora'])
df.dropna(subset=['potencia_ativa_kW', 'corrente_A', 'tensao_saida'], inplace=True)

df['potencia_aparente_kVA'] = (np.sqrt(3) * df['tensao_saida'] * df['corrente_A']) / 1000
df['fator_potencia'] = 0.0
df.loc[df['potencia_aparente_kVA'] > 0.01, 'fator_potencia'] = df['potencia_ativa_kW'] / df['potencia_aparente_kVA']
df.loc[df['fator_potencia'] > 1, 'fator_potencia'] = 1

df_operacional = df[(df['potencia_ativa_kW'] > 1) & (df['tensao_saida'] > 100)].copy()
df_operacional['potencia_reativa_kVAr'] = np.sqrt(np.maximum(0, df_operacional['potencia_aparente_kVA']**2 - df_operacional['potencia_ativa_kW']**2))
potencia_nominal_entrada_kw = POTENCIA_NOMINAL_SAIDA_KW / EFICIENCIA_NOMINAL_MOTOR
df_operacional['carregamento_percentual'] = (df_operacional['potencia_ativa_kW'] / potencia_nominal_entrada_kw) * 100

stats_descritivas = df_operacional[['potencia_ativa_kW', 'corrente_A', 'fator_potencia', 'potencia_aparente_kVA', 'potencia_reativa_kVAr', 'carregamento_percentual']].describe().T
print("--- ESTATÍSTICAS FINAIS (CALCULADAS DO CSV) ---"); print(stats_descritivas.round(2))

# --- 5. GERAÇÃO DE TODOS OS ARQUIVOS DE IMAGEM ---
# Tabelas
nominais_data = pd.DataFrame([['15 kW (20 cv)'], ['~230 V (saída VFD)'], ['92.8 %']], index=['Potência Nominal', 'Tensão de Operação', 'Eficiência Nominal'], columns=['Valor'])
gerar_tabela_nominais(nominais_data, 'Dados Nominais do Motor', 'tabela_nominais.png')

stats_para_tabela = stats_descritivas[['mean', '50%', 'std', 'min', 'max', '25%', '75%']].copy()
stats_para_tabela.columns = ['Média', 'Mediana (Q2)', 'DP', 'Mínimo', 'Máximo', 'Q1 (25%)', 'Q3 (75%)']
gerar_tabela_estatisticas(stats_para_tabela, 'ESTATÍSTICAS DE OPERAÇÃO', 'tabela_stats.png')

# Gráficos
P_MEDIA_CALCULADA = stats_descritivas.loc['potencia_ativa_kW', 'mean']
FP_MEDIO_CALCULADO = stats_descritivas.loc['fator_potencia', 'mean']

# Gráfico 1: Série Temporal do Ciclo Completo
daily_stats_full = df.set_index('data_hora')[['potencia_ativa_kW', 'fator_potencia']].resample('D').mean().fillna(0)
fig, ax1 = plt.subplots(figsize=(12, 6)); ax1.set_title('Médias Diárias (Ciclo Completo, Incluindo Paradas)', fontsize=16, fontweight='bold', color=COR_CINZA); ax1.plot(daily_stats_full.index, daily_stats_full['potencia_ativa_kW'], color=COR_ROXO, marker='o', linestyle='-', label='Potência Ativa Média (kW)'); ax1.set_ylabel('Potência Ativa (kW)', color=COR_ROXO); ax1.tick_params(axis='y', labelcolor=COR_ROXO); ax2 = ax1.twinx(); ax2.plot(daily_stats_full.index, daily_stats_full['fator_potencia'], color=COR_TEAL, marker='x', linestyle='--', label='Fator de Potência Médio'); ax2.set_ylabel('FP Médio', color=COR_TEAL); ax2.tick_params(axis='y', labelcolor=COR_TEAL); ax2.set_ylim(0, 1.0); ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m')); plt.gcf().autofmt_xdate(); lines1, labels1 = ax1.get_legend_handles_labels(); lines2, labels2 = ax2.get_legend_handles_labels(); ax2.legend(lines1 + lines2, labels1 + labels2, loc='best'); plt.tight_layout(); plt.savefig('serie_temporal_ciclo_completo.png', dpi=300); plt.close(fig); print("Gráfico 'serie_temporal_ciclo_completo.png' gerado.")

# Gráfico 2: Série Temporal Apenas em Operação
daily_stats_op = df_operacional.set_index('data_hora')[['potencia_ativa_kW', 'fator_potencia']].resample('D').mean().dropna()
fig, ax1 = plt.subplots(figsize=(12, 6)); ax1.set_title('Desempenho Médio Diário (Apenas em Operação)', fontsize=16, fontweight='bold', color=COR_CINZA); ax1.plot(daily_stats_op.index, daily_stats_op['potencia_ativa_kW'], color=COR_ROXO, marker='o', linestyle='-', label='Potência Ativa Média (kW)'); ax1.set_ylabel('Potência Ativa (kW)', color=COR_ROXO); ax1.tick_params(axis='y', labelcolor=COR_ROXO); ax2 = ax1.twinx(); ax2.plot(daily_stats_op.index, daily_stats_op['fator_potencia'], color=COR_TEAL, marker='x', linestyle='--', label='Fator de Potência Médio'); ax2.set_ylabel('FP Médio', color=COR_TEAL); ax2.tick_params(axis='y', labelcolor=COR_TEAL); ax2.set_ylim(0.4, 0.8); ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m')); plt.gcf().autofmt_xdate(); lines1, labels1 = ax1.get_legend_handles_labels(); lines2, labels2 = ax2.get_legend_handles_labels(); ax2.legend(lines1 + lines2, labels1 + labels2, loc='best'); plt.tight_layout(); plt.savefig('serie_temporal_em_operacao.png', dpi=300); plt.close(fig); print("Gráfico 'serie_temporal_em_operacao.png' gerado.")

# Outros gráficos
fig, ax = plt.subplots(figsize=(10, 6)); ax.hist(df_operacional['potencia_ativa_kW'], bins=30, color=COR_ROXO, edgecolor='white', alpha=0.9); ax.axvline(P_MEDIA_CALCULADA, color=COR_TEAL, linestyle='--', linewidth=2.5, label=f'Potência Média: {P_MEDIA_CALCULADA:.2f} kW'); ax.set_title('Distribuição da Potência Ativa (Motor em Operação)', fontsize=16, fontweight='bold', color=COR_CINZA); ax.set_xlabel('Potência Ativa (kW)'); ax.set_ylabel('Frequência'); ax.legend(); plt.tight_layout(); plt.savefig('histograma_potencia_color.png', dpi=300); plt.close(fig); print("Gráfico 'histograma_potencia_color.png' gerado.")
fig, ax = plt.subplots(figsize=(10, 6)); ax.hist(df_operacional['fator_potencia'], bins=30, color=COR_TEAL, edgecolor='white', alpha=0.9); ax.axvline(FP_MEDIO_CALCULADO, color=COR_ROXO, linestyle='--', linewidth=2.5, label=f'FP Médio: {FP_MEDIO_CALCULADO:.2f}'); ax.set_title('Distribuição do Fator de Potência (Motor em Operação)', fontsize=16, fontweight='bold', color=COR_CINZA); ax.set_xlabel('Fator de Potência'); ax.set_ylabel('Frequência'); ax.legend(); plt.tight_layout(); plt.savefig('histograma_fp_color.png', dpi=300); plt.close(fig); print("Gráfico 'histograma_fp_color.png' gerado.")
fig, ax = plt.subplots(figsize=(10, 6)); scatter = ax.scatter(df_operacional['potencia_ativa_kW'], df_operacional['fator_potencia'], c=df_operacional['fator_potencia'], cmap=cmap_custom, alpha=0.7); ax.set_title('Correlação entre Carga do Motor e Fator de Potência', fontsize=16, fontweight='bold', color=COR_CINZA); ax.set_xlabel('Potência Ativa (kW)'); ax.set_ylabel('Fator de Potência'); cbar = plt.colorbar(scatter); cbar.set_label('Nível do Fator de Potência'); plt.tight_layout(); plt.savefig('dispersao_potencia_fp_color.png', dpi=300); plt.close(fig); print("Gráfico 'dispersao_potencia_fp_color.png' gerado.")

print("\nProcesso finalizado.")
