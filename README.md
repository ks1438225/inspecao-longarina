🔧 Sistema de Inspeção de Longarina (Cadeirinha)
Aplicação desenvolvida em Streamlit para registro, acompanhamento e exportação de inspeções de qualidade industrial de longarinas tipo “cadeirinha”.
Visão Geral
Este sistema permite:
Registrar inspeções com medições dimensionais
Validar automaticamente conformidade com tolerâncias
Armazenar dados em banco SQLite
Visualizar histórico com indicadores (KPIs)
Gerar relatórios em PDF
Acompanhar taxa de conformidade ao longo do tempo
Tecnologias Utilizadas
Python
Streamlit (interface web)
SQLite3 (banco de dados local)
Pandas (manipulação de dados)
ReportLab (geração de PDF)
Estrutura Esperada
📁 projeto/
│
├── app.py
├── inspecoes.db (gerado automaticamente)
└── imagens/
    ├── logo_aguia.png
    ├── passo1.png
    ├── passo2.png
    └── passo3.png
⚙️ Funcionalidades-
1. Registro de Inspeção
Entrada de dados:
Data e hora
Ordem de Produção (O.P.)
Inspetor
Medidas A, B, C, D, E
Verificação de bandeja (OK / NÃO)
Comprimento
Observações
Validação automática:
Cada medida possui valor nominal e tolerância
Status final:
OK (conforme)
NÃO OK (fora do padrão)
2.  Histórico e Análise
Exibição de todas as inspeções registradas
Indicadores principais:
Total de inspeções
Quantidade de conformes
Quantidade de não conformes
Taxa de conformidade (%)
Filtros:
Por Ordem de Produção
Por Status
Gráfico:
Evolução da conformidade por data
3. Exportação de Relatórios
Geração de PDF com:
Cabeçalho personalizado (logo + título)
Período selecionado
Tabela completa de inspeções
Permite selecionar:
Data inicial
Data final
Regras de Validação
Medida	Nominal	Tolerância
A	30.0	±0.5
B	70.0	±0.5
C	20.0	±0.5
D	20.0	±0.5
E	15.0	±0.5
A inspeção é considerada OK somente se:
Todas as medidas estiverem dentro da tolerância
A bandeja estiver marcada como OK
Banco de Dados
Tabela: inspecoes
Campos principais:
data
hora
op (Ordem de Produção)
inspetor
med_a a med_e
bandeja
comp
status
obs
criado_em
Como Executar
Instale as dependências:
pip install streamlit pandas reportlab
Execute o aplicativo:
streamlit run app.py
Acesse no navegador:
http://localhost:8501
Personalizações-
O sistema inclui:
Estilização CSS customizada
Layout responsivo em colunas
Cabeçalho com identidade visual
Script para navegação otimizada via teclado (Tab)
Observações:
O banco de dados é criado automaticamente na primeira execução
As imagens são opcionais, mas recomendadas para melhor usabilidade
O sistema é ideal para uso em chão de fábrica ou controle de qualidade
Autoria: Desenvolvido para controle de qualidade industrial, com foco em usabilidade, rastreabilidade e padronização de inspeções.
Desenvolvedora: Programadora Web Kauane Silva
