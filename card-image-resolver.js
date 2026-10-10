// card-image-resolver.js
// Resolve URLs de fotos de cartas com precisão usando Coleção Oficial (Set) + Número,
// com suporte a cache local, multi-idiomas e suporte prioritário para URLs pré-resolvidas.

(function (window) {
    const CACHE_KEY = 'tcg_card_images_cache_v1';
    let localCache = {};

    try {
        const stored = localStorage.getItem(CACHE_KEY);
        if (stored) {
            localCache = JSON.parse(stored);
        }
    } catch (e) {
        localCache = {};
    }

    // Conjunto de sets e mapeamentos predefinidos para resolução instantânea
    let setsMap = {
        "151": { "serie": "sv", "set": "sv03.5", "lang": "pt" },
        "collection 151": { "serie": "sv", "set": "sv03.5", "lang": "pt" },
        "pokemon card 151": { "serie": "sv", "set": "sv03.5", "lang": "pt" },
        "amigos de jornada": { "serie": "sv", "set": "sv09", "lang": "pt" },
        "coroa estelar": { "serie": "sv", "set": "sv07", "lang": "pt" },
        "fagulhas impetuosas": { "serie": "sv", "set": "sv08", "lang": "pt" },
        "evolucoes prismaticas": { "serie": "sv", "set": "sv08.5", "lang": "pt" },
        "mascaras do crepusculo": { "serie": "sv", "set": "sv06", "lang": "pt" },
        "forcas temporais": { "serie": "sv", "set": "sv05", "lang": "pt" },
        "fabulas nebulosas": { "serie": "sv", "set": "sv06.5", "lang": "pt" },
        "destinos de paldea": { "serie": "sv", "set": "sv04.5", "lang": "pt" },
        "fenda paradoxal": { "serie": "sv", "set": "sv04", "lang": "pt" },
        "obsidiana em chamas": { "serie": "sv", "set": "sv03", "lang": "pt" },
        "evolucoes em paldea": { "serie": "sv", "set": "sv02", "lang": "pt" },
        "escarlate e violeta": { "serie": "sv", "set": "sv01", "lang": "pt" },
        "escarlate e violeta promos": { "serie": "sv", "set": "svp", "lang": "pt" },
        "fogo branco": { "serie": "sv", "set": "sv10.5w", "lang": "pt" },
        "raio preto": { "serie": "sv", "set": "sv10.5b", "lang": "pt" },
        "caos ascendente": { "serie": "me", "set": "me04", "lang": "pt" },
        "fogo fantasmagorico": { "serie": "me", "set": "me02", "lang": "pt" },
        "equilibrio perfeito": { "serie": "me", "set": "me03", "lang": "pt" },
        "celebracao de 30 anos": { "serie": "me", "set": "30th", "lang": "en" },
        "celebracao de 30 anos cartas classicas": { "serie": "me", "set": "30th-c", "lang": "en" },
        "30 anos": { "serie": "me", "set": "30th", "lang": "en" },
        "megaevolucao": { "serie": "me", "set": "mep", "lang": "en" },
        "promos mega evolucao": { "serie": "me", "set": "mep", "lang": "en" },
        "mega evolution promos": { "serie": "me", "set": "mep", "lang": "en" },
        "wild force": { "serie": "SV", "set": "SV5K", "lang": "ja" },
        "abyss eye": { "serie": "SV", "set": "SV9a", "lang": "ja" },
        "alter genesis": { "serie": "sm", "set": "sm12", "lang": "ja" },
        "dark crystal blaze": { "serie": "SV", "set": "SV3", "lang": "ja" },
        "eevee heroes": { "serie": "swsh", "set": "s6a", "lang": "ja" },
        "ruler of the black flame": { "serie": "SV", "set": "SV3", "lang": "ja" },
        "espada e escudo promos": { "serie": "swsh", "set": "swshp", "lang": "pt" },
        "realeza absoluta": { "serie": "swsh", "set": "swsh12.5", "lang": "pt" },
        "tempestade prateada": { "serie": "swsh", "set": "swsh12", "lang": "pt" },
        "origem perdida": { "serie": "swsh", "set": "swsh11", "lang": "pt" },
        "astros cintilantes": { "serie": "swsh", "set": "swsh9", "lang": "pt" },
        "golpe fusao": { "serie": "swsh", "set": "swsh8", "lang": "pt" },
        "ceus em evolucao": { "serie": "swsh", "set": "swsh7", "lang": "pt" },
        "reinado arrepiante": { "serie": "swsh", "set": "swsh6", "lang": "pt" },
        "estilos de batalha": { "serie": "swsh", "set": "swsh5", "lang": "pt" },
        "destinos brilhantes": { "serie": "swsh", "set": "swsh4.5", "lang": "pt" },
        "voltagem vivida": { "serie": "swsh", "set": "swsh4", "lang": "pt" },
        "escuridao incandescente": { "serie": "swsh", "set": "swsh3", "lang": "pt" },
        "rixa rebelde": { "serie": "swsh", "set": "swsh2", "lang": "pt" },
        "espada e escudo": { "serie": "swsh", "set": "swsh1", "lang": "pt" },
        "celebracoes": { "serie": "swsh", "set": "cel25", "lang": "pt" },
        "caminho do campeao": { "serie": "swsh", "set": "swsh3.5", "lang": "pt" },
        "sol e lua": { "serie": "sm", "set": "sm1", "lang": "pt" },
        "guardioes ascendentes": { "serie": "sm", "set": "sm2", "lang": "pt" },
        "sombras ardentes": { "serie": "sm", "set": "sm3", "lang": "pt" },
        "lendas luminescentes": { "serie": "sm", "set": "sm3.5", "lang": "pt" },
        "invasao carmim": { "serie": "sm", "set": "sm4", "lang": "pt" },
        "ultraprisma": { "serie": "sm", "set": "sm5", "lang": "pt" },
        "luz proibida": { "serie": "sm", "set": "sm6", "lang": "pt" },
        "tempestade celestial": { "serie": "sm", "set": "sm7", "lang": "pt" },
        "trovoes perdidos": { "serie": "sm", "set": "sm8", "lang": "pt" },
        "uniao de aliados": { "serie": "sm", "set": "sm9", "lang": "pt" },
        "elos inquebraveis": { "serie": "sm", "set": "sm10", "lang": "pt" },
        "sintonia mental": { "serie": "sm", "set": "sm11", "lang": "pt" },
        "destinos ocultos": { "serie": "sm", "set": "sm115", "lang": "pt" },
        "eclipse cosmico": { "serie": "sm", "set": "sm12", "lang": "pt" }
    };

    fetch('card-sets-map.json')
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (data) {
                setsMap = Object.assign({}, setsMap, data);
            }
        })
        .catch(() => {});

    function cleanString(str) {
        if (!str) return '';
        return str.normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, "")
            .trim();
    }

    function extractNumberInfo(rawNum) {
        if (!rawNum) return { raw: '', digits: '', padded3: '', padded2: '', plain: '' };
        const numPart = String(rawNum).split('/')[0].trim();
        const digits = numPart.replace(/\D/g, '');
        const plain = digits.replace(/^0+/, '') || '0';
        return {
            raw: numPart,
            digits: digits,
            plain: plain,
            padded3: digits ? digits.padStart(3, '0') : numPart,
            padded2: digits ? digits.padStart(2, '0') : numPart
        };
    }

    function getCardImageUrls(card) {
        if (!card) return { low: '', high: '', fallback: '' };

        // 1. PRIORIDADE MÁXIMA: Se o backend já pré-resolveu a URL (em cards_latest.json), usa diretamente!
        if (card.image_url) {
            return {
                low: card.image_url,
                high: card.image_high_url || card.image_url,
                fallback: ''
            };
        }

        const setRaw = card.set_pt || '';
        const setClean = cleanString(setRaw);
        const numInfo = extractNumberInfo(card.card_number);

        const cacheKey = `${setClean}_${numInfo.raw}`;
        if (localCache[cacheKey]) {
            return localCache[cacheKey];
        }

        const setConfig = setsMap[setClean];

        let lowUrl = '';
        let highUrl = '';
        let fallbackUrl = '';

        if (setConfig) {
            const serie = setConfig.serie;
            const setId = setConfig.set;
            const defaultLang = setConfig.lang || 'pt';

            let formattedNum = numInfo.padded3;
            const sLower = serie.lower ? serie.lower() : String(serie).toLowerCase();
            const sidLower = setId.lower ? setId.lower() : String(setId).toLowerCase();

            if (sLower === 'sv' || sLower === 'me' || sidLower.startsWith('swsh9') || sidLower.startsWith('swsh10') || sidLower.startsWith('swsh11') || sidLower.startsWith('swsh12')) {
                formattedNum = numInfo.padded3;
            } else {
                formattedNum = numInfo.plain;
            }

            lowUrl = `https://assets.tcgdex.net/${defaultLang}/${serie}/${setId}/${formattedNum}/low.webp`;
            highUrl = `https://assets.tcgdex.net/${defaultLang}/${serie}/${setId}/${formattedNum}/high.webp`;

            const altNum = (formattedNum === numInfo.plain) ? numInfo.padded3 : numInfo.plain;
            const altLangs = ['en', 'pt', 'ja', 'zh-tw'].filter(l => l !== defaultLang);
            fallbackUrl = altLangs.map(l => `https://assets.tcgdex.net/${l}/${serie}/${setId}/${formattedNum}/low.webp`).join('|') +
                `|https://assets.tcgdex.net/${defaultLang}/${serie}/${setId}/${altNum}/low.webp`;
        } else if (setClean.includes('promo') || setClean.includes('mega') || setClean.includes('30')) {
            if (setClean.includes('30')) {
                lowUrl = `https://assets.tcgdex.net/en/me/30th/${numInfo.padded3}/low.webp`;
                highUrl = `https://assets.tcgdex.net/en/me/30th/${numInfo.padded3}/high.webp`;
                fallbackUrl = `https://assets.tcgdex.net/en/me/30th-c/${numInfo.padded3}/low.webp`;
            } else if (setClean.includes('mega')) {
                lowUrl = `https://assets.tcgdex.net/en/me/mep/${numInfo.padded3}/low.webp`;
                highUrl = `https://assets.tcgdex.net/en/me/mep/${numInfo.padded3}/high.webp`;
            } else if (setClean.includes('escarlate') || setClean.includes('violeta') || setClean.includes('sv')) {
                lowUrl = `https://assets.tcgdex.net/pt/sv/svp/${numInfo.padded3}/low.webp`;
                highUrl = `https://assets.tcgdex.net/pt/sv/svp/${numInfo.padded3}/high.webp`;
            } else if (setClean.includes('espada') || setClean.includes('escudo') || setClean.includes('swsh')) {
                lowUrl = `https://assets.tcgdex.net/pt/swsh/swshp/SWSH${numInfo.padded3}/low.webp`;
                highUrl = `https://assets.tcgdex.net/pt/swsh/swshp/SWSH${numInfo.padded3}/high.webp`;
            }
        }

        return {
            low: lowUrl || '',
            high: highUrl || lowUrl || '',
            fallback: fallbackUrl
        };
    }

    function handleCardImgError(imgEl, fallbackListStr) {
        if (!imgEl) return;
        const fallbacksAttr = imgEl.dataset.fallbacks || fallbackListStr || '';
        const remaining = fallbacksAttr.split('|').filter(Boolean);
        
        if (remaining.length > 0) {
            const nextUrl = remaining.shift();
            imgEl.dataset.fallbacks = remaining.join('|');
            imgEl.src = nextUrl;
            return;
        }

        if (imgEl.parentElement && imgEl.parentElement.classList.contains('grid-card-photo-side')) {
            imgEl.parentElement.innerHTML = '<span class="grid-card-photo-placeholder" title="Foto indisponível no TCGdex">🃏</span>';
        } else if (imgEl.parentElement && imgEl.parentElement.classList.contains('card-thumbnail-wrap')) {
            imgEl.parentElement.innerHTML = '<span class="card-thumbnail-placeholder" title="Foto indisponível no TCGdex">🃏</span>';
        } else {
            imgEl.style.display = 'none';
        }
    }

    window.CardImageResolver = {
        getCardImageUrls: getCardImageUrls,
        handleCardImgError: handleCardImgError,
        cleanString: cleanString
    };

})(window);
