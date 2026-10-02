# Analises-Gastos-Eleicao-Rj-2026

📊 Painel de Auditoria de Finanças Eleitorais — Rio de Janeiro 2026

Dashboard executivo desenvolvido em Power BI para auditoria, rastreabilidade e análise estratégica dos dados de prestação de contas das Eleições de 2026 no Estado do Rio de Janeiro (TSE).

O projeto combina um pipeline de Análise Exploratória de Dados (EDA) em Python, uma arquitetura dimensional em Star Schema de alta performance e uma interface focada em inteligência financeira para tomada de decisão em nível executivo.

🎯 Objetivos de Negócio

Transparência e Governança: Auditar o volume de recursos públicos (Fundo Partidário / FEFC) versus aportes privados nas campanhas do RJ.

Análise Média de Ticket de Campanha: Identificar a eficiência na alocação de receitas e controlar os saldos financeiros remanescentes.

Mapeamento de Gastos Críticos: Categorizar as maiores rubricas de despesas (pessoal, militância, marketing e serviços terceirizados).

Comparativo Partidário: Avaliar a concentração de recursos e gastos entre as principais legendas políticas do estado.

🔬 Análise Exploratória de Dados (EDA) & Pré-Processamento

Antes da construção da camada visual no Power BI, foi realizada uma etapa rigorosa de EDA (Exploratory Data Analysis) utilizando Python (pandas, seaborn, matplotlib, pyarrow) sobre os dados brutos extraídos do portal do TSE.

1. Principais Validações e Limpeza

Tratamento de Nulos e Inconsistências: Mapeamento de doadores/fornecedores sem identificação (CPF/CNPJ) e imputação de categorias padrão.

Integridade Referencial: Garantia de que todos os candidatos presentes nas tabelas de receita e despesa existiam na dimensão dim_candidato.

Otimização de Performance: Conversão dos dados originais em .csv para o formato colunar .parquet, reduzindo o volume de armazenamento em mais de 70% e acelerando a ingestão no Power BI.

2. Exemplos de Código & Análises do EDA (Python)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Carregamento otimizado dos dados em formato Parquet
df_receitas = pd.read_parquet("fato_receitas.parquet")
df_despesas = pd.read_parquet("fato_despesas.parquet")

# 1. Distribuição e Identificação de Outliers (Boxplot de Receitas por Origem)
plt.figure(figsize=(10, 5))
sns.boxplot(x='tp_recurso', y='vr_receita', data=df_receitas, palette='Set2')
plt.title('Distribuição do Valor de Receita por Tipo de Recurso (Público vs Privado)')
plt.yscale('log') # Escala logarítmica devido à alta assimetria
plt.savefig('eda_boxplot_receitas.png')
plt.close()

# 2. Matriz de Sumarização entre Arrecadação e Despesas por Candidato
df_candidato_summary = df_receitas.groupby('sq_candidato')['vr_receita'].sum().to_frame().join(
    df_despesas.groupby('sq_candidato')['vr_despesa'].sum()
).fillna(0)

print("Estatísticas Descritivas (Arrecadação vs Despesas):")
print(df_candidato_summary.describe())

# 3. Top 10 Categorias de Gastos mais Frequentes vs Mais Volumosas
top_gastos = df_despesas.groupby('ds_despesa')['vr_despesa'].agg(['sum', 'count', 'mean']).sort_values(by='sum', ascending=False)
print("\nTop Categorias de Despesas:")
print(top_gastos.head(10))


3. Principais Descobertas do EDA

Assimetria Severa (Cauda Longa): A distribuição de recursos segue uma regra de Pareto acentuada, onde uma pequena porcentagem de candidaturas concentra a maioria das verbas partidárias.

Outliers Extremos: Presença de doações pontuais de elevado valor concentradas no início do período eleitoral.

Elevada Concentração de Categorias: Mais de 60% do volume total de despesas está concentrado em apenas 4 categorias operacionais.

📈 Insights da Versão 1.0 (Análise Executiva)

Com base no modelo consolidado, destacam-se os seguintes indicadores macro para o cenário eleitoral do Rio de Janeiro:

1. Origem dos Recursos (Receitas)

Predomínio do Capital Público: $91{,}14\%$ (R$ 441,60 Mi) de todos os recursos arrecadados provêm de verbas públicas (FEFC/Fundo Partidário), enquanto a verba privada representa apenas $8{,}86\%$ (R$ 42,93 Mi).

Dependência Partidária: A maioria esmagadora das candidaturas opera sob dependência direta dos repasses dos diretórios centrais.

2. Arrecadação vs. Despesas por Partido (Top 10)

Liderança em Volume: O PL (R$ 112 Mi arrecadados / R$ 75 Mi gastos) e o PSD (R$ 50 Mi arrecadados / R$ 35 Mi gastos) lideram a movimentação financeira no estado.

Capacidade Financeira: As legendas UNIÃO (R$ 42 Mi / R$ 31 Mi), PT (R$ 38 Mi / R$ 27 Mi) e PP (R$ 37 Mi / R$ 17 Mi) completam o bloco principal com saldos remanescentes relevantes.

3. Matriz de Despesas Operacionais

Gargalos Operacionais: A maior fatia das despesas contratadas está concentrada em Despesas com Pessoal (R$ 63 Mi) e Atividades de Militância e Mobilização de Rua (R$ 49 Mi).

Comunicação e Propaganda: A soma de Publicidade por Impressos (R$ 45 Mi) e Impulsionamento de Conteúdo Digital (R$ 28 Mi) evidencia o equilíbrio entre o marketing tradicional e o digital.

🏗️ Arquitetura de Dados & Modelagem Técnica

O modelo foi projetado seguindo o padrão Star Schema (Esquema Estrela) para garantir elevada performance em consultas DAX e escalabilidade.

                  ┌───────────────────┐
                  │   dim_candidato   │
                  └─────────┬─────────┘
                            │
              ┌─────────────┴─────────────┐
              │ 1                         │ 1
              ▼ *                         ▼ *
    ┌───────────────────┐       ┌───────────────────┐
    │   fato_receitas   │       │   fato_despesas   │
    └───────────────────┘       └───────────────────┘
              ▲                           ▲
              │ *                         │ *
              └─────────────┬─────────────┘
                            │ 1
                  ┌─────────┴─────────┐
                  │    dim_doador     │
                  └───────────────────┘


📐 Biblioteca de Métricas DAX

Abaixo estão apresentados os exemplos de cálculos e fórmulas DAX implementados na camada analítica do dashboard:

1. Indicadores de Volume e Saldo (KPIs Básicos)

// Total de Arrecadação de Campanhas
Total Arrecadado = 
SUM(fato_receitas[vr_receita])

// Total de Despesas Contratadas
Total Despesas = 
SUM(fato_despesas[vr_despesa])

// Saldo Líquido de Campanha
Saldo Campanha = 
[Total Arrecadado] - [Total Despesas]


2. Indicadores Estruturais e Proporcionais

// Proporção de Verba Pública
% Verba Pública = 
DIVIDE(
    CALCULATE([Total Arrecadado], fato_receitas[tp_recurso] = "Público"),
    [Total Arrecadado],
    0
)

// Proporção de Verba Privada
% Verba Privada = 
DIVIDE(
    CALCULATE([Total Arrecadado], fato_receitas[tp_recurso] = "Privado"),
    [Total Arrecadado],
    0
)


3. Métricas Médias e Avançadas (Analytics & Rankings)

// Ticket Médio de Arrecadação por Candidato
Ticket Médio Arrecadado = 
DIVIDE(
    [Total Arrecadado],
    DISTINCTCOUNT(dim_candidato[sq_candidato]),
    0
)

// Ranking Dinâmico de Partidos por Arrecadação
Rank Partido Arrecadacao = 
IF(
    HASONEVALUE(dim_candidato[sg_partido]),
    RANKX(
        ALL(dim_candidato[sg_partido]),
        [Total Arrecadado],
        ,
        DESC,
        Dense
    )
)

// Média de Gastos por Categoria de Despesa
Média Gasto por Categoria = 
AVERAGEX(
    VALUES(fato_despesas[ds_despesa]),
    [Total Despesas]
)


🎨 Layout e Componentes da Interface

Elemento

Descrição e Funcionalidade

KPI Cards (Topo)

Exibição do Total Arrecadado (R$ 484,53 Mi), Total em Despesas (R$ 299,64 Mi), % Verba Pública ($91{,}14\%$) e Saldo de Campanha (R$ 184,89 Mi).

Slicer Lateral

Menu vertical dinâmico com fotos dos candidatos para filtragem instantânea do painel.

Gráfico Donut

Proporção entre Recursos Públicos e Privados.

Gráfico de Colunas

Arrecadação vs. Despesas por Partido (Top 10).

Bar Chart & Treemap

Ranqueamento das principais categorias de custos e mapa de árvore de distribuição de gastos.

🚀 Roadmap & Próximos Passos (Versão 2.0)

Esta entrega compreende a Versão 1.0 (Visão Executiva Macro). O projeto prevê as seguintes expansões para os próximos ciclos de atualização:

[ ] Módulo de Análise Triangular: Mapeamento cruzado de relações entre doadores de campanha, candidatos e fornecedores finais.

[ ] Drill-Through por CNPJ/CPF: Detalhamento granular de notas fiscais e empresas prestadoras de serviço contratadas por campanha.

[ ] Visão Temporal de Fluxo de Caixa: Evolução diária/semanal da entrada de receitas e liquidação de despesas ao longo do período eleitoral.

🛠️ Tecnologias Utilizadas

Business Intelligence: Power BI Desktop

Linguagem de Análise: DAX (Data Analysis Expressions)

Análise de Dados & ETL: Python (pandas, seaborn, pyarrow)

Formato de Arquivos: Parquet & CSV
