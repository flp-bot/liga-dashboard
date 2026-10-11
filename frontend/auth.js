/**
 * LigaPokemon Authentication Module
 * Manages session status, modal interactions, assisted/headless login and credential updates.
 */

let authState = {
    cookies_exist: false,
    cookies_count: 0,
    last_cookie_update: null,
    email: '',
    email_masked: '',
    task_state: {
        is_running: false,
        current_task: null,
        last_result: null
    }
};

if (typeof IS_LOCAL_SERVER === 'undefined') {
    var IS_LOCAL_SERVER = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
}

// smartFetch é gerenciado pelo common.js. Caso não esteja definido, usa fetch padrão.
if (typeof smartFetch === 'undefined') {
    var smartFetch = async function(url, options = {}) {
        return fetch(url, options);
    };
}


let authPollInterval = null;

function initAuth() {
    injectAuthModal();
    fetchSessionStatus();
    // Poll session status periodically
    setInterval(fetchSessionStatus, 15000);
}

function injectAuthModal() {
    if (document.getElementById('auth-modal-overlay')) return;

    const modalHTML = `
    <div class="auth-modal-overlay" id="auth-modal-overlay" onclick="handleBackdropClick(event)">
        <div class="auth-modal-card" id="auth-modal-card">
            <div class="auth-modal-header">
                <div class="auth-modal-title-group">
                    <div class="auth-modal-icon">
                        <i data-lucide="shield-check" style="width: 24px; height: 24px;"></i>
                    </div>
                    <div>
                        <h3 class="auth-modal-title">Conexão LigaPokemon</h3>
                        <p class="auth-modal-desc">Gerencie a sessão e sincronização da sua conta</p>
                    </div>
                </div>
                <button class="auth-modal-close" onclick="closeAuthModal()" title="Fechar">
                    <i data-lucide="x" style="width: 20px; height: 20px;"></i>
                </button>
            </div>

            <div class="auth-modal-body">
                <!-- Status Banner -->
                <div class="auth-status-box">
                    <div class="auth-status-info">
                        <h4>
                            <span class="status-dot" id="modal-status-dot"></span>
                            <span id="modal-status-title">Verificando sessão...</span>
                        </h4>
                        <p id="modal-status-subtitle">Carregando dados da conta...</p>
                    </div>
                    <button class="btn-action-secondary" id="btn-test-session" onclick="testSession()" style="padding: 8px 14px; font-size: 0.8rem;">
                        <i data-lucide="refresh-cw" id="icon-test-session" style="width: 14px; height: 14px;"></i>
                        <span>Testar Sessão</span>
                    </button>
                </div>

                <!-- Feedback Box -->
                <div class="auth-feedback-box" id="auth-feedback-box">
                    <i data-lucide="info" id="auth-feedback-icon" style="width: 18px; height: 18px; flex-shrink: 0;"></i>
                    <span id="auth-feedback-text"></span>
                </div>

                <!-- Action Buttons -->
                <div class="auth-actions-group">
                    <!-- Assisted Login (Open Browser) -->
                    <button class="btn-action-hero" id="btn-login-assisted" onclick="startLogin(false)">
                        <div class="action-hero-left">
                            <i data-lucide="external-link" style="width: 22px; height: 22px;"></i>
                            <div class="action-hero-text">
                                <h5>Conexão Assistida (Abrir Navegador)</h5>
                                <span>Abre a janela na tela para resolver Captchas e logar com 1 clique</span>
                            </div>
                        </div>
                        <i data-lucide="chevron-right" style="width: 18px; height: 18px;"></i>
                    </button>

                    <!-- Background Login -->
                    <button class="btn-action-secondary" id="btn-login-headless" onclick="startLogin(true)">
                        <div class="action-hero-left">
                            <i data-lucide="zap" style="width: 18px; height: 18px; color: var(--accent-pink);"></i>
                            <div class="action-hero-text">
                                <h5>Login em Segundo Plano</h5>
                                <span>Tenta autenticar direto usando as credenciais salvas</span>
                            </div>
                        </div>
                        <i data-lucide="chevron-right" style="width: 18px; height: 18px;"></i>
                    </button>
                </div>

                <!-- Accordion: Credentials -->
                <div class="auth-accordion">
                    <div class="auth-accordion-header" onclick="toggleCredentialsAccordion()">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <i data-lucide="key-round" style="width: 16px; height: 16px; color: #a78bfa;"></i>
                            <span>Alterar E-mail e Senha salvos</span>
                        </div>
                        <i data-lucide="chevron-down" id="accordion-chevron" style="width: 16px; height: 16px; transition: transform 0.25s;"></i>
                    </div>
                    <div class="auth-accordion-content" id="auth-accordion-content">
                        <div class="auth-input-group">
                            <label>E-mail LigaPokemon</label>
                            <input type="email" id="auth-input-email" class="auth-input" placeholder="seu-email@gmail.com" />
                        </div>
                        <div class="auth-input-group">
                            <label>Senha</label>
                            <div class="auth-input-wrapper">
                                <input type="password" id="auth-input-pass" class="auth-input" placeholder="Digite sua senha" />
                                <button type="button" class="auth-input-toggle-pass" onclick="togglePasswordVisibility()">
                                    <i data-lucide="eye" id="icon-pass-eye" style="width: 16px; height: 16px;"></i>
                                </button>
                            </div>
                        </div>
                        <button class="btn-action-secondary" id="btn-save-creds" onclick="saveCredentials()" style="justify-content: center; background: rgba(139, 92, 246, 0.2); border-color: rgba(139, 92, 246, 0.4); margin-top: 4px;">
                            <i data-lucide="save" style="width: 16px; height: 16px;"></i>
                            <span>Salvar Credenciais</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

function handleBackdropClick(e) {
    if (e.target && e.target.id === 'auth-modal-overlay') {
        closeAuthModal();
    }
}

function openAuthModal() {
    const overlay = document.getElementById('auth-modal-overlay');
    if (overlay) {
        overlay.classList.add('active');
        fetchSessionStatus();
    }
}

function closeAuthModal() {
    const overlay = document.getElementById('auth-modal-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

function toggleCredentialsAccordion() {
    const content = document.getElementById('auth-accordion-content');
    const chevron = document.getElementById('accordion-chevron');
    if (content) {
        const isOpen = content.classList.contains('open');
        if (isOpen) {
            content.classList.remove('open');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
        } else {
            content.classList.add('open');
            if (chevron) chevron.style.transform = 'rotate(180deg)';
            const emailInput = document.getElementById('auth-input-email');
            if (emailInput && !emailInput.value && authState.email) {
                emailInput.value = authState.email;
            }
        }
    }
}

function togglePasswordVisibility() {
    const input = document.getElementById('auth-input-pass');
    const icon = document.getElementById('icon-pass-eye');
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) icon.setAttribute('data-lucide', 'eye-off');
    } else {
        input.type = 'password';
        if (icon) icon.setAttribute('data-lucide', 'eye');
    }
    if (window.lucide) window.lucide.createIcons();
}

function showFeedback(text, type = 'info', iconName = 'info') {
    const box = document.getElementById('auth-feedback-box');
    const textElem = document.getElementById('auth-feedback-text');
    const iconElem = document.getElementById('auth-feedback-icon');
    if (!box || !textElem) return;

    box.className = `auth-feedback-box active auth-feedback-${type}`;
    textElem.textContent = text;
    if (iconElem) {
        iconElem.setAttribute('data-lucide', iconName);
        if (type === 'info' && iconName === 'loader') {
            iconElem.classList.add('spinning-icon');
        } else {
            iconElem.classList.remove('spinning-icon');
        }
    }
    if (window.lucide) window.lucide.createIcons();
}

function hideFeedback() {
    const box = document.getElementById('auth-feedback-box');
    if (box) box.classList.remove('active');
}

let failedFetchCount = 0;

async function fetchSessionStatus() {
    try {
        const res = await smartFetch('/api/session-status');
        if (!res.ok) return;
        const data = await res.json();
        failedFetchCount = 0;
        authState = data;
        updateUI();

        // If a task is currently running, poll faster
        if (data.task_state && data.task_state.is_running) {
            if (!authPollInterval) {
                authPollInterval = setInterval(fetchSessionStatus, 2000);
            }
        } else {
            if (authPollInterval) {
                clearInterval(authPollInterval);
                authPollInterval = null;
            }
        }
    } catch (e) {
        failedFetchCount++;
        // Se falhar mais de 3 vezes seguidas, indica reconectando
        if (failedFetchCount >= 3) {
            const dot = document.getElementById('session-dot');
            const text = document.getElementById('session-status-text');
            if (dot) dot.className = 'status-dot dot-amber';
            if (text) text.textContent = 'Liga: Reconectando...';
        }
    }
}

function updateUI() {
    const dot = document.getElementById('session-dot');
    const text = document.getElementById('session-status-text');
    const modalDot = document.getElementById('modal-status-dot');
    const modalTitle = document.getElementById('modal-status-title');
    const modalSubtitle = document.getElementById('modal-status-subtitle');

    const isRunning = authState.task_state && authState.task_state.is_running;
    const currentTask = authState.task_state ? authState.task_state.current_task : null;

    // Set Header status
    if (isRunning) {
        if (dot) dot.className = 'status-dot dot-amber';
        if (text) text.textContent = `Liga: ${currentTask === 'login' ? 'Conectando...' : 'Ocupado'}`;
    } else if (authState.cookies_exist) {
        if (dot) dot.className = 'status-dot dot-green';
        if (text) text.textContent = 'Liga: Conectado';
    } else {
        if (dot) dot.className = 'status-dot dot-red';
        if (text) text.textContent = 'Liga: Desconectado';
    }

    // Set Modal status
    if (modalDot && modalTitle && modalSubtitle) {
        if (isRunning) {
            modalDot.className = 'status-dot dot-amber';
            modalTitle.textContent = currentTask === 'login' ? 'Autenticação em Andamento...' : 'Tarefa em Execução...';
            modalSubtitle.textContent = 'Aguarde a finalização do processo.';
            showFeedback('Operação em andamento no navegador. Por favor, aguarde...', 'info', 'loader');
            disableButtons(true);
        } else {
            disableButtons(false);
            if (authState.cookies_exist) {
                modalDot.className = 'status-dot dot-green';
                modalTitle.textContent = `Sessão Salva (${authState.email_masked || 'Ativa'})`;
                modalSubtitle.textContent = authState.last_cookie_update 
                    ? `Última sincronização: ${authState.last_cookie_update}` 
                    : 'Cookies gravados.';
            } else {
                modalDot.className = 'status-dot dot-red';
                modalTitle.textContent = 'Sessão Não Encontrada';
                modalSubtitle.textContent = 'Realize o login para permitir a sincronização automática.';
            }

            // Check if there was a recent result
            const lastRes = authState.task_state ? authState.task_state.last_result : null;
            if (lastRes) {
                if (lastRes.success || lastRes.logged_in) {
                    showFeedback(lastRes.message || 'Sessão validada com sucesso!', 'success', 'check-circle');
                } else {
                    showFeedback(lastRes.message || 'Aviso na verificação de sessão.', 'warning', 'alert-triangle');
                }
            }
        }
    }
}

function disableButtons(disabled) {
    const btnAssisted = document.getElementById('btn-login-assisted');
    const btnHeadless = document.getElementById('btn-login-headless');
    const btnTest = document.getElementById('btn-test-session');
    const btnSave = document.getElementById('btn-save-creds');

    if (btnAssisted) btnAssisted.disabled = disabled;
    if (btnHeadless) btnHeadless.disabled = disabled;
    if (btnTest) btnTest.disabled = disabled;
    if (btnSave) btnSave.disabled = disabled;
}

async function startLogin(headless = false) {
    showFeedback(
        headless ? 'Iniciando login em segundo plano...' : 'Abrindo navegador na sua tela para autenticação...', 
        'info', 
        'loader'
    );
    disableButtons(true);

    try {
        const res = await smartFetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ headless: headless })
        });
        const data = await res.json();
        
        if (res.ok) {
            showFeedback(data.message || 'Processo de login iniciado!', 'info', 'loader');
            fetchSessionStatus();
        } else {
            showFeedback(data.message || 'Erro ao iniciar login.', 'error', 'alert-circle');
            disableButtons(false);
        }
    } catch (err) {
        showFeedback(`Erro ao conectar ao servidor: ${err.message}`, 'error', 'alert-circle');
        disableButtons(false);
    }
}

async function testSession() {
    const icon = document.getElementById('icon-test-session');
    if (icon) icon.classList.add('spinning-icon');
    showFeedback('Verificando se a sessão atual continua autenticada na Liga...', 'info', 'loader');
    disableButtons(true);

    try {
        const res = await smartFetch('/api/check-session', { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            fetchSessionStatus();
        } else {
            showFeedback(data.message || 'Erro ao checar sessão.', 'error', 'alert-circle');
            disableButtons(false);
        }
    } catch (err) {
        showFeedback(`Erro de comunicação: ${err.message}`, 'error', 'alert-circle');
        disableButtons(false);
    } finally {
        if (icon) icon.classList.remove('spinning-icon');
    }
}

async function saveCredentials() {
    const emailInput = document.getElementById('auth-input-email');
    const passInput = document.getElementById('auth-input-pass');

    const email = emailInput ? emailInput.value.trim() : '';
    const password = passInput ? passInput.value.trim() : '';

    if (!email || !password) {
        showFeedback('Preencha tanto o e-mail quanto a senha para salvar.', 'warning', 'alert-triangle');
        return;
    }

    showFeedback('Salvando credenciais...', 'info', 'loader');

    try {
        const res = await smartFetch('/api/save-credentials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (res.ok) {
            showFeedback('Credenciais salvas com sucesso! Você já pode realizar o login.', 'success', 'check-circle');
            fetchSessionStatus();
        } else {
            showFeedback(data.message || 'Erro ao salvar credenciais.', 'error', 'alert-circle');
        }
    } catch (err) {
        showFeedback(`Erro ao salvar: ${err.message}`, 'error', 'alert-circle');
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuth);
} else {
    initAuth();
}
