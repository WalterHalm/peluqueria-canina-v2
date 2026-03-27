document.addEventListener('DOMContentLoaded', function () { loadClusterPlugin(initReMap); });
if (document.readyState === 'complete' || document.readyState === 'interactive') { setTimeout(function() { loadClusterPlugin(initReMap); }, 0); }

function loadClusterPlugin(callback) {
    if (typeof L !== 'undefined' && typeof L.markerClusterGroup === 'function') {
        callback(); return;
    }
    var s = document.createElement('script');
    s.src = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js';
    s.onload = callback;
    s.onerror = callback; // si falla el CDN, igual inicializa sin clusters
    document.head.appendChild(s);
}

function initReMap() {
    if (window._reMapInitialized) return;
    var mapEl = document.getElementById('re_map');
    if (!mapEl) return;
    window._reMapInitialized = true;
    window._reMapDebug = { getMap: function() { return map; }, getProps: function() { return allProps; } };

    // ── Estado ──
    var activeFilters = { tipo: [], habitaciones: [], zona: [] };
    var allProps = [];
    var markers = {};
    var initialFitDone = false;
    var searchDates = { in: null, out: null, guests: null };

    // ── Mapa ──
    var map = L.map('re_map', { scrollWheelZoom: false, zoomControl: true })
        .setView([-30.77, -57.99], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    // Cluster group — se desactiva a zoom alto para mostrar marcadores individuales con precio
    var clusterGroup;
    if (typeof L.markerClusterGroup === 'function') {
        clusterGroup = L.markerClusterGroup({
            maxClusterRadius: 60,
            disableClusteringAtZoom: 15,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            iconCreateFunction: function (cluster) {
                return L.divIcon({
                    html: '<div class="re-cluster">' + cluster.getChildCount() + '</div>',
                    className: '',
                    iconSize: [40, 40],
                });
            },
        });
        map.addLayer(clusterGroup);
    }

    // Ctrl + scroll
    mapEl.addEventListener('wheel', function (e) {
        if (e.ctrlKey) { e.preventDefault(); e.deltaY < 0 ? map.zoomIn() : map.zoomOut(); }
    }, { passive: false });

    var overlay = document.createElement('div');
    overlay.className = 're-map-overlay';
    overlay.textContent = 'Usá Ctrl + scroll para hacer zoom';
    mapEl.appendChild(overlay);
    var overlayTimer;
    mapEl.addEventListener('wheel', function (e) {
        if (!e.ctrlKey) {
            overlay.classList.add('re-map-overlay--visible');
            clearTimeout(overlayTimer);
            overlayTimer = setTimeout(function () { overlay.classList.remove('re-map-overlay--visible'); }, 1500);
        }
    });

    // ── Modal filtros ──
    var modalOverlay = document.getElementById('re_modal_overlay');
    var filterToggle = document.getElementById('re_filter_toggle');
    var modalClose   = document.getElementById('re_modal_close');
    var modalClear   = document.getElementById('re_modal_clear');
    var modalApply   = document.getElementById('re_modal_apply');

    if (filterToggle) filterToggle.addEventListener('click', function () {
        modalOverlay.classList.add('re-modal-overlay--open');
    });
    if (modalClose) modalClose.addEventListener('click', closeModal);
    if (modalOverlay) modalOverlay.addEventListener('click', function (e) {
        if (e.target === modalOverlay) closeModal();
    });
    function closeModal() { modalOverlay.classList.remove('re-modal-overlay--open'); }

    if (modalApply) modalApply.addEventListener('click', function () {
        closeModal();
        loadProperties();
    });

    if (modalClear) modalClear.addEventListener('click', function () {
        clearAllFilters();
    });

    // ── Filtros: click en chips ──
    document.querySelectorAll('.re-filter-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var group = btn.closest('[data-group]').getAttribute('data-group');
            var value = btn.getAttribute('data-value');
            var idx = activeFilters[group].indexOf(value);
            if (idx === -1) {
                activeFilters[group].push(value);
                btn.classList.add('re-chip--active');
            } else {
                activeFilters[group].splice(idx, 1);
                btn.classList.remove('re-chip--active');
            }
            updateFilterBadge();
        });
    });

    var clearBtn = document.getElementById('re_clear_filters');
    if (clearBtn) clearBtn.addEventListener('click', function () {
        clearAllFilters();
        loadProperties();
    });

    function clearAllFilters() {
        activeFilters = { tipo: [], habitaciones: [], zona: [] };
        document.querySelectorAll('.re-filter-btn').forEach(function (b) {
            b.classList.remove('re-chip--active');
        });
        updateFilterBadge();
    }

    function updateFilterBadge() {
        var total = activeFilters.tipo.length + activeFilters.habitaciones.length + activeFilters.zona.length;
        var badge = document.getElementById('re_filter_badge');
        var clearB = document.getElementById('re_clear_filters');
        if (badge) { badge.textContent = total; badge.style.display = total > 0 ? 'inline-flex' : 'none'; }
        if (clearB) clearB.style.display = total > 0 ? 'inline-flex' : 'none';
        if (filterToggle) filterToggle.classList.toggle('re-filter-toggle--active', total > 0);
    }

    // ── Toggle lista/mapa (móvil) ──
    var mapInitialized = window.innerWidth > 768;
    var propList  = document.getElementById('re_prop_list');
    var mapSticky = document.querySelector('.re-map-sticky');

    function isMobile() { return window.innerWidth <= 768; }

    function setMobileView(view) {
        if (!isMobile()) return;
        if (view === 'map') {
            if (propList)  propList.style.display  = 'none';
            if (mapSticky) mapSticky.style.display = 'block';
            setTimeout(function () {
                map.invalidateSize();
                if (allProps.length > 0) {
                    map.fitBounds(
                        allProps.map(function (p) { return [p.lat, p.lng]; }),
                        { padding: [40, 40] }
                    );
                }
                mapInitialized = true;
            }, 50);
        } else {
            if (propList)  propList.style.display  = 'block';
            if (mapSticky) mapSticky.style.display = 'none';
        }
    }

    // Aplicar vista inicial en móvil
    if (isMobile()) setMobileView('list');

    // Re-aplicar si cambia el tamaño de ventana
    window.addEventListener('resize', function () {
        if (!isMobile()) {
            if (propList)  propList.style.display  = '';
            if (mapSticky) mapSticky.style.display = '';
            map.invalidateSize();
        } else {
            var activeBtn = document.querySelector('.re-view-btn--active');
            var view = activeBtn ? activeBtn.getAttribute('data-view') : 'list';
            setMobileView(view);
        }
    });

    document.querySelectorAll('.re-view-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var view = btn.getAttribute('data-view');
            document.querySelectorAll('.re-view-btn').forEach(function (b) {
                b.classList.toggle('re-view-btn--active', b === btn);
            });
            setMobileView(view);
        });
    });

    // ── Búsqueda con autocomplete Nominatim ──
    var searchInput = document.getElementById('re_search_place');
    var autocompleteBox = null;
    var nominatimTimer = null;

    function createAutocompleteBox() {
        if (autocompleteBox) return;
        autocompleteBox = document.createElement('div');
        autocompleteBox.className = 're-autocomplete';
        document.body.appendChild(autocompleteBox);
    }

    function positionAutocomplete() {
        if (!autocompleteBox || !searchInput) return;
        var rect = searchInput.getBoundingClientRect();
        autocompleteBox.style.top    = (rect.bottom + window.scrollY + 6) + 'px';
        autocompleteBox.style.left   = (rect.left   + window.scrollX)     + 'px';
        autocompleteBox.style.width  = Math.max(rect.width, 300)           + 'px';
    }

    function clearAutocomplete() {
        if (autocompleteBox) {
            autocompleteBox.innerHTML = '';
            autocompleteBox.classList.remove('re-autocomplete--open');
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            var q = searchInput.value.trim();
            clearTimeout(nominatimTimer);
            if (q.length < 3) { clearAutocomplete(); return; }

            nominatimTimer = setTimeout(function () {
                fetch('https://nominatim.openstreetmap.org/search?format=json&limit=6&addressdetails=1&q=' + encodeURIComponent(q), {
                    headers: { 'Accept-Language': 'es' }
                })
                .then(function (r) { return r.json(); })
                .then(function (results) {
                    createAutocompleteBox();
                    positionAutocomplete();
                    autocompleteBox.innerHTML = '';
                    if (!results.length) { clearAutocomplete(); return; }

                    results.forEach(function (item) {
                        var row = document.createElement('div');
                        row.className = 're-autocomplete__item';
                        var icon = item.class === 'place' || item.type === 'city' ? '🏙️' :
                                   item.class === 'boundary' ? '🗺️' : '📍';
                        var name = item.display_name.split(',').slice(0, 3).join(', ');
                        row.innerHTML =
                            '<span class="re-autocomplete__icon">' + icon + '</span>' +
                            '<span class="re-autocomplete__text">' + name + '</span>';

                        row.addEventListener('mousedown', function (e) {
                            e.preventDefault(); // evita que el input pierda foco antes del click
                            searchInput.value = name;
                            clearAutocomplete();
                            var bbox = item.boundingbox;
                            if (bbox) {
                                map.fitBounds([
                                    [parseFloat(bbox[0]), parseFloat(bbox[2])],
                                    [parseFloat(bbox[1]), parseFloat(bbox[3])]
                                ], { padding: [20, 20] });
                            } else {
                                map.setView([parseFloat(item.lat), parseFloat(item.lon)], 13);
                            }
                        });
                        autocompleteBox.appendChild(row);
                    });
                    autocompleteBox.classList.add('re-autocomplete--open');
                });
            }, 350);
        });

        searchInput.addEventListener('blur', function () {
            setTimeout(clearAutocomplete, 150);
        });

        searchInput.addEventListener('keydown', function (e) {
            if (!autocompleteBox || !autocompleteBox.classList.contains('re-autocomplete--open')) return;
            var items = autocompleteBox.querySelectorAll('.re-autocomplete__item');
            var active = autocompleteBox.querySelector('.re-autocomplete__item--active');
            var idx = Array.from(items).indexOf(active);
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (active) active.classList.remove('re-autocomplete__item--active');
                (items[idx + 1] || items[0]).classList.add('re-autocomplete__item--active');
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (active) active.classList.remove('re-autocomplete__item--active');
                (items[idx - 1] || items[items.length - 1]).classList.add('re-autocomplete__item--active');
            } else if (e.key === 'Enter' && active) {
                e.preventDefault();
                active.dispatchEvent(new MouseEvent('mousedown'));
            } else if (e.key === 'Escape') {
                clearAutocomplete();
            }
        });
    }

    // ── Botón de búsqueda ──
    var searchBtn = document.getElementById('re_search_btn');
    if (searchBtn) searchBtn.addEventListener('click', function () {
        searchDates.in     = document.getElementById('re_date_in').value || null;
        searchDates.out    = document.getElementById('re_date_out').value || null;
        searchDates.guests = document.getElementById('re_guests').value || null;
        loadProperties();
    });

    // ── URL del JSON ──
    function buildUrl() {
        var params = [];
        if (activeFilters.tipo.length)         params.push('tipo='         + encodeURIComponent(activeFilters.tipo.join('|')));
        if (activeFilters.habitaciones.length)  params.push('habitaciones=' + encodeURIComponent(activeFilters.habitaciones.join('|')));
        if (activeFilters.zona.length)          params.push('zone='         + encodeURIComponent(activeFilters.zona.join('|')));
        if (searchDates.in)                     params.push('date_in='      + encodeURIComponent(searchDates.in));
        if (searchDates.out)                    params.push('date_out='     + encodeURIComponent(searchDates.out));
        if (searchDates.guests)                 params.push('guests='       + encodeURIComponent(searchDates.guests));
        return '/mapa/propiedades.json' + (params.length ? '?' + params.join('&') : '');
    }

    // ── Calcular precio según noches ──
    function calcPrecio(p) {
        if (!p.price) return null;
        if (searchDates.in && searchDates.out) {
            var d1 = new Date(searchDates.in), d2 = new Date(searchDates.out);
            var nights = Math.round((d2 - d1) / 86400000);
            if (nights > 0) return { total: p.price * nights, nights: nights, perNight: p.price };
        }
        return { total: null, nights: null, perNight: p.price };
    }

    function precioHTML(p) {
        var c = calcPrecio(p);
        if (!c) return '';
        var sym = p.currency || '$';
        if (c.total && c.nights) {
            return '<div class="re-card-price">' +
                '<span class="re-card-price__total">' + sym + ' ' + c.total.toLocaleString('es-AR', {maximumFractionDigits:0}) + '</span>' +
                '<span class="re-card-price__nights"> · ' + c.nights + ' noche' + (c.nights > 1 ? 's' : '') + '</span>' +
                '</div>' +
                '<div class="re-card-price__per">' + sym + ' ' + c.perNight.toLocaleString('es-AR', {maximumFractionDigits:0}) + ' / noche</div>';
        }
        return '<div class="re-card-price">' +
            '<span class="re-card-price__total">' + sym + ' ' + c.perNight.toLocaleString('es-AR', {maximumFractionDigits:0}) + '</span>' +
            (p.rent_ok ? '<span class="re-card-price__nights"> / noche</span>' : '') +
            '</div>';
    }

    // ── Marcador con precio ──
    function createMarker(p) {
        var label = p.price
            ? (p.currency || '$') + ' ' + Number(p.price).toLocaleString('es-AR', {maximumFractionDigits:0})
            : p.name.split(' ')[0];
        var color = p.rent_ok && !p.sale_ok ? '#222' : (!p.rent_ok && p.sale_ok ? '#198754' : '#6f42c1');
        var icon = L.divIcon({
            className: '',
            html: '<div class="re-price-marker" style="background:' + color + '">' + label + '</div>',
            iconAnchor: [40, 36],
            iconSize: [80, 28],
        });
        return L.marker([p.lat, p.lng], { icon: icon });
    }

    function tipoBadge(p) {
        if (p.rent_ok && p.sale_ok) return '<span class="re-badge re-badge--both">Alquiler · Venta</span>';
        if (p.rent_ok) return '<span class="re-badge re-badge--rent">Alquiler</span>';
        return '<span class="re-badge re-badge--sale">Venta</span>';
    }

    // ── Carousel de imágenes ──
    function buildCarousel(p) {
        // Por ahora una imagen — se puede extender con múltiples imágenes
        return '<div class="re-card-carousel" data-id="' + p.id + '">' +
            '<img src="' + p.image_url + '" class="re-card-img" onerror="this.src=\'\';this.parentElement.classList.add(\'re-card-carousel--empty\')"/>' +
            tipoBadge(p) +
            '<button class="re-card-fav" title="Guardar">♡</button>' +
        '</div>';
    }

    // ── Renderizar lista ──
    function renderList() {
        var bounds = map.getBounds();
        var mapSize = map.getSize();
        // En móvil con mapa oculto los bounds son inválidos — mostrar todas las props
        var visible = (mapSize.x === 0 || mapSize.y === 0)
            ? allProps
            : allProps.filter(function (p) { return bounds.contains(L.latLng(p.lat, p.lng)); });
        var countEl = document.getElementById('re_prop_count');
        var cards   = document.getElementById('re_prop_cards');
        if (!countEl || !cards) return;
        countEl.textContent = visible.length + ' alojamiento' + (visible.length !== 1 ? 's' : '');
        cards.innerHTML = '';
        if (visible.length === 0) {
            var msg = searchDates.in && searchDates.out
                ? '<div class="re-empty__icon">📅</div><p>Sin disponibilidad en esas fechas</p><small>Probá con otras fechas o explorá el mapa.</small>'
                : '<div class="re-empty__icon">🏠</div><p>No hay propiedades en esta área.</p><small>Mové el mapa para explorar más.</small>';
            cards.innerHTML = '<div class="re-empty">' + msg + '</div>';
            return;
        }
        visible.forEach(function (p) {
            var card = document.createElement('div');
            card.className = 're-prop-card';
            card.setAttribute('data-id', p.id);
            card.innerHTML =
                buildCarousel(p) +
                '<div class="re-card-body">' +
                    '<div class="re-card-top">' +
                        '<div class="re-card-name">' + p.name + '</div>' +
                        '<div class="re-card-rating">★ <span>Nuevo</span></div>' +
                    '</div>' +
                    '<div class="re-card-location">📍 ' + (p.address || p.zone || '') + '</div>' +
                    (p.habitaciones ? '<div class="re-card-attrs">🛏 ' + p.habitaciones + ' hab.</div>' : '') +
                    precioHTML(p) +
                    '<a href="' + p.url + '" class="re-card-cta">Ver propiedad</a>' +
                '</div>';

            // Hover: resaltar marcador
            card.addEventListener('mouseenter', function () {
                if (markers[p.id]) {
                    var el = markers[p.id].getElement();
                    if (el) el.querySelector('.re-price-marker').classList.add('re-price-marker--hover');
                }
            });
            card.addEventListener('mouseleave', function () {
                if (markers[p.id]) {
                    var el = markers[p.id].getElement();
                    if (el) el.querySelector('.re-price-marker').classList.remove('re-price-marker--hover');
                }
            });

            card.addEventListener('click', function (e) {
                if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;
                map.setView([p.lat, p.lng], 16);
                if (markers[p.id]) markers[p.id].openPopup();
                document.querySelectorAll('.re-prop-card').forEach(function (c) { c.classList.remove('re-prop-card--active'); });
                card.classList.add('re-prop-card--active');
            });

            cards.appendChild(card);
        });
    }

    function clearMarkers() {
        if (clusterGroup) clusterGroup.clearLayers();
        else Object.values(markers).forEach(function (m) { map.removeLayer(m); });
        markers = {};
    }

    function renderSkeletons(n) {
        var s = '<div class="re-skeleton"><div class="re-skeleton__img"></div><div class="re-skeleton__body"><div class="re-skeleton__line re-skeleton__line--title"></div><div class="re-skeleton__line"></div><div class="re-skeleton__line re-skeleton__line--short"></div></div></div>';
        var html = '';
        for (var i = 0; i < n; i++) html += s;
        return html;
    }

    function loadProperties() {
        initialFitDone = false;
        clearMarkers();
        allProps = [];
        var countEl = document.getElementById('re_prop_count');
        var cards   = document.getElementById('re_prop_cards');
        if (countEl) countEl.textContent = 'Buscando...';
        if (cards)   cards.innerHTML = renderSkeletons(4);

        fetch(buildUrl())
            .then(function (r) { return r.json(); })
            .then(function (props) {
                allProps = props;
                props.forEach(function (p) {
                    var popup =
                        '<div class="re-popup">' +
                        '<img src="' + p.image_url + '" class="re-popup__img" onerror="this.style.display=\'none\'"/>' +
                        '<div class="re-popup__body">' +
                        '<div class="re-popup__name">' + p.name + '</div>' +
                        (p.price ? '<div class="re-popup__price">' + (p.currency||'$') + ' ' + Number(p.price).toLocaleString('es-AR',{maximumFractionDigits:0}) + (p.rent_ok ? '/noche' : '') + '</div>' : '') +
                        '<a href="' + p.url + '" class="re-popup__link">Ver propiedad →</a>' +
                        '</div></div>';

                    var marker = createMarker(p);
                    marker.bindPopup(popup, { maxWidth: 260, className: 're-leaflet-popup' });
                    marker.on('mouseover', function () {
                        var el = marker.getElement();
                        if (el) el.querySelector('.re-price-marker').classList.add('re-price-marker--hover');
                        var card = document.querySelector('.re-prop-card[data-id="' + p.id + '"]');
                        if (card) card.classList.add('re-prop-card--hover');
                    });
                    marker.on('mouseout', function () {
                        var el = marker.getElement();
                        if (el) el.querySelector('.re-price-marker').classList.remove('re-price-marker--hover');
                        var card = document.querySelector('.re-prop-card[data-id="' + p.id + '"]');
                        if (card) card.classList.remove('re-prop-card--hover');
                    });
                    marker.on('click', function () {
                        document.querySelectorAll('.re-prop-card').forEach(function (c) { c.classList.remove('re-prop-card--active'); });
                        var card = document.querySelector('.re-prop-card[data-id="' + p.id + '"]');
                        if (card) { card.classList.add('re-prop-card--active'); card.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
                    });
                    if (clusterGroup) clusterGroup.addLayer(marker);
                    else marker.addTo(map);
                    markers[p.id] = marker;
                });

                if (props.length > 0) {
                    if (isMobile() && !mapInitialized) {
                        initialFitDone = true;
                        renderList();
                    } else {
                        map.once('moveend', function () { initialFitDone = true; renderList(); });
                        map.fitBounds(props.map(function (p) { return [p.lat, p.lng]; }), { padding: [60, 60] });
                    }
                } else {
                    initialFitDone = true;
                    renderList();
                }
            });
    }

    map.on('moveend', function () { if (initialFitDone) renderList(); });
    setTimeout(function () { map.invalidateSize(); }, 200);
    loadProperties();
}
