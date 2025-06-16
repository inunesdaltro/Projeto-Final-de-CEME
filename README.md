# Conversão de Energia e Máquinas Elétricas
O objetivo principal deste código é automatizar a análise de dados de um motor, transformando os dados brutos de um arquivo CSV em todos os resultados visuais necessários para o relatório.
# Análise de Desempenho e Sobrecarga de Motor de Indução

## Visão Geral do Projeto

Este projeto consiste em um estudo de caso realizado para a disciplina de **Conversão de Energia e Máquinas Elétricas (ENE0469)** da Universidade de Brasília (UnB). O objetivo é analisar o desempenho operacional de um conjunto motor-bomba no sistema de água gelada do Hospital Sarah Kubitschek, utilizando dados reais medidos em campo e dados nominais dos equipamentos.

A análise revelou uma condição de operação crítica e perigosa, onde o motor elétrico se encontra drasticamente subdimensionado para a carga, operando em um regime de sobrecarga severa e contínua.

## Principais Descobertas

* **Motor Identificado:** WEG W22 de **15 kW (20 CV)**.
* **Consumo Elétrico Medido:** O motor consome em média **48.51 kW** de potência ativa.
* **Diagnóstico Crítico:** O motor opera com uma **sobrecarga de aproximadamente 300%** de sua capacidade nominal.
* **Fator Agravante:** O sistema apresenta um **baixo fator de potência médio de 0.69**, o que aumenta a corrente de linha e o estresse térmico sobre o sistema.
* **Conclusão:** A condição de operação representa um **risco iminente de falha catastrófica** do motor, exigindo intervenção imediata da equipe de manutenção.

## Estrutura do Repositório

* `projetofinal.py`: Script principal em Python que realiza toda a análise dos dados.
* `bomba_centro_cirurgico.csv`: Arquivo com os dados brutos medidos no sistema.
* `Relatorio_Final.pdf`: (Opcional) O relatório final do trabalho, gerado a partir do código LaTeX.
* `/outputs/`: (Sugestão) Pasta para armazenar os 6 arquivos PNG gerados pelo script:
    * `tabela_stats.png`
    * `tabela_nominais.png`
    * `serie_temporal_color.png`
    * `dispersao_potencia_fp_color.png`
    * `histograma_potencia_color.png`
    * `histograma_fp_color.png`

## Como Executar o Código

### Requisitos

É necessário ter Python 3 instalado, juntamente com as seguintes bibliotecas:
* pandas
* numpy
* matplotlib

Você pode instalar todas as dependências com o seguinte comando:
```bash
pip install pandas numpy matplotlib
```

### Passos para Execução

1.  Clone este repositório para a sua máquina local.
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    ```
2.  Navegue até a pasta do projeto.
    ```bash
    cd <NOME_DA_PASTA_DO_PROJETO>
    ```
3.  Certifique-se de que o arquivo `bomba_centro_cirurgico.csv` está na mesma pasta que o script `projetofinal.py`.
4.  Execute o script a partir do seu terminal:
    ```bash
    python projetofinal.py
    ```
5.  Após a execução, os 6 arquivos de imagem (tabelas e gráficos) serão salvos na mesma pasta.
