import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 1. CONFIGURAÇÕES E PALETA DE CORES ---
COR_TEAL = '#36C3B9'
COR_ROXO = '#8D36C3'
COR_CINZA = '#4C4C4C'
plt.style.use('seaborn-v0_8-whitegrid')

# Constantes do motor e do sistema
TENSAO_LINHA_V = 380
POTENCIA_NOMINAL_SAIDA_KW = 15.0
EFICIENCIA_NOMINAL_MOTOR = 0.928
FP_ALVO = 0.92

# --- 2. CARREGAMENTO E TRATAMENTO DOS DADOS ---
try:
    df = pd.read_csv('bomba_centro_cirurgico.csv')
except FileNotFoundError:
    print("Erro: Arquivo 'bomba_centro_cirurgico.csv' não encontrado.")
    exit()

# **CORREÇÃO CRUCIAL**: Renomeia as colunas do arquivo real e trata a data
df.rename(columns={'potencia': 'potencia_ativa_kW', 'corrente': 'corrente_A', 'data': 'data_hora'}, inplace=True)
df['data_hora'] = pd.to_datetime(df['data_hora'])
df.dropna(subset=['potencia_ativa_kW', 'corrente_A'], inplace=True)
df = df[df['potencia_ativa_kW'] > 1].copy()

# --- 3. CÁLCULOS DE ENGENHARIA ELÉTRICA (com os dados corretos) ---
potencia_nominal_entrada_kw = POTENCIA_NOMINAL_SAIDA_KW / EFICIENCIA_NOMINAL_MOTOR
df['potencia_aparente_kVA'] = (np.sqrt(3) * TENSAO_LINHA_V * df['corrente_A']) / 1000
df['fator_potencia'] = df['potencia_ativa_kW'] / df['potencia_aparente_kVA']
df.loc[df['fator_potencia'] > 1, 'fator_potencia'] = 1
df['potencia_reativa_kVAr'] = np.sqrt(np.maximum(0, df['potencia_aparente_kVA']**2 - df['potencia_ativa_kW']**2))
df['carregamento_percentual'] = (df['potencia_ativa_kW'] / potencia_nominal_entrada_kw) * 100

# --- 4. ANÁLISE ESTATÍSTICA ---
stats_descritivas = df[['potencia_ativa_kW', 'corrente_A', 'fator_potencia', 'potencia_aparente_kVA', 'potencia_reativa_kVAr', 'carregamento_percentual']].describe().T
stats_descritivas = stats_descritivas[['mean', '50%', 'std', 'min', 'max', '25%', '75%']]
stats_descritivas.columns = ['Média', 'Mediana (Q2)', 'Desvio Padrão', 'Mínimo', 'Máximo', 'Q1 (25%)', 'Q3 (75%)']
stats_descritivas.index = ['Potência Ativa (kW)', 'Corrente (A)', 'Fator de Potência', 'Potência Aparente (kVA)', 'Potência Reativa (kVAr)', 'Carregamento (%)']
stats_formatada = stats_descritivas.round(2)
print("--- TABELA DE ESTATÍSTICAS (Valores Corrigidos) ---")
print(stats_formatada)

# --- 5. GERAÇÃO DAS IMAGENS DAS TABELAS (com cores) ---
def gerar_tabela_imagem(data, titulo, nome_arquivo):
    """Renderiza um DataFrame como uma imagem PNG estilizada."""
    plt.style.use('default')
    num_rows = len(data)
    fig_height = 1.0 + num_rows * 0.4
    fig, ax = plt.subplots(figsize=(8, fig_height))
    ax.axis('off')
    ax.set_title(titulo, fontweight='bold', fontsize=16, color=COR_CINZA, pad=20)
    
    # Cria a tabela
    table = ax.table(cellText=data.values, colLabels=data.columns, rowLabels=data.index, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    
    # Colore as células
    for i, key in enumerate(data.index):
        # Colore a linha do header
        table[0, i].set_facecolor(COR_CINZA)
        table[0, i].set_text_props(color='white', weight='bold')
    
    for i in range(num_rows + 1):
        # Colore a coluna do index
        if i > 0:
            table[i, -1].set_facecolor(COR_ROXO)
            table[i, -1].set_text_props(color='white', weight='bold')

    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Tabela '{nome_arquivo}' gerada com sucesso.")

# Gerar tabela de dados nominais
nominais_data = pd.DataFrame([
    ['Potência Nominal', '15 kW (20 cv)'],
    ['Tensão de Linha', '380 V'],
    ['Eficiência Nominal', '92.8 %'],
    ['FP Nominal', '0.81']
], columns=['Parâmetro', 'Valor']).set_index('Parâmetro')
gerar_tabela_imagem(nominais_data, 'Dados Nominais do Motor', 'tabela_nominais.png')

# Gerar tabela de estatísticas corrigida
stats_para_imagem = stats_formatada.copy()
stats_para_imagem.columns = ['Média', 'Mediana', 'DP', 'Mín', 'Máx', 'Q1', 'Q3']
gerar_tabela_imagem(stats_para_imagem, 'Estatísticas de Operação (Dados Corrigidos)', 'tabela_stats.png')


# --- 6. GERAÇÃO DOS GRÁFICOS (com nomes de arquivo corretos) ---
plt.style.use('seaborn-v0_8-whitegrid') # Volta para o estilo de gráfico

# Histograma da Potência Ativa
P_media = stats_descritivas.loc['Potência Ativa (kW)', 'Média']
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['potencia_ativa_kW'], bins=30, color=COR_ROXO, edgecolor='white', alpha=0.9)
ax.axvline(P_media, color=COR_TEAL, linestyle='--', linewidth=2.5, label=f'Potência Média: {P_media:.2f} kW')
ax.set_title('Distribuição da Potência Ativa Consumida', fontsize=16, fontweight='bold', color=COR_CINZA)
ax.set_xlabel('Potência Ativa (kW)', color=COR_CINZA)
ax.set_ylabel('Frequência de Ocorrências', color=COR_CINZA)
ax.legend()
plt.tight_layout()
plt.savefig('histograma_potencia_color.png', dpi=300)
plt.close(fig)
print("Gráfico 'histograma_potencia_color.png' gerado com sucesso.")

# Histograma do Fator de Potência
fp_medio = stats_descritivas.loc['Fator de Potência', 'Média']
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['fator_potencia'], bins=30, color=COR_TEAL, edgecolor='white', alpha=0.9)
ax.axvline(fp_medio, color=COR_ROXO, linestyle='--', linewidth=2.5, label=f'FP Médio: {fp_medio:.2f}')
ax.set_title('Distribuição do Fator de Potência', fontsize=16, fontweight='bold', color=COR_CINZA)
ax.set_xlabel('Fator de Potência', color=COR_CINZA)
ax.set_ylabel('Frequência de Ocorrências', color=COR_CINZA)
ax.legend()
plt.tight_layout()
plt.savefig('histograma_fp_color.png', dpi=300)
plt.close(fig)
print("Gráfico 'histograma_fp_color.png' gerado com sucesso.")

# Gráfico de Dispersão
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(df['potencia_ativa_kW'], df['fator_potencia'], c=df['fator_potencia'], cmap='viridis', alpha=0.6)
ax.set_title('Correlação entre Carga do Motor e Fator de Potência', fontsize=16, fontweight='bold', color=COR_CINZA)
ax.set_xlabel('Potência Ativa (kW)', color=COR_CINZA)
ax.set_ylabel('Fator de Potência', color=COR_CINZA)
cbar = plt.colorbar(scatter)
cbar.set_label('Nível do Fator de Potência')
plt.tight_layout()
plt.savefig('dispersao_potencia_fp_color.png', dpi=300)
plt.close(fig)
print("Gráfico 'dispersao_potencia_fp_color.png' gerado com sucesso.")

# Série Temporal das Médias Diárias
daily_stats = df[['potencia_ativa_kW', 'fator_potencia']].resample('D', on='data_hora').mean().dropna()
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.set_title('Médias Diárias de Potência Ativa e Fator de Potência', fontsize=16, fontweight='bold', color=COR_CINZA)
ax1.set_xlabel('Data', color=COR_CINZA)

# Eixo 1 para Potência Ativa
ax1.plot(daily_stats.index, daily_stats['potencia_ativa_kW'], color=COR_ROXO, marker='o', linestyle='-', label='Potência Ativa Média (kW)')
ax1.set_ylabel('Potência Ativa Média (kW)', color=COR_ROXO)
ax1.tick_params(axis='y', labelcolor=COR_ROXO)

# Eixo 2 para Fator de Potência
ax2 = ax1.twinx()
ax2.plot(daily_stats.index, daily_stats['fator_potencia'], color=COR_TEAL, marker='x', linestyle='--', label='Fator de Potência Médio')
ax2.set_ylabel('Fator de Potência Médio', color=COR_TEAL)
ax2.tick_params(axis='y', labelcolor=COR_TEAL)
ax2.set_ylim(0, 1.0) # FP vai de 0 a 1

# Formatação da data no eixo x
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
plt.gcf().autofmt_xdate() # Rotaciona as datas para melhor visualização

# Legendas
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='best')

plt.tight_layout()
plt.savefig('serie_temporal_color.png', dpi=300)
plt.close(fig)
print("Gráfico 'serie_temporal_color.png' gerado com sucesso.")
print("\nProcesso finalizado. Todos os arquivos de imagem foram criados/atualizados.")
