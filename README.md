# Scraper Diário da Coleção LigaPokemon

Este projeto automatiza a leitura e exportação diária das suas cartas e coleções do site [LigaPokemon](https://www.ligapokemon.com.br/?view=colecao/colecao).

## 📁 Estrutura de Arquivos

```
c:\liga\
├── config.py              # Configurações de login, URLs e caminhos
├── setup_session.py       # Script de login e persistência inicial de sessão/cookies
├── scraper.py             # Script principal que extrai a coleção e gera relatórios
├── run_now.bat            # Arquivo executável para rodar o scraper manualmente
├── install_schedule.bat   # Script para agendar a execução diária no Windows (Task Scheduler)
├── README.md              # Guia de uso e instruções
├── user_data/             # Perfil e cookies persistidos do navegador
└── data/                  # Diretório de exportações geradas (CSV, JSON, logs)
    ├── collection_latest.csv
    ├── collection_latest.json
    ├── collection_YYYY-MM-DD.csv
    └── history_log.csv
```

---

## 🚀 Como Usar

### 1. Configuração Inicial da Sessão (Apenas 1ª vez)

Devido ao sistema de verificação por Captcha na tela de login da LigaPokemon, o scraper utiliza um perfil persistente de navegador (`user_data/`). 

Execute o comando no terminal:
```bash
python setup_session.py
```
*O script irá abrir o navegador, realizar a autenticação e salvar a sessão.*

---

### 2. Executando o Scraper Manualmente

Para rodar a leitura da coleção imediatamente a qualquer momento:
- Dê um duplo clique no arquivo **`run_now.bat`**  
ou rode no terminal:
```bash
python scraper.py
```

Os dados extraídos estarão disponíveis no diretório `data/`:
- `data/collection_latest.csv`: Coleção completa legível no Excel.
- `data/collection_latest.json`: Coleção estruturada em formato JSON.
- `data/history_log.csv`: Histórico do número total de cartas e valor ao longo dos dias.

---

### 3. Ativando o Agendador Diário no Windows

Para rodar automaticamente todos os dias às **08:00 AM**:
1. Clique com o botão direito no arquivo **`install_schedule.bat`** e escolha **Executar como Administrador**.
2. A tarefa `LigaPokemonScraper` será criada no **Agendador de Tarefas do Windows**.

Para alterar o horário de execução, edite a opção `/ST 08:00` no arquivo `install_schedule.bat`.
