# LigaDashboard — Scraper & Dashboard da Coleção LigaPokemon

Este projeto automatiza a leitura, histórico, gerenciamento de vendas e comparação de preços da sua coleção de cartas do site [LigaPokemon](https://www.ligapokemon.com.br/).

---

## 📁 Estrutura do Projeto

```
c:\liga\
├── AGENTS.md                  # Guia de arquitetura e contexto para Agentes IA
├── README.md                  # Este guia do usuário
├── config.py                  # Configurações globais e paths
├── backend/                   # Servidor REST (server.py), Banco SQLite (database.py) e Scrapers
├── frontend/                  # Páginas HTML, CSS e Componentes JavaScript
├── scripts/                   # Scripts auxiliares (setup_session.py, etc.)
├── tools_scratch/             # Scripts temporários e testes isolados
├── data/                      # Banco de dados (liga.db) e exportações CSV/JSON
├── open_dashboard.bat         # Executável para abrir o Dashboard Web
├── run_now.bat                # Executável para rodar o scraper manualmente
└── install_schedule.bat       # Script para agendar a execução diária no Windows
```

---

## 🚀 Como Usar

### 1. Abrir o Dashboard Web
Para visualizar o Dashboard com gráficos, tendências e precificação:
- Dê um duplo clique no arquivo **`open_dashboard.bat`**
- Acesse no seu navegador: `http://127.0.0.1:5050`

---

### 2. Configuração Inicial da Sessão (Apenas 1ª vez)
Devido ao Captcha na tela de login da LigaPokemon, o scraper utiliza um perfil persistente de navegador (`user_data/`).

Pelo Dashboard em `http://127.0.0.1:5050`, clique em **Conectar Conta** ou execute via terminal:
```bash
python scripts/setup_session.py
```

---

### 3. Executando o Scraper Manualmente
Para atualizar sua coleção imediatamente:
- Dê um duplo clique no arquivo **`run_now.bat`**  
ou rode no terminal:
```bash
python backend/scraper.py
```

---

### 4. Agendador Diário no Windows
Para agendar a execução diária às **20:00**:
1. Execute **`install_schedule.bat`** como Administrador.
2. A tarefa `LigaPokemonScraper` será configurada no Agendador de Tarefas do Windows.

