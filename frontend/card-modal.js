/**
 * Reusable Card Price History Modal Component
 * LigaPokemon - Explorador de Coleções & Busca de Cartas
 */

(function () {
    // 1. Inject Styles
    if (!document.getElementById('card-modal-component-styles')) {
        const style = document.createElement('style');
        style.id = 'card-modal-component-styles';
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(9, 13, 22, 0.85);
                backdrop-filter: blur(14px);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                animation: fadeIn 0.25s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            .modal-card {
                background: rgba(26, 34, 52, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
                max-width: 860px;
                width: 100%;
                padding: 28px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
                animation: popUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                max-height: 92vh;
                overflow-y: auto;
            }

            @keyframes popUp {
                from { transform: scale(0.92); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }

            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .modal-icon {
                width: 44px;
                height: 44px;
                background: linear-gradient(135deg, var(--primary, #8b5cf6), var(--accent-pink, #ec4899));
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 16px rgba(139, 92, 246, 0.35);
            }

            .modal-close-btn {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: var(--text-muted, #94a3b8);
                width: 38px;
                height: 38px;
                border-radius: 50%;
                font-size: 1.4rem;
                line-height: 1;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
            }

            .modal-close-btn:hover {
                background: rgba(239, 68, 68, 0.25);
                color: #ef4444;
                border-color: rgba(239, 68, 68, 0.4);
            }

            .modal-badges-bar {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }

            .modal-controls-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
                margin-bottom: 20px;
            }

            .modal-toggle-group {
                display: flex;
                gap: 6px;
                background: rgba(15, 23, 42, 0.6);
                padding: 4px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            .modal-toggle-btn {
                background: transparent;
                border: none;
                color: var(--text-muted, #94a3b8);
                padding: 6px 14px;
                border-radius: 8px;
                font-size: 0.82rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .modal-toggle-btn.active {
                background: var(--primary, #8b5cf6);
                color: #fff;
                box-shadow: 0 2px 10px rgba(139, 92, 246, 0.35);
            }

            .modal-stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
                gap: 14px;
            }

            .modal-stat-box {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
                padding: 14px;
            }

            .modal-stat-label {
                font-size: 0.75rem;
                color: var(--text-muted, #94a3b8);
                text-transform: uppercase;
                font-weight: 600;
                margin-bottom: 4px;
            }

            .modal-stat-val {
                font-family: 'Outfit', sans-serif;
                font-size: 1.1rem;
                font-weight: 700;
            }

            .btn-google-search-modal {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 8px 14px;
                border-radius: 12px;
                background: linear-gradient(135deg, rgba(66, 133, 244, 0.22), rgba(234, 67, 53, 0.22));
                border: 1px solid rgba(66, 133, 244, 0.4);
                color: #93c5fd;
                font-size: 0.82rem;
                font-weight: 700;
                text-decoration: none;
                transition: all 0.25s ease;
            }

            .btn-google-search-modal:hover {
                background: linear-gradient(135deg, rgba(66, 133, 244, 0.45), rgba(234, 67, 53, 0.45));
                border-color: #60a5fa;
                color: #ffffff;
                transform: translateY(-2px);
            }

            .modal-card-img-wrap {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-shrink: 0;
            }

            .modal-card-img {
                width: 140px;
                height: 195px;
                border-radius: 12px;
                object-fit: cover;
                border: 2px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7), 0 0 24px rgba(139, 92, 246, 0.35);
                transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }

            .modal-card-img:hover {
                transform: scale(1.05) rotate(1deg);
            }
        `;
        document.head.appendChild(style);
    }

    // 2. Inject Modal HTML Component if missing
    window.ensureCardModalDOM = function () {
        if (document.getElementById('card-history-modal')) return document.getElementById('card-history-modal');

        const modalDiv = document.createElement('div');
        modalDiv.id = 'card-history-modal';
        modalDiv.className = 'modal-overlay';
        modalDiv.style.display = 'none';
        modalDiv.onclick = function (e) {
            if (e.target === this) closeCardHistoryModal();
        };

        modalDiv.innerHTML = `
            <div class="modal-card">
                <div class="modal-header">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div class="modal-icon">
                            <i data-lucide="trending-up" style="width: 24px; height: 24px; color: #fff;"></i>
                        </div>
                        <div>
                            <h2 id="modal-card-name" style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: #fff;">
                                Histórico do Card
                            </h2>
                            <p id="modal-card-sub" style="font-size: 0.85rem; color: var(--text-muted, #94a3b8);">
                                Carregando informações...
                            </p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <a id="modal-google-search-btn" href="#" target="_blank" rel="noopener noreferrer" class="btn-google-search-modal" title="Pesquisar no Google em outra aba">
                            <i data-lucide="search" style="width: 14px; height: 14px;"></i>
                            <span>Pesquisar no Google</span>
                            <i data-lucide="external-link" style="width: 12px; height: 12px;"></i>
                        </a>
                        <button class="modal-close-btn" onclick="closeCardHistoryModal()">&times;</button>
                    </div>
                </div>

                <!-- Badges Bar -->
                <div class="modal-badges-bar" id="modal-badges-bar"></div>

                <!-- Controls Row -->
                <div class="modal-controls-row">
                    <div class="modal-toggle-group">
                        <button class="modal-toggle-btn active" data-metric="all" onclick="changeChartMetric('all', this)">📊 Todos os Preços</button>
                        <button class="modal-toggle-btn" data-metric="avg" onclick="changeChartMetric('avg', this)">🟣 Preço Médio</button>
                        <button class="modal-toggle-btn" data-metric="min" onclick="changeChartMetric('min', this)">🔵 Mínimo</button>
                        <button class="modal-toggle-btn" data-metric="max" onclick="changeChartMetric('max', this)">💖 Máximo</button>
                    </div>

                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 0.8rem; color: var(--text-muted, #94a3b8);">Período:</span>
                        <select id="modal-period-select" class="select-filter" style="padding: 6px 12px; font-size: 0.82rem;" onchange="updateModalChartPeriod(this.value)">
                            <option value="14" selected>14 Dias</option>
                            <option value="7">7 Dias</option>
                            <option value="30">30 Dias</option>
                        </select>
                    </div>
                </div>

                <!-- Chart & Image Container -->
                <div style="display: flex; gap: 20px; align-items: stretch; margin-bottom: 20px; flex-wrap: wrap;">
                    <div id="modal-card-img-container" class="modal-card-img-wrap" style="display: none;">
                        <img id="modal-card-img-el" class="modal-card-img" src="" alt="Carta" />
                    </div>
                    <div style="flex: 1; min-width: 280px; position: relative; height: 320px;">
                        <canvas id="cardHistoryChart"></canvas>
                    </div>
                </div>

                <!-- Summary Stats Grid -->
                <div class="modal-stats-grid" id="modal-stats-grid"></div>
            </div>
        `;
        document.body.appendChild(modalDiv);
        return modalDiv;
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.ensureCardModalDOM);
    } else {
        window.ensureCardModalDOM();
    }
})();

// Global State
window.currentModalCardKey = window.currentModalCardKey || null;
window.currentModalMetric = window.currentModalMetric || 'all';
window.currentModalPeriod = window.currentModalPeriod || 14;
window.modalChartInstance = window.modalChartInstance || null;
window.cardHistoryMap = window.cardHistoryMap || {};

// Helper: Format BRL Fallback
function formatBRLFallback(val) {
    if (typeof window.formatBRL === 'function') {
        return window.formatBRL(val);
    }
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);
}

// Helper: Card Key Fallback
function getCardKeyFallback(card) {
    if (!card) return '';
    if (typeof window.getCardKey === 'function') {
        return window.getCardKey(card);
    }
    return `${card.binder_id || ''}_${card.card_name_en || card.card_name_pt}_${card.card_number}_${card.set_pt}_${card.quality}_${card.language}`;
}

// Get All Available Cards from Environment
function getAllAvailableCards() {
    if (window.allCardsData && Array.isArray(window.allCardsData) && window.allCardsData.length > 0) {
        return window.allCardsData;
    }
    if (typeof allCardsData !== 'undefined' && Array.isArray(allCardsData) && allCardsData.length > 0) {
        return allCardsData;
    }
    if (window.filteredCards && Array.isArray(window.filteredCards) && window.filteredCards.length > 0) {
        return window.filteredCards;
    }
    if (typeof filteredCards !== 'undefined' && Array.isArray(filteredCards) && filteredCards.length > 0) {
        return filteredCards;
    }
    return [];
}

// Fetch Card History API
async function fetchCardHistory() {
    try {
        const fetchFn = typeof window.smartFetch === 'function' ? window.smartFetch : fetch;
        const res = await fetchFn('/api/card-history');
        if (res.ok) {
            window.cardHistoryMap = await res.json();
        }
    } catch (e) {
        console.warn('Erro ao carregar histórico de preços:', e);
    }
}

// Open Modal Component
async function openCardHistoryModal(cardKey, cardsList = null) {
    window.currentModalCardKey = cardKey;

    const dataList = cardsList || getAllAvailableCards();
    let card = dataList.find(c => getCardKeyFallback(c) === cardKey || getCardKeyFallback(c) === decodeURIComponent(cardKey));

    if (!card) {
        // Fallback: search by matching parts or history entry
        card = dataList.find(c => {
            const k = getCardKeyFallback(c);
            return k && (k.includes(cardKey) || cardKey.includes(k));
        });
    }

    if (!card) {
        // Create basic card representation so modal never fails to open
        const parts = cardKey ? cardKey.split('_') : [];
        card = {
            card_name_pt: parts[1] || cardKey || 'Card',
            card_name_en: parts[1] || cardKey || 'Card',
            set_pt: parts[3] || 'Desconhecido',
            card_number: parts[2] || '',
            quality: parts[4] || 'NM',
            language: parts[5] || 'PT',
            binder_name: parts[0] ? `Pasta ${parts[0]}` : 'Coleção'
        };
    }

    if (!window.cardHistoryMap || Object.keys(window.cardHistoryMap).length === 0) {
        await fetchCardHistory();
    }

    const modal = window.ensureCardModalDOM ? window.ensureCardModalDOM() : document.getElementById('card-history-modal');
    if (modal) modal.style.display = 'flex';

    const cardName = card.card_name_pt || card.card_name_en || 'Card';
    const nameEl = document.getElementById('modal-card-name');
    const subEl = document.getElementById('modal-card-sub');
    if (nameEl) nameEl.textContent = cardName;
    if (subEl) {
        subEl.textContent = `${card.set_pt || ''} • #${card.card_number || ''} • ${card.quality || ''} • ${card.language || ''} • Pasta: ${card.binder_name || 'Coleção'}`;
    }

    const modalGoogleBtn = document.getElementById('modal-google-search-btn');
    if (modalGoogleBtn) {
        const searchQuery = `pokemon ${cardName} ${card.set_pt || ''} ${card.card_number || ''}`.trim();
        modalGoogleBtn.href = `https://www.google.com/search?tbm=isch&q=${encodeURIComponent(searchQuery)}`;
        modalGoogleBtn.title = `Pesquisar '${searchQuery}' no Google Imagens`;
    }

    // Badges Bar
    let costText = 'Sem Custo Cadastrado';
    if (typeof window.getCostPaidMap === 'function') {
        const costMap = window.getCostPaidMap();
        const costPaid = costMap[cardKey];
        if (costPaid !== undefined && costPaid !== null) {
            costText = `Custo Pago: ${formatBRLFallback(costPaid)}`;
        }
    } else {
        try {
            const costMap = JSON.parse(localStorage.getItem('ligapokemon_costs_paid') || '{}');
            const costPaid = costMap[cardKey];
            if (costPaid !== undefined && costPaid !== null) {
                costText = `Custo Pago: ${formatBRLFallback(costPaid)}`;
            }
        } catch (e) {}
    }

    const badgesBar = document.getElementById('modal-badges-bar');
    if (badgesBar) {
        badgesBar.innerHTML = `
            <span class="badge badge-set">${card.set_pt || 'Pokémon'}</span>
            <span class="badge badge-nm">${card.quality || 'NM'}</span>
            <span class="badge badge-binder">${card.binder_name || 'Coleção'}</span>
            <span class="badge" style="background: rgba(245, 158, 11, 0.2); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.3);">${costText}</span>
        `;
    }

    // Modal Card Image
    const imgContainer = document.getElementById('modal-card-img-container');
    const imgEl = document.getElementById('modal-card-img-el');
    if (imgContainer && imgEl) {
        let imgUrl = '';
        let fallbackStr = '';

        if (window.CardImageResolver && typeof window.CardImageResolver.getCardImageUrls === 'function') {
            const urls = window.CardImageResolver.getCardImageUrls(card);
            imgUrl = urls.high || urls.low;
            fallbackStr = urls.fallback || '';
        } else {
            imgUrl = card.image_high_url || card.image_url;
        }

        if (imgUrl) {
            imgEl.dataset.fallbacks = fallbackStr;
            imgEl.onerror = function() {
                if (window.CardImageResolver && typeof window.CardImageResolver.handleCardImgError === 'function') {
                    window.CardImageResolver.handleCardImgError(this);
                } else {
                    imgContainer.style.display = 'none';
                }
            };
            imgEl.src = imgUrl;
            imgEl.alt = cardName || 'Carta';
            imgContainer.style.display = 'flex';
        } else {
            imgContainer.style.display = 'none';
            imgEl.src = '';
        }
    }

    renderCardHistoryChart();
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }
}

// Close Modal
function closeCardHistoryModal() {
    const modal = document.getElementById('card-history-modal');
    if (modal) modal.style.display = 'none';
}

// Change Metric Toggle
function changeChartMetric(metric, btnEl) {
    window.currentModalMetric = metric;
    document.querySelectorAll('.modal-toggle-btn').forEach(btn => btn.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');
    renderCardHistoryChart();
}

// Update Period Selector
function updateModalChartPeriod(days) {
    window.currentModalPeriod = parseInt(days, 10) || 14;
    renderCardHistoryChart();
}

// Render Chart & Stats
function renderCardHistoryChart() {
    if (!window.currentModalCardKey) return;
    const dataList = getAllAvailableCards();
    let card = dataList.find(c => getCardKeyFallback(c) === window.currentModalCardKey);
    let historyPoints = (window.cardHistoryMap && window.cardHistoryMap[window.currentModalCardKey]) || [];

    if (historyPoints.length === 0 && card) {
        historyPoints = [{
            date: new Date().toISOString().split('T')[0],
            min: card.price_min_brl || 0,
            avg: card.price_avg_brl || 0,
            max: card.price_max_brl || 0
        }];
    }

    const slicedPoints = historyPoints.slice(-window.currentModalPeriod);
    const labels = slicedPoints.map(p => p.date);
    const minVals = slicedPoints.map(p => p.min || 0);
    const avgVals = slicedPoints.map(p => p.avg || 0);
    const maxVals = slicedPoints.map(p => p.max || 0);

    const canvas = document.getElementById('cardHistoryChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (window.modalChartInstance) window.modalChartInstance.destroy();

    const datasets = [];

    if (window.currentModalMetric === 'all' || window.currentModalMetric === 'avg') {
        datasets.push({
            label: 'Preço Médio (R$)',
            data: avgVals,
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.15)',
            borderWidth: 3,
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointHoverRadius: 7
        });
    }

    if (window.currentModalMetric === 'all' || window.currentModalMetric === 'min') {
        datasets.push({
            label: 'Preço Mínimo (R$)',
            data: minVals,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2.5,
            fill: false,
            tension: 0.35,
            pointRadius: 4
        });
    }

    if (window.currentModalMetric === 'all' || window.currentModalMetric === 'max') {
        datasets.push({
            label: 'Preço Máximo (R$)',
            data: maxVals,
            borderColor: '#ec4899',
            backgroundColor: 'rgba(236, 72, 153, 0.1)',
            borderWidth: 2.5,
            fill: false,
            tension: 0.35,
            pointRadius: 4
        });
    }

    window.modalChartInstance = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' } } },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${formatBRLFallback(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: {
                    ticks: {
                        color: '#94a3b8',
                        callback: function (val) { return formatBRLFallback(val); }
                    },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                }
            }
        }
    });

    // Update Summary Stats Grid in Modal
    const lastPoint = slicedPoints[slicedPoints.length - 1] || {};
    const firstPoint = slicedPoints[0] || {};
    const isSinglePoint = slicedPoints.length <= 1;
    const avgDiff = isSinglePoint ? 0 : (lastPoint.avg || 0) - (firstPoint.avg || 0);
    const avgPct = (!isSinglePoint && firstPoint.avg > 0) ? ((avgDiff / firstPoint.avg) * 100).toFixed(1) : "0.0";

    let variationHtml = `<span style="color: #94a3b8;">➖ R$ 0,00 (0.0%)</span>`;
    if (!isSinglePoint && avgDiff > 0) {
        variationHtml = `<span style="color: #34d399;">📈 +${formatBRLFallback(avgDiff)} (+${avgPct}%)</span>`;
    } else if (!isSinglePoint && avgDiff < 0) {
        variationHtml = `<span style="color: #f87171;">📉 ${formatBRLFallback(avgDiff)} (${avgPct}%)</span>`;
    }

    const statsGrid = document.getElementById('modal-stats-grid');
    if (statsGrid) {
        statsGrid.innerHTML = `
            <div class="modal-stat-box">
                <div class="modal-stat-label">Preço Mínimo Atual</div>
                <div class="modal-stat-val" style="color: #93c5fd;">${formatBRLFallback(lastPoint.min)}</div>
            </div>
            <div class="modal-stat-box">
                <div class="modal-stat-label">Preço Médio Atual</div>
                <div class="modal-stat-val" style="color: #c4b5fd;">${formatBRLFallback(lastPoint.avg)}</div>
            </div>
            <div class="modal-stat-box">
                <div class="modal-stat-label">Preço Máximo Atual</div>
                <div class="modal-stat-val" style="color: #f472b6;">${formatBRLFallback(lastPoint.max)}</div>
            </div>
            <div class="modal-stat-box">
                <div class="modal-stat-label">Variação (${slicedPoints.length} DIAS)</div>
                <div class="modal-stat-val">${variationHtml}</div>
            </div>
        `;
    }
}

// Keydown listener to close on ESC
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeCardHistoryModal();
});
