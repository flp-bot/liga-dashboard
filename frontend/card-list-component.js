/**
 * Unified Card List Component & Renderer
 * Shared between collections.html and sales.html for LigaPokemon Explorer
 */

(function () {
    // 1. Inject Shared CSS Styles
    if (!document.getElementById('card-list-component-styles')) {
        const style = document.createElement('style');
        style.id = 'card-list-component-styles';
        style.textContent = `
        /* Shared Card List & Table Styles */
        .cards-grid-2x2 {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
            margin-bottom: 24px;
            width: 100%;
        }

        @media (max-width: 960px) {
            .cards-grid-2x2 {
                grid-template-columns: minmax(0, 1fr);
            }
        }

        .grid-card-item {
            background: rgba(26, 34, 52, 0.75);
            border: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
            border-radius: 18px;
            padding: 16px;
            display: flex;
            gap: 16px;
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease, box-shadow 0.25s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
            min-width: 0;
            width: 100%;
        }

        .grid-card-item:hover {
            transform: translateY(-3px);
            border-color: rgba(139, 92, 246, 0.5);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px var(--primary-glow, rgba(139, 92, 246, 0.35));
        }

        .grid-card-photo-side {
            width: 110px;
            min-width: 110px;
            max-width: 110px;
            height: 154px;
            min-height: 154px;
            max-height: 154px;
            border-radius: 12px;
            overflow: hidden;
            flex-shrink: 0;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .grid-card-photo-side img {
            width: 100% !important;
            height: 100% !important;
            max-width: 100% !important;
            max-height: 100% !important;
            object-fit: cover !important;
            transition: transform 0.3s ease;
            display: block !important;
        }

        .grid-card-item:hover .grid-card-photo-side img {
            transform: scale(1.08);
        }

        .grid-card-photo-placeholder {
            font-size: 2.2rem;
            color: var(--text-muted, #94a3b8);
            opacity: 0.6;
        }

        .grid-card-info-side {
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .grid-card-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 6px;
        }

        .grid-card-name {
            font-family: 'Outfit', sans-serif;
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.3;
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .grid-card-name:hover {
            color: #c4b5fd;
        }

        .grid-card-sub {
            font-size: 0.78rem;
            color: var(--text-muted, #94a3b8);
            margin-bottom: 8px;
        }

        .grid-card-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 10px;
        }

        .grid-card-prices-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            background: rgba(15, 23, 42, 0.55);
            padding: 8px 10px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 10px;
        }

        .grid-price-item {
            display: flex;
            flex-direction: column;
        }

        .grid-price-label {
            font-size: 0.68rem;
            color: var(--text-muted, #94a3b8);
            text-transform: uppercase;
            font-weight: 600;
        }

        .grid-price-val {
            font-family: 'Outfit', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
        }

        .grid-card-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding-top: 6px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }

        /* Google Search Button */
        .btn-google-search {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 6px;
            border-radius: 6px;
            background: rgba(66, 133, 244, 0.14);
            border: 1px solid rgba(66, 133, 244, 0.35);
            color: #93c5fd;
            font-size: 0.72rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            white-space: nowrap;
        }

        .btn-google-search:hover {
            background: rgba(66, 133, 244, 0.3);
            border-color: #60a5fa;
            color: #ffffff;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(66, 133, 244, 0.35);
        }

        /* Badges */
        .badge {
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 3px;
            line-height: 1.2;
        }

        .badge-binder { background: rgba(139, 92, 246, 0.2); color: #c4b5fd; border: 1px solid rgba(139, 92, 246, 0.3); }
        .badge-sale { background: rgba(245, 158, 11, 0.2); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-set { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
        .badge-foil { background: rgba(245, 158, 11, 0.2); color: #fde047; }
        .badge-nm { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; }

        /* Trend Badges */
        .trend-badge {
            padding: 2px 7px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.74rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
            line-height: 1.2;
        }

        .trend-up {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
        }

        .trend-down {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.15);
        }

        .trend-stable {
            background: rgba(148, 163, 184, 0.15);
            color: #cbd5e1;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }

        /* Cost Input */
        .cost-input {
            width: 70px;
            height: 26px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
            border-radius: 8px;
            padding: 2px 6px;
            color: #fde68a;
            font-size: 0.8rem;
            font-weight: 600;
            font-family: 'Plus Jakarta Sans', sans-serif;
            outline: none;
            transition: all 0.3s ease;
            text-align: right;
        }

        .cost-input:focus {
            border-color: var(--accent-amber, #f59e0b);
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.25);
            background: rgba(15, 23, 42, 0.85);
        }

        .cost-input::placeholder {
            color: rgba(148, 163, 184, 0.5);
            font-weight: 400;
        }

        .cost-saved-indicator {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: var(--accent-emerald, #10b981);
            border-radius: 50%;
            margin-left: 6px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .cost-saved-indicator.show {
            opacity: 1;
            animation: pulse-dot 1s ease;
        }

        @keyframes pulse-dot {
            0% { transform: scale(1); opacity: 0; }
            50% { transform: scale(1.8); opacity: 1; }
            100% { transform: scale(1); opacity: 1; }
        }

        /* Profit Badges */
        .profit-badge {
            padding: 2px 7px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.74rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
            line-height: 1.2;
        }

        .profit-positive {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .profit-negative {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .profit-neutral {
            background: rgba(148, 163, 184, 0.1);
            color: var(--text-muted, #94a3b8);
            border: 1px solid rgba(148, 163, 184, 0.15);
            font-weight: 400;
            font-size: 0.74rem;
        }

        /* Table view thumbnail */
        .cards-table-container {
            background: var(--card-bg, rgba(26, 34, 52, 0.75));
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
            border-radius: 20px;
            overflow: hidden;
            width: 100%;
        }

        .table-responsive {
            overflow-x: auto;
            width: 100%;
            scrollbar-width: thin;
            scrollbar-color: rgba(139, 92, 246, 0.4) rgba(15, 23, 42, 0.6);
        }

        .table-responsive::-webkit-scrollbar {
            height: 8px;
        }

        .table-responsive::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 4px;
        }

        .table-responsive::-webkit-scrollbar-thumb {
            background: rgba(139, 92, 246, 0.4);
            border-radius: 4px;
        }

        .table-responsive::-webkit-scrollbar-thumb:hover {
            background: rgba(139, 92, 246, 0.7);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th {
            background: rgba(255, 255, 255, 0.04);
            padding: 8px 6px;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            color: var(--text-muted, #94a3b8);
            border-bottom: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
            white-space: nowrap;
        }

        th.sortable {
            cursor: pointer;
            user-select: none;
            transition: all 0.2s ease;
        }

        th.sortable:hover {
            background: rgba(255, 255, 255, 0.08);
            color: #fff;
        }

        th.sortable.active-sort {
            color: #c4b5fd;
            background: rgba(139, 92, 246, 0.18);
            border-bottom: 2px solid var(--primary, #8b5cf6);
        }

        .sort-icon {
            display: inline-block;
            margin-left: 4px;
            font-size: 0.75rem;
            color: var(--accent-pink, #ec4899);
        }

        td {
            padding: 5px 6px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-size: 0.82rem;
            vertical-align: middle;
            white-space: nowrap;
        }

        .td-card-name {
            white-space: normal;
            min-width: 170px;
        }

        tr:hover td {
            background: rgba(255, 255, 255, 0.03);
        }

        .card-name-title {
            font-weight: 700;
            color: #fff;
            font-size: 0.88rem;
            line-height: 1.2;
        }

        .card-sub-info {
            font-size: 0.71rem;
            color: var(--text-muted, #94a3b8);
            margin-top: 1px;
            line-height: 1.1;
        }

        .card-thumbnail-wrap {
            position: relative;
            display: inline-block;
            flex-shrink: 0;
            cursor: pointer;
            width: 26px;
            height: 36px;
        }

        .card-thumbnail {
            width: 26px !important;
            height: 36px !important;
            max-width: 26px !important;
            max-height: 36px !important;
            border-radius: 4px;
            object-fit: cover !important;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
            transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease;
            display: block !important;
        }

        .card-thumbnail-placeholder {
            width: 26px;
            height: 36px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px dashed rgba(255, 255, 255, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted, #94a3b8);
            font-size: 0.75rem;
            flex-shrink: 0;
            cursor: pointer;
        }

        .card-thumbnail-wrap:hover .card-thumbnail {
            transform: scale(1.15) rotate(-2deg);
            border-color: var(--primary, #8b5cf6);
            box-shadow: 0 6px 20px var(--primary-glow, rgba(139, 92, 246, 0.35));
            z-index: 10;
        }

        .clickable-card-title {
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .clickable-card-title:hover {
            color: #c4b5fd;
            transform: translateX(2px);
        }

        /* Pagination Bar */
        .pagination-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 20px;
            background: var(--card-bg, rgba(26, 34, 52, 0.75));
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
            border-radius: 16px;
            margin-top: 20px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }

        .pagination-controls {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .page-btn {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
            color: #fff;
            padding: 7px 14px;
            border-radius: 10px;
            font-size: 0.84rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .page-btn:hover:not(:disabled) {
            background: rgba(255, 255, 255, 0.12);
            border-color: var(--primary, #8b5cf6);
            transform: translateY(-1px);
        }

        .page-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        `;
        document.head.appendChild(style);
    }
})();

/**
 * Utility Functions & CardListRenderer Module
 */

function getCardKey(card) {
    if (!card) return '';
    return `${card.binder_id || ''}_${card.card_name_en || card.card_name_pt}_${card.card_number}_${card.set_pt}_${card.quality}_${card.language}`;
}

function formatBRL(val) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);
}

function getCardTrendInfo(c, historyMap) {
    let trend = c.trend || 'stable';
    let pct = c.price_change_pct || 0;
    let brl = c.price_change_brl || 0;

    let mapToUse = historyMap || window.cardHistoryMap;
    if (!mapToUse && typeof cardHistoryMap !== 'undefined') {
        mapToUse = cardHistoryMap;
    }

    const key = getCardKey(c);
    if (mapToUse && mapToUse[key] && mapToUse[key].length >= 2) {
        const entries = mapToUse[key];
        const curMin = entries[entries.length - 1].min || 0;
        const prevMin = entries[entries.length - 2].min || 0;
        if (prevMin > 0 && curMin !== prevMin) {
            brl = Math.round((curMin - prevMin) * 100) / 100;
            pct = Math.round(((brl / prevMin) * 100) * 10) / 10;
            if (brl > 0) trend = 'up';
            else if (brl < 0) trend = 'down';
            else trend = 'stable';
        }
    }

    return { trend, pct, brl };
}

/**
 * Render Cards Grid
 */
function renderCardsGrid(cards, options = {}) {
    const containerId = options.containerId || 'cards-grid-container';
    const container = document.getElementById(containerId);
    if (!container) return;

    const emptyMsg = options.emptyMessage || 'Nenhuma carta encontrada com os filtros selecionados.';

    if (!cards || cards.length === 0) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted, #94a3b8); padding: 48px; background: rgba(26, 34, 52, 0.5); border-radius: 18px; border: 1px dashed var(--card-border, rgba(255, 255, 255, 0.08));">${emptyMsg}</div>`;
        return;
    }

    let costMap = {};
    if (typeof getCostPaidMap === 'function') {
        costMap = getCostPaidMap();
    } else if (options.costMap) {
        costMap = options.costMap;
    } else {
        try {
            costMap = JSON.parse(localStorage.getItem('ligapokemon_costs_paid') || '{}');
        } catch (e) { costMap = {}; }
    }

    container.innerHTML = cards.map(c => {
        const cardKey = getCardKey(c);
        const escapedKey = cardKey.replace(/'/g, "\\'").replace(/"/g, '&quot;');

        const trendInfo = getCardTrendInfo(c, options.cardHistoryMap);
        let trendBadge = `<span class="trend-badge trend-stable" onclick="openCardHistoryModal('${escapedKey}')" style="cursor:pointer;" title="Variação baseada no Preço Mínimo de Mercado">➖ Estável 📊</span>`;
        if (trendInfo.trend === 'up') {
            trendBadge = `<span class="trend-badge trend-up" onclick="openCardHistoryModal('${escapedKey}')" style="cursor:pointer;" title="Variação baseada no Preço Mínimo de Mercado">📈 +${trendInfo.pct}% (+${formatBRL(trendInfo.brl)}) 📊</span>`;
        } else if (trendInfo.trend === 'down') {
            trendBadge = `<span class="trend-badge trend-down" onclick="openCardHistoryModal('${escapedKey}')" style="cursor:pointer;" title="Variação baseada no Preço Mínimo de Mercado">📉 ${trendInfo.pct}% (${formatBRL(trendInfo.brl)}) 📊</span>`;
        }

        const extrasBadge = c.extras ? `<span class="badge badge-foil">${c.extras}</span>` : '';
        const savedCost = costMap[cardKey];
        const costValue = savedCost !== undefined ? savedCost : '';

        let profitHtml = '<span class="profit-badge profit-neutral">Insira o custo →</span>';
        if (savedCost !== undefined && savedCost !== null) {
            const minPrice = c.price_min_brl || 0;
            const diff = minPrice - savedCost;
            const pctChange = savedCost > 0 ? ((diff / savedCost) * 100).toFixed(1) : 0;
            if (diff > 0) {
                profitHtml = `<span class="profit-badge profit-positive">📈 +${formatBRL(diff)} (+${pctChange}%)</span>`;
            } else if (diff < 0) {
                profitHtml = `<span class="profit-badge profit-negative">📉 ${formatBRL(diff)} (${pctChange}%)</span>`;
            } else {
                profitHtml = `<span class="profit-badge profit-neutral">⚖️ Empate</span>`;
            }
        }

        const cardName = c.card_name_pt || c.card_name_en || '';
        const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(`pokemon ${cardName} ${c.card_number || ''}`)}`;

        const photoUrls = (window.CardImageResolver && typeof window.CardImageResolver.getCardImageUrls === 'function')
            ? window.CardImageResolver.getCardImageUrls(c)
            : { low: c.image_url || '', fallback: '' };
        const resolvedLow = photoUrls.low || c.image_url || '';

        const photoEl = resolvedLow 
            ? `<img src="${resolvedLow}" data-fallbacks="${photoUrls.fallback || ''}" alt="${cardName}" loading="lazy" onerror="window.CardImageResolver ? window.CardImageResolver.handleCardImgError(this) : this.parentElement.innerHTML='<span class=\\'grid-card-photo-placeholder\\'>🃏</span>'" />`
            : `<span class="grid-card-photo-placeholder">🃏</span>`;

        const isSaleBinder = options.isSalesPage || (window.saleBinderIds && window.saleBinderIds.includes(String(c.binder_id)));
        const binderBadgeClass = isSaleBinder ? 'badge-sale' : 'badge-binder';
        const binderIcon = isSaleBinder ? '🏷️ ' : '';
        const binderDefaultLabel = isSaleBinder ? 'Venda' : 'Coleção';

        return `
            <div class="grid-card-item">
                <!-- Left Side: Photo -->
                <div class="grid-card-photo-side" onclick="openCardHistoryModal('${escapedKey}')" title="Clique para ver o histórico de preços e foto">
                    ${photoEl}
                </div>

                <!-- Right Side: Card Information -->
                <div class="grid-card-info-side">
                    <div>
                        <div class="grid-card-header">
                            <div style="min-width: 0;">
                                <div class="grid-card-name" onclick="openCardHistoryModal('${escapedKey}')" title="Ver histórico de preços">
                                    ${cardName}
                                </div>
                                <div class="grid-card-sub">
                                    ${c.card_name_en && c.card_name_en !== cardName ? c.card_name_en + ' • ' : ''}#${c.card_number}
                                </div>
                            </div>
                            <a href="${googleSearchUrl}" target="_blank" rel="noopener noreferrer" class="btn-google-search" title="Pesquisar no Google em outra aba" onclick="event.stopPropagation();">
                                <i data-lucide="search" style="width: 11px; height: 11px;"></i>
                                <span>Google</span>
                            </a>
                        </div>

                        <div class="grid-card-tags">
                            <span class="badge ${binderBadgeClass}">${binderIcon}${c.binder_name || binderDefaultLabel}</span>
                            <span class="badge badge-set">${c.set_pt}</span>
                            <span class="badge" style="background: rgba(255,255,255,0.08); font-weight: 700;">${c.quantity}x</span>
                            <span class="badge badge-nm">${c.quality}</span>
                            <span class="badge" style="background: rgba(255,255,255,0.06);">${c.language}</span>
                            ${extrasBadge}
                        </div>

                        <div class="grid-card-prices-row">
                            <div class="grid-price-item">
                                <span class="grid-price-label">Mínimo</span>
                                <span class="grid-price-val" style="color: #93c5fd;">${formatBRL(c.price_min_brl)}</span>
                            </div>
                            <div class="grid-price-item">
                                <span class="grid-price-label">Médio</span>
                                <span class="grid-price-val" style="color: #c4b5fd;">${formatBRL(c.price_avg_brl)}</span>
                            </div>
                            <div class="grid-price-item">
                                <span class="grid-price-label">Máximo</span>
                                <span class="grid-price-val" style="color: #f472b6;">${formatBRL(c.price_max_brl)}</span>
                            </div>
                        </div>
                    </div>

                    <div class="grid-card-footer">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            ${trendBadge}
                        </div>

                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="display: flex; align-items: center; position: relative;">
                                <input type="number" step="0.01" min="0" 
                                    class="cost-input" 
                                    placeholder="Custo R$" 
                                    value="${costValue}" 
                                    data-card-key="${cardKey.replace(/"/g, '&quot;')}" 
                                    data-min-price="${c.price_min_brl || 0}"
                                    oninput="handleCostChange(this)" 
                                    onchange="handleCostChange(this)" 
                                    style="width: 85px;" />
                                <span class="cost-saved-indicator"></span>
                            </div>
                            <div class="profit-td-cell">
                                ${profitHtml}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render Cards Table
 */
function renderCardsTable(cards, options = {}) {
    const tbodyId = options.tbodyId || 'cards-table-body';
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;

    const emptyMsg = options.emptyMessage || 'Nenhuma carta encontrada com os filtros selecionados.';

    if (!cards || cards.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--text-muted, #94a3b8); padding: 32px;">${emptyMsg}</td></tr>`;
        return;
    }

    let costMap = {};
    if (typeof getCostPaidMap === 'function') {
        costMap = getCostPaidMap();
    } else if (options.costMap) {
        costMap = options.costMap;
    } else {
        try {
            costMap = JSON.parse(localStorage.getItem('ligapokemon_costs_paid') || '{}');
        } catch (e) { costMap = {}; }
    }

    tbody.innerHTML = cards.map(c => {
        const cardKey = getCardKey(c);
        const escapedKey = cardKey.replace(/'/g, "\\'").replace(/"/g, '&quot;');

        const trendInfo = getCardTrendInfo(c, options.cardHistoryMap);
        let trendBadge = `<span class="trend-badge trend-stable" onclick="openCardHistoryModal('${escapedKey}')" style="cursor:pointer;" title="Variação baseada no Preço Mínimo de Mercado: Estável">➖ R$ 0,00</span>`;
        if (trendInfo.trend === 'up') {
            trendBadge = `<span class="trend-badge trend-up" onclick="openCardHistoryModal('${escapedKey}')" style="cursor:pointer;" title="Subiu +${formatBRL(trendInfo.brl)} (+${trendInfo.pct}%)">📈 +${formatBRL(trendInfo.brl)}</span>`;
        } else if (trendInfo.trend === 'down') {
            trendBadge = `<span class="trend-badge trend-down" onclick="openCardHistoryModal('${escapedKey}')" style="cursor:pointer;" title="Caiu ${formatBRL(trendInfo.brl)} (${trendInfo.pct}%)">📉 ${formatBRL(trendInfo.brl)}</span>`;
        }

        const extrasBadge = c.extras ? `<span class="badge badge-foil">${c.extras}</span>` : '';
        const savedCost = costMap[cardKey];
        const costValue = savedCost !== undefined ? savedCost : '';

        let profitHtml = '<span class="profit-badge profit-neutral" title="Insira o custo pago">-</span>';
        if (savedCost !== undefined && savedCost !== null) {
            const minPrice = c.price_min_brl || 0;
            const diff = minPrice - savedCost;
            const pctChange = savedCost > 0 ? ((diff / savedCost) * 100).toFixed(1) : 0;
            if (diff > 0) {
                profitHtml = `<span class="profit-badge profit-positive" title="Lucro de +${pctChange}%">📈 +${formatBRL(diff)}</span>`;
            } else if (diff < 0) {
                profitHtml = `<span class="profit-badge profit-negative" title="Prejuízo de ${pctChange}%">📉 ${formatBRL(diff)}</span>`;
            } else {
                profitHtml = `<span class="profit-badge profit-neutral" title="Empate">R$ 0,00</span>`;
            }
        }

        const cardName = c.card_name_pt || c.card_name_en || '';
        const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(`pokemon ${cardName} ${c.card_number || ''}`)}`;

        const thumbUrls = (window.CardImageResolver && typeof window.CardImageResolver.getCardImageUrls === 'function')
            ? window.CardImageResolver.getCardImageUrls(c)
            : { low: c.image_url || '', fallback: '' };
        const resolvedThumb = thumbUrls.low || c.image_url || '';

        const imgThumb = resolvedThumb 
            ? `<div class="card-thumbnail-wrap" onclick="openCardHistoryModal('${escapedKey}')" title="Ver foto e histórico de preços">
                 <img class="card-thumbnail" src="${resolvedThumb}" data-fallbacks="${thumbUrls.fallback || ''}" alt="${cardName}" loading="lazy" onerror="window.CardImageResolver ? window.CardImageResolver.handleCardImgError(this) : this.parentElement.style.display='none'" />
               </div>`
            : `<div class="card-thumbnail-placeholder" onclick="openCardHistoryModal('${escapedKey}')" title="Ver histórico de preços">🃏</div>`;

        const isSaleBinder = options.isSalesPage || (window.saleBinderIds && window.saleBinderIds.includes(String(c.binder_id)));
        const binderBadgeClass = isSaleBinder ? 'badge-sale' : 'badge-binder';
        const binderIcon = isSaleBinder ? '🏷️ ' : '';
        const binderDefaultLabel = isSaleBinder ? 'Venda' : 'Coleção';

        return `
            <tr>
                <td><span class="badge ${binderBadgeClass}">${binderIcon}${c.binder_name || binderDefaultLabel}</span></td>
                <td class="td-card-name">
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px; min-width: 0;">
                            ${imgThumb}
                            <div style="min-width: 0;">
                                <div class="card-name-title clickable-card-title" onclick="openCardHistoryModal('${escapedKey}')" title="Clique para ver o gráfico de histórico e foto">
                                    <span>${cardName}</span>
                                    <i data-lucide="line-chart" style="width: 13px; height: 13px; color: var(--primary, #8b5cf6); opacity: 0.85; flex-shrink: 0;"></i>
                                </div>
                                <div class="card-sub-info">${c.card_name_en || ''}</div>
                            </div>
                        </div>
                        <a href="${googleSearchUrl}" target="_blank" rel="noopener noreferrer" class="btn-google-search" title="Pesquisar '${cardName} ${c.card_number || ''}' no Google em outra aba" onclick="event.stopPropagation();" style="flex-shrink: 0;">
                            <i data-lucide="search" style="width: 11px; height: 11px;"></i>
                            <span>Google</span>
                            <i data-lucide="external-link" style="width: 9px; height: 9px; opacity: 0.7;"></i>
                        </a>
                    </div>
                </td>
                <td>
                    <span class="badge badge-set">${c.set_pt}</span>
                    <div class="card-sub-info">#${c.card_number}</div>
                </td>
                <td><strong>${c.quantity}x</strong></td>
                <td>
                    <span class="badge badge-nm">${c.quality}</span>
                    <span class="badge" style="background: rgba(255,255,255,0.06);">${c.language}</span>
                    ${extrasBadge}
                </td>
                <td style="color: #93c5fd; font-variant-numeric: tabular-nums;">${formatBRL(c.price_min_brl)}</td>
                <td style="color: #c4b5fd; font-weight: 700; font-variant-numeric: tabular-nums;">${formatBRL(c.price_avg_brl)}</td>
                <td style="color: #f472b6; font-variant-numeric: tabular-nums;">${formatBRL(c.price_max_brl)}</td>
                <td>${trendBadge}</td>
                <td>
                    <div style="display: flex; align-items: center;">
                        <input type="number" step="0.01" min="0" 
                            class="cost-input" 
                            placeholder="R$ 0,00" 
                            value="${costValue}" 
                            data-card-key="${cardKey.replace(/"/g, '&quot;')}" 
                            data-min-price="${c.price_min_brl || 0}"
                            oninput="handleCostChange(this)" 
                            onchange="handleCostChange(this)" />
                        <span class="cost-saved-indicator"></span>
                    </div>
                </td>
                <td class="profit-td-cell">${profitHtml}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Handle inline Cost Change
 */
function handleCostChange(inputEl) {
    const cardKey = inputEl.dataset.cardKey;
    const val = inputEl.value.trim();
    const numVal = val === '' ? '' : parseFloat(val);

    if (typeof saveCostPaid === 'function') {
        saveCostPaid(cardKey, numVal);
    }

    // Instant inline update without rebuilding DOM
    const containerEl = inputEl.closest('tr') || inputEl.closest('.grid-card-item');
    if (containerEl) {
        const profitEl = containerEl.querySelector('.profit-td-cell');
        const minPrice = parseFloat(inputEl.dataset.minPrice || 0);
        if (profitEl) {
            if (numVal === '' || isNaN(numVal)) {
                if (containerEl.tagName === 'TR') {
                    profitEl.innerHTML = '<span class="profit-badge profit-neutral" title="Insira o custo pago">-</span>';
                } else {
                    profitEl.innerHTML = '<span class="profit-badge profit-neutral">Insira o custo →</span>';
                }
            } else {
                const diff = minPrice - numVal;
                const pctChange = numVal > 0 ? ((diff / numVal) * 100).toFixed(1) : 0;
                if (diff > 0) {
                    if (containerEl.tagName === 'TR') {
                        profitEl.innerHTML = `<span class="profit-badge profit-positive" title="Lucro de +${pctChange}%">📈 +${formatBRL(diff)}</span>`;
                    } else {
                        profitEl.innerHTML = `<span class="profit-badge profit-positive">📈 +${formatBRL(diff)} (+${pctChange}%)</span>`;
                    }
                } else if (diff < 0) {
                    if (containerEl.tagName === 'TR') {
                        profitEl.innerHTML = `<span class="profit-badge profit-negative" title="Prejuízo de ${pctChange}%">📉 ${formatBRL(diff)}</span>`;
                    } else {
                        profitEl.innerHTML = `<span class="profit-badge profit-negative">📉 ${formatBRL(diff)} (${pctChange}%)</span>`;
                    }
                } else {
                    if (containerEl.tagName === 'TR') {
                        profitEl.innerHTML = `<span class="profit-badge profit-neutral" title="Empate">R$ 0,00</span>`;
                    } else {
                        profitEl.innerHTML = `<span class="profit-badge profit-neutral">⚖️ Empate</span>`;
                    }
                }
            }
        }
    }

    // Show saved dot indicator briefly
    const dot = inputEl.parentElement.querySelector('.cost-saved-indicator');
    if (dot) {
        dot.classList.remove('show');
        void dot.offsetWidth;
        dot.classList.add('show');
        setTimeout(() => dot.classList.remove('show'), 1200);
    }

    if (typeof updateProfitSummary === 'function') {
        updateProfitSummary();
    }
}

// Global Export Object
window.CardListRenderer = {
    getCardKey: getCardKey,
    formatBRL: formatBRL,
    getCardTrendInfo: getCardTrendInfo,
    renderCardsGrid: renderCardsGrid,
    renderCardsTable: renderCardsTable,
    handleCostChange: handleCostChange
};
