# Analises-Gastos-Eleicao-Rj-2026


Dashboard executivo focado em **auditoria financeira, rastreabilidade e inteligência de mercado** sobre os dados de prestação de contas das **Eleições de 2026** no Estado do Rio de Janeiro, utilizando dados abertos do Tribunal Superior Eleitoral (TSE).


O projeto implementa um pipeline completo de dados: desde a **Análise Exploratória (EDA)** em Python, passando por uma modelagem dimensional **Star Schema** otimizada em arquivos **Parquet**, até a camada visual focada em tomadas de decisão estratégicas.

https://github.com/user-attachments/assets/a1e18da7-94e9-4d0f-8cd1-81a10bfcfad0

---

## 🎯 Objetivos de Negócio

* **Governança & Transparência:** Auditar a dependência crônica de recursos públicos (Fundo Partidário/FEFC) em relação a aportes privados no RJ.
* **Eficiência de Alocação Capital:** Controlar o fluxo de caixa, saldos remanescentes e o *burn rate* (ritmo de gastos) das campanhas.
* **Mapeamento de Custos Críticos:** Categorizar as maiores rubricas operacionais (pessoal, marketing tradicional e tráfego pago).
* **Análise de Concentração Partidária:** Avaliar a dominância de mercado das principais legendas políticas do estado.

---

## 🔬 Engenharia de Dados & Análise Exploratória (EDA)

Antes da construção do dashboard, foi realizada uma etapa rigorosa de ingestão e higienização utilizando Python para tratar a volumetria massiva das tabelas brutas do TSE.

### ⚡ Otimização com Apache Parquet
Os arquivos originais em `.csv` foram convertidos para o formato colunar `.parquet` via `pyarrow`. 
* **Resultado:** Redução de **mais de 70% no espaço de armazenamento** e aceleração de **5x na velocidade de ingestão e atualização** do modelo no Power BI.

### 💻 Pipeline de EDA (Python)

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Carregamento otimizado de dados volumosos
df_receitas = pd.read_parquet("fato_receitas.parquet")
df_despesas = pd.read_parquet("fato_despesas.parquet")

# 1. Identificação de Outliers e Assimetria de Caixa
plt.figure(figsize=(10, 5))
sns.boxplot(x='tp_recurso', y='vr_receita', data=df_receitas, palette='Set2')
plt.title('Distribuição de Receita por Origem (Escala Logarítmica)')
plt.yscale('log')
plt.savefig('eda_boxplot_receitas.png')
plt.close()

# 2. Matriz de Sumarização: Arrecadação vs Despesas por Candidato
df_candidato_summary = df_receitas.groupby('sq_candidato')['vr_receita'].sum().to_frame().join(
    df_despesas.groupby('sq_candidato')['vr_despesa'].sum()
).fillna(0)
print(df_candidato_summary.describe())
```

### 🔍 Descobertas Críticas do EDA
* **Efeito Pareto (Cauda Longa):** Uma fração mínima de candidaturas majoritárias (como as lideradas por *Douglas Ruas* e *Eduardo Paes*) concentra a maior parte dos repasses dos diretórios nacionais.

---

## 📈 Insights da Versão 1.0 (Visão Executiva)

### 1. Origem dos Recursos
* **Predomínio Público:** **91,14%** (R$ 441,60 Mi) de todo o financiamento eleitoral fluminense provém do Fundão (FEFC), evidenciando a dependência do caixa estatal em relação ao capital privado (8,86% | R$ 42,93 Mi)

* <img width="4200" height="1500" alt="eda_dinheiro_publico" src="https://github.com/user-attachments/assets/e4aa18e6-7853-4e99-84ae-ed31db509400" />


### 2. Market Share Financeiro por Legenda (Top 5)

| Partido | Arrecadação Total | Despesas Contratadas | Cenário de Caixa |
| :--- | :---: | :---: | :--- |
| **PL** | R$ 112 Mi | R$ 75 Mi | Liderança isolada de captação |
| **PSD** | R$ 50 Mi | R$ 35 Mi | Segunda maior força do estado |
| **UNIÃO** | R$ 42 Mi | R$ 31 Mi | Alta retenção de saldo |
| **PT** | R$ 38 Mi | R$ 27 Mi | Equilíbrio operacional |
| **PP** | R$ 37 Mi | R$ 17 Mi | Maior margem de caixa livre |

### 3. O Mito do Marketing Digital Puro
Embora as ferramentas online tenham forte apelo visual, o tráfego pago (Impulsionamento de Conteúdo) consumiu **R$ 28 Milhões**. A engrenagem tradicional offline — **Despesas com Pessoal (R$ 63 Mi)** e **Militância/Mobilização de Rua (R$ 49 Mi)** — consome o **triplo** do orçamento digital.

<img width="4800" height="3600" alt="eda_despesas" src="https://github.com/user-attachments/assets/c352d255-b9fd-4a4b-a9ae-a441dfbe586a" />

---

## 🏗️ Arquitetura de Dados & Modelagem Técnica

O modelo foi estruturado em um padrão puramente dimensional **Star Schema (Esquema Estrela)** para garantir a eliminação de relacionamentos muitos-para-muitos e maximizar a performance das consultas DAX.


## 📐 Biblioteca de Métricas DAX

### 1. Indicadores de Volume e Fluxo de Caixa
```dax
Total Arrecadado = SUM(fato_receitas[vr_receita])

Total Despesas = SUM(fato_despesas[vr_despesa])

Saldo Campanha = [Total Arrecadado] - [Total Despesas]
```

### 2. Proporções Estruturais de Origem
```dax
% Verba Pública = 
DIVIDE(
    CALCULATE([Total Arrecadado], fato_receitas[tp_recurso] = "Público"),
    [Total Arrecadado],
    0
)
```

### 3. Inteligência de Mercado & Rankings Dinâmicos
```dax
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
```

---

## 🎨 Interface & UX Componentes

* **Visual Cards (KPIs):** Sumarização executiva no topo com os 4 principais indicadores macro.
* **Filtro Lateral Dinâmico:** Segmentação instantânea por fotos das principais lideranças (André Marinho, Anthony Garotinho, Cyro Garcia, Douglas Ruas e Eduardo Paes).
* **Gráficos Integrados:** Uso combinado de *Donut Chart* para receitas, colunas para comparativos partidários e um *Treemap* de alta densidade para distribuição de despesas.

---

## 🚀 Roadmap de Evolução (Fase 2)

- [ ] **Mapeamento de ROI (Pós-Eleição):** Assim que as urnas fecharem, integrar a base de Boletins de Urna para calcular a métrica de **Custo por Voto (ROI de Campanha)**.
- [ ] **Drill-Through de Fornecedores:** Permitir a abertura granular até o nível de CNPJ/CPF de empresas de publicidade contratadas.
- [ ] **Análise Temporal de Caixa:** Linha do tempo sequencial mostrando a velocidade de arrecadação versus o ritmo de queima de estoque/verba.

---

## 🛠️ Tecnologias Utilizadas

* **Business Intelligence:** Power BI Desktop & Camada DAX Avançada
* **Data Engineering & ETL:** Python 3.10 (`pandas`, `pyarrow`, `matplotlib`, `seaborn`)
* **Armazenamento:** Apache Parquet
