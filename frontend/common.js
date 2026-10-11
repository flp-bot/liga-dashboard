/**
 * LigaPokemon Common Utilities & SmartFetch Router
 */
if (typeof IS_LOCAL_SERVER === 'undefined') {
    var IS_LOCAL_SERVER = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
}

const LOCAL_SERVER_BASE = 'http://127.0.0.1:5050';

async function smartFetch(url, options = {}) {
    let cleanUrl = url.split('?')[0];
    if (!cleanUrl.startsWith('/')) {
        cleanUrl = '/' + cleanUrl;
    }

    // 1. If running on local server (localhost/127.0.0.1), use relative fetch
    if (IS_LOCAL_SERVER) {
        return fetch(url, options);
    }

    // 2. If opened via file:// or non-server hostname, try contacting local server http://127.0.0.1:5050
    if (window.location.protocol === 'file:' || !IS_LOCAL_SERVER) {
        try {
            const localUrl = LOCAL_SERVER_BASE + cleanUrl;
            const resp = await fetch(localUrl, { cache: 'no-store', ...options });
            if (resp.ok) return resp;
        } catch (e) {
            // Local server on 5050 is not reachable, fallback to static / localStorage handler
        }
    }

    const cloudMap = {
        '/api/latest': 'data/collection_latest.json',
        '/api/cards': 'data/cards_latest.json',
        '/api/costs': 'data/cards_costs.json',
        '/api/sales-config': 'data/sales_config.json',
        '/api/registered-stores': 'data/registered_stores.json',
        '/api/store-cards': 'data/store_cards_latest.json',
        '/api/history': 'data/history_log.json',
        '/api/card-history': 'data/cards_history.json',
        '/api/session-status': 'data/session_status.json'
    };

    if (options.method === 'POST') {
        if (cleanUrl === '/api/registered-stores') {
            try {
                const body = JSON.parse(options.body || '{}');
                if (body.stores && Array.isArray(body.stores)) {
                    localStorage.setItem('ligapokemon_registered_stores', JSON.stringify({ stores: body.stores }));
                }
            } catch (e) {}
            return new Response(JSON.stringify({ status: "success", mode: "web_local_storage" }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        if (cleanUrl === '/api/costs') {
            try {
                const body = JSON.parse(options.body || '{}');
                if (body.cards_costs) {
                    const localMap = JSON.parse(localStorage.getItem('ligapokemon_costs_paid') || '{}');
                    Object.assign(localMap, body.cards_costs);
                    localStorage.setItem('ligapokemon_costs_paid', JSON.stringify(localMap));
                }
                if (body.total_collection_cost !== undefined) {
                    localStorage.setItem('total_collection_cost_paid', body.total_collection_cost);
                }
            } catch (e) {}
            return new Response(JSON.stringify({ status: "success", mode: "web_local_storage" }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        if (cleanUrl === '/api/sales-config') {
            try {
                const body = JSON.parse(options.body || '{}');
                let currentConfig = JSON.parse(localStorage.getItem('ligapokemon_sales_config') || '{"sale_binder_ids":[]}');
                if (body.sale_binder_ids && Array.isArray(body.sale_binder_ids)) {
                    currentConfig.sale_binder_ids = body.sale_binder_ids.map(String);
                }
                if (body.toggle_binder_id) {
                    const bId = String(body.toggle_binder_id);
                    const set = new Set(currentConfig.sale_binder_ids || []);
                    if (set.has(bId)) set.delete(bId); else set.add(bId);
                    currentConfig.sale_binder_ids = Array.from(set);
                }
                localStorage.setItem('ligapokemon_sales_config', JSON.stringify(currentConfig));
            } catch (e) {}
            return new Response(JSON.stringify({ status: "success", mode: "web_local_storage" }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        return new Response(JSON.stringify({
            status: "busy",
            message: "Essa operação precisa ser iniciada com o servidor local ativo em http://127.0.0.1:5050."
        }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }

    // Check localStorage fallback for registered-stores
    if (cleanUrl === '/api/registered-stores') {
        const localStores = localStorage.getItem('ligapokemon_registered_stores');
        if (localStores) {
            try {
                return new Response(localStores, {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            } catch (e) {}
        }
    }

    const targetUrl = cloudMap[cleanUrl] || cleanUrl;
    const separator = targetUrl.includes('?') ? '&' : '?';
    const noCacheUrl = `${targetUrl}${separator}_t=${Date.now()}`;
    const fetchOptions = {
        cache: 'no-store',
        ...options,
        headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            ...(options.headers || {})
        }
    };

    try {
        const resp = await fetch(noCacheUrl, fetchOptions);
        if (resp.ok) return resp;
    } catch (e) {}

    return fetch(url, options);
}

/**
 * Currency Formatting Helper
 */
function formatBRL(value) {
    const val = parseFloat(value) || 0;
    return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

/**
 * Global Toast Notification System
 */
function showToast(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 99999; display: flex; flex-direction: column; gap: 10px; max-width: 360px; pointer-events: none;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.style.cssText = `
        pointer-events: auto;
        padding: 12px 18px;
        border-radius: 8px;
        color: #fff;
        font-size: 14px;
        font-family: system-ui, -apple-system, sans-serif;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.3s ease;
        opacity: 0;
        transform: translateY(20px);
    `;

    const bgMap = {
        success: 'linear-gradient(135deg, #10b981, #059669)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
        info: 'linear-gradient(135deg, #3b82f6, #2563eb)'
    };
    const iconMap = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.style.background = bgMap[type] || bgMap.info;
    toast.innerHTML = `<span>${iconMap[type] || 'ℹ️'}</span><span>${message}</span>`;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Loading Overlay Helper
 */
function showLoadingOverlay(message = 'Carregando dados...') {
    let overlay = document.getElementById('global-loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'global-loading-overlay';
        overlay.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(4px); z-index: 99998; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-family: system-ui, sans-serif; transition: opacity 0.3s ease;';
        overlay.innerHTML = `
            <div style="width: 48px; height: 48px; border: 4px solid rgba(255,255,255,0.2); border-top-color: #3b82f6; border-radius: 50%; animation: spinOverlay 0.8s linear infinite;"></div>
            <p id="global-loading-text" style="margin-top: 16px; font-size: 15px; font-weight: 500;"></p>
            <style>@keyframes spinOverlay { to { transform: rotate(360deg); } }</style>
        `;
        document.body.appendChild(overlay);
    }
    document.getElementById('global-loading-text').innerText = message;
    overlay.style.display = 'flex';
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('global-loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

