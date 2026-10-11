# 🤖 AGENTS.md — Guia de Arquitetura e Contexto para Agentes IA

Bem-vindo ao repositório **LigaDashboard / LigaPokemon Scraper**!
Este documento serve como mapa arquitetural para agentes de IA entenderem rapidamente a estrutura do projeto, o fluxo de dados e os contratos de API.

---

## 📁 Mapa do Repositório

```
c:\liga\
├── AGENTS.md                  # 🤖 Este guia de arquitetura e contexto
├── README.md                  # 📘 Documentação de uso do usuário
├── config.py                  # ⚙️ Configurações globais, URLs e paths
├── firebase.json              # 🔥 Configurações do Firebase Hosting
├── .gitignore                 # 🙈 Regras de exclusão do Git
│
├── backend/                   # 🐍 Núcleo Python (Servidor & Scrapers)
│   ├── server.py              # Servidor HTTP / REST API (Porta 5050)
│   ├── database.py            # Camada de banco de dados (SQLite: data/liga.db)
│   ├── scraper.py             # Scraper de coleções pessoais da LigaPokemon (Playwright)
│   ├── store_scraper.py       # Scraper de cartas de lojas parceiras da LigaPokemon
│   ├── firebase_sync.py       # Sincronizador de dados com o Firebase Hosting
│   ├── update_card_images.py  # Gerador/Atualizador de imagens de cartas de novos conjuntos
│   └── fix_card_images.py     # Corretor de links e resolução de imagens de cartas
│
├── frontend/                  # 🌐 Interface Web e Assets
│   ├── index.html             # Página inicial / Redirecionamento
│   ├── dashboard.html         # Visão geral da coleção e gráficos
│   ├── collections.html       # Busca e listagem de cartas pessoais
│   ├── sales.html             # Painel de precificação e vendas
│   ├── stores.html            # Comparador de preços com lojas parceiras
│   ├── auth.css               # Estilos da interface e modais
│   ├── auth.js                # Lógica de sessão de usuário
│   ├── card-list-component.js # Componente customizado Web Component de lista de cartas
│   ├── card-modal.js          # Modal interativo de detalhes da carta
│   ├── card-image-resolver.js # Resoluções de imagens de cartas e sprites
│   └── common.js              # Utilitários JS comuns
│
├── scripts/                   # 🛠️ Scripts auxiliares e operacionais
│   ├── setup_session.py       # Login inicial no Chromium com salvamento de sessão/cookies
│   └── recalc_trends.py       # Recálculo de tendências históricas de preços
│
├── tools_scratch/             # 🧪 Scripts temporários, OCR e amostras de teste
│   ├── scratch_*.py           # Testes isolados de scrapers e template matching
│   ├── generate_*.py          # Utilitários de visualização de dígitos e cortes
│   └── price_*.png            # Amostras de recorte de preços para OCR
│
├── data/                      # 📊 Dados persistentes, exportações e banco de dados
│   ├── liga.db                # Banco de dados principal SQLite
│   ├── card-sets-map.json     # Mapeamento de coleções/conjuntos
│   ├── session_cookies.json   # Cookies de sessão autenticada da LigaPokemon
│   ├── collection_latest.csv  # Exportação CSV mais recente
│   └── collection_latest.json # Exportação JSON mais recente
│
└── Executáveis (.bat / .ps1 na raiz para acesso fácil no Windows Explorer):
    ├── run_now.bat            # Executa o scraper de coleção imediatamente
    ├── open_dashboard.bat     # Inicia o backend/server.py e abre o navegador
    ├── install_schedule.bat   # Agenda a execução diária no Windows Task Scheduler
    └── install_schedule.ps1   # Script PowerShell de agendamento diário
```

---

## 🔄 Fluxo de Dados e Arquitetura

1. **Autenticação & Sessão (`scripts/setup_session.py`)**:
   - Abre o Chromium via Playwright, permite login manual/automático e salva sessão em `user_data/` e `data/session_cookies.json`.

2. **Extração de Dados (`backend/scraper.py` & `backend/store_scraper.py`)**:
   - `scraper.py`: Coleta cartas da coleção do usuário na LigaPokemon, extrai valores/quantidades, grava no SQLite `data/liga.db` e exporta arquivos para `data/`.
   - `store_scraper.py`: Extrai cartas de lojas específicas e armazena na tabela de lojas do SQLite.

3. **Servidor REST & Backend (`backend/server.py`)**:
   - Roda um servidor HTTP nativo em Python na porta **5050**.
   - Servidor estático: serve páginas de `frontend/` e dados estáticos de `data/`.

4. **Interface Frontend (`frontend/`)**:
   - Desenvolvido em HTML5 Vanilla, Custom CSS e JavaScript nativo (Web Components sem dependências pesadas de framework).

---

## 🔌 Principais Endpoints da API REST (`http://127.0.0.1:5050`)

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/latest` | Retorna o resumo e métricas da coleção mais recente |
| `GET` | `/api/cards` | Retorna a lista completa de cartas registradas |
| `GET` | `/api/history` | Retorna o histórico do valor total e quantidade da coleção |
| `GET` | `/api/card-history` | Retorna histórico individual de preços por carta |
| `GET` | `/api/costs` | Retorna os preços de custo cadastrados para as cartas |
| `GET` | `/api/sales-config` | Retorna as configurações da calculadora de vendas |
| `GET` | `/api/registered-stores` | Retorna as lojas cadastradas para scraping |
| `GET` | `/api/store-cards` | Retorna as cartas raspadas de lojas parceiras |
| `POST` | `/api/run-scraper` | Inicia o `scraper.py` em segundo plano |
| `POST` | `/api/run-store-scraper` | Inicia o `store_scraper.py` em segundo plano |
| `POST` | `/api/login` | Inicia o fluxo de setup de login com o navegador |

---

## ⚠️ Regras e Diretrizes para Agentes IA

1. **Limpeza da Raiz**:
   - **NUNCA** crie arquivos temporários, PNGs, JPEGs ou scripts de rascunho na raiz `c:\liga\`.
   - Coloque arquivos temporários ou de teste em `tools_scratch/` ou em `data/`.

2. **Organização por Camadas**:
   - Códigos Python backend/scrapers ficam em `backend/`.
   - Modificações HTML/CSS/JS ficam em `frontend/`.
   - Scripts de agendamento/login ficam em `scripts/`.

3. **Compatibilidade de Caminhos**:
   - Sempre utilize a biblioteca `config.py` para obter diretórios (`config.BASE_DIR`, `config.BACKEND_DIR`, `config.FRONTEND_DIR`, `config.DATA_DIR`).
