document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('re_product_map');
    if (!el) return;

    var lat = parseFloat(el.getAttribute('data-lat'));
    var lng = parseFloat(el.getAttribute('data-lng'));
    if (isNaN(lat) || isNaN(lng)) return;

    var map = L.map('re_product_map').setView([lat, lng], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    L.marker([lat, lng]).addTo(map).bindPopup(
        '<strong>' + el.getAttribute('data-name') + '</strong><br>' +
        '<small>' + el.getAttribute('data-address') + '</small>'
    ).openPopup();

    setTimeout(function () { map.invalidateSize(); }, 300);
});
