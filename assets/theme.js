/* MustBuy theme — vanilla JS, no dependencies */
(function () {
  'use strict';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ---------- Money ---------- */
  function formatMoney(cents, format) {
    if (typeof cents === 'string') cents = cents.replace('.', '');
    format = format || window.theme.moneyFormat || '₪{{amount}}';
    const placeholder = /\{\{\s*(\w+)\s*\}\}/;
    const fmt = (n, precision, thousands = ',', decimal = '.') => {
      if (isNaN(n) || n == null) return '0';
      n = (n / 100).toFixed(precision);
      const parts = n.split('.');
      const dollars = parts[0].replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1' + thousands);
      return dollars + (parts[1] ? decimal + parts[1] : '');
    };
    const match = format.match(placeholder);
    let value = '';
    switch (match && match[1]) {
      case 'amount_no_decimals': value = fmt(cents, 0); break;
      case 'amount_with_comma_separator': value = fmt(cents, 2, '.', ','); break;
      case 'amount_no_decimals_with_comma_separator': value = fmt(cents, 0, '.', ','); break;
      default: value = fmt(cents, 2);
    }
    // Israeli display: ₪249 instead of ₪249.00 (keeps agorot like ₪99.90)
    return format.replace(placeholder, value.replace(/[.,]00$/, ''));
  }
  window.theme.formatMoney = formatMoney;

  /* ---------- Toast ---------- */
  function toast(msg) {
    let el = $('.toast');
    if (!el) { el = document.createElement('div'); el.className = 'toast'; document.body.appendChild(el); }
    el.textContent = msg;
    el.classList.add('is-visible');
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove('is-visible'), 2200);
  }

  /* ---------- Drawers ---------- */
  let lastFocus = null;
  function openDrawer(id) {
    const d = document.getElementById(id);
    if (!d) return;
    lastFocus = document.activeElement;
    d.classList.add('is-open');
    d.setAttribute('aria-hidden', 'false');
    document.body.classList.add('no-scroll');
    const f = $('button, a, input', $('.drawer__panel', d));
    if (f) setTimeout(() => f.focus(), 50);
  }
  function closeDrawer(d) {
    d.classList.remove('is-open');
    d.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('no-scroll');
    if (lastFocus) lastFocus.focus();
  }
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-open-drawer]');
    if (opener) { e.preventDefault(); openDrawer(opener.dataset.openDrawer); return; }
    const closer = e.target.closest('[data-close-drawer]');
    if (closer) { e.preventDefault(); closeDrawer(closer.closest('.drawer')); }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    $$('.drawer.is-open').forEach(closeDrawer);
    const s = $('.search-modal.is-open');
    if (s) s.classList.remove('is-open');
  });

  /* ---------- Search toggle ---------- */
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-search-toggle]');
    if (!t) return;
    e.preventDefault();
    const m = $('#SearchModal');
    if (!m) return;
    m.classList.toggle('is-open');
    if (m.classList.contains('is-open')) $('input', m).focus();
  });

  /* ---------- Sticky header shadow ---------- */
  const header = $('.header-wrapper');
  if (header) {
    const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Announcement rotator ---------- */
  $$('[data-announcement]').forEach((bar) => {
    const items = $$('.announcement__item', bar);
    if (items.length < 2) return;
    let i = 0;
    setInterval(() => {
      items[i].classList.remove('is-active');
      i = (i + 1) % items.length;
      items[i].classList.add('is-active');
    }, parseInt(bar.dataset.speed || '4', 10) * 1000);
  });

  /* ---------- Reveal on scroll ---------- */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -60px 0px' });
    $$('.reveal').forEach((el) => io.observe(el));
  } else {
    $$('.reveal').forEach((el) => el.classList.add('is-in'));
  }

  /* ---------- Countdown ---------- */
  function startCountdown(el) {
    let end;
    if (el.dataset.mode === 'evergreen') {
      // Resets every day at midnight (local time) — perpetual "ends today"
      end = new Date(); end.setHours(23, 59, 59, 999);
    } else {
      end = new Date(el.dataset.end);
      if (isNaN(end)) return;
    }
    const units = { d: $('[data-d]', el), h: $('[data-h]', el), m: $('[data-m]', el), s: $('[data-s]', el) };
    const pad = (n) => String(n).padStart(2, '0');
    const tick = () => {
      let diff = Math.max(0, end - new Date());
      if (diff === 0 && el.dataset.mode === 'evergreen') { end.setDate(end.getDate() + 1); diff = end - new Date(); }
      const d = Math.floor(diff / 864e5), h = Math.floor(diff / 36e5) % 24, m = Math.floor(diff / 6e4) % 60, s = Math.floor(diff / 1e3) % 60;
      if (units.d) units.d.textContent = pad(d);
      if (units.h) units.h.textContent = pad(h);
      if (units.m) units.m.textContent = pad(m);
      if (units.s) units.s.textContent = pad(s);
      if (diff === 0 && el.dataset.hideOnEnd === 'true') el.closest('.shopify-section').hidden = true;
    };
    tick();
    setInterval(tick, 1000);
  }
  $$('[data-countdown]').forEach(startCountdown);

  /* ---------- Cart (AJAX) ---------- */
  const Cart = {
    async fetchSections() {
      const res = await fetch(`${window.theme.routes.root}?sections=cart-drawer-content`);
      return res.json();
    },
    async refresh(open) {
      try {
        const sections = await this.fetchSections();
        const html = sections['cart-drawer-content'];
        const wrap = $('#CartDrawerContent');
        if (wrap && html) {
          const doc = new DOMParser().parseFromString(html, 'text/html');
          const fresh = doc.querySelector('#CartDrawerContent');
          if (fresh) wrap.innerHTML = fresh.innerHTML;
        }
        const cart = await (await fetch(`${window.theme.routes.cart}.js`)).json();
        $$('[data-cart-count]').forEach((c) => { c.textContent = cart.item_count; c.dataset.count = cart.item_count; });
        if (open) openDrawer('CartDrawer');
      } catch (err) { console.error(err); }
    },
    async add(formData) {
      const res = await fetch(`${window.theme.routes.cartAdd}.js`, {
        method: 'POST',
        headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.description || data.message || 'Error');
      return data;
    },
    async change(line, quantity) {
      const drawer = $('#CartDrawer');
      if (drawer) drawer.classList.add('is-loading');
      const res = await fetch(`${window.theme.routes.cartChange}.js`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ line, quantity })
      });
      const data = await res.json();
      if (!res.ok) toast(data.description || data.message || 'שגיאה');
      await this.refresh(false);
      if (drawer) drawer.classList.remove('is-loading');
    }
  };
  window.theme.cart = Cart;

  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('form[data-ajax-cart]');
    if (!form || window.theme.cartType !== 'drawer') return;
    e.preventDefault();
    const btn = $('[type="submit"]', form);
    const label = btn ? btn.innerHTML : '';
    if (btn) { btn.setAttribute('aria-disabled', 'true'); btn.innerHTML = window.theme.strings.adding; }
    try {
      await Cart.add(new FormData(form));
      await Cart.refresh(true);
    } catch (err) {
      toast(err.message);
    } finally {
      if (btn) { btn.removeAttribute('aria-disabled'); btn.innerHTML = label; }
    }
  });

  // Quantity +/- buttons (product form & cart)
  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-qty-btn]');
    if (!b) return;
    e.preventDefault();
    const input = $('input', b.closest('.qty'));
    const step = b.dataset.qtyBtn === 'plus' ? 1 : -1;
    const min = parseInt(input.min || '0', 10);
    input.value = Math.max(min, (parseInt(input.value, 10) || 0) + step);
    input.dispatchEvent(new Event('change', { bubbles: true }));
  });

  document.addEventListener('change', (e) => {
    const input = e.target.closest('[data-cart-line-qty]');
    if (!input) return;
    Cart.change(parseInt(input.dataset.cartLineQty, 10), parseInt(input.value, 10) || 0);
  });
  document.addEventListener('click', (e) => {
    const rm = e.target.closest('[data-cart-remove]');
    if (!rm) return;
    e.preventDefault();
    Cart.change(parseInt(rm.dataset.cartRemove, 10), 0);
  });

  /* ---------- Product page ---------- */
  function initProduct(root) {
    const dataEl = $('[data-product-json]', root);
    if (!dataEl) return;
    const product = JSON.parse(dataEl.textContent);
    const form = $('form[data-product-form]', root);
    const idInput = form ? $('input[name="id"]', form) : null;
    const atcBtns = $$('[data-atc]', root).concat($$('[data-atc]', $('#StickyAtc') || document.createElement('div')));
    const priceEls = $$('[data-price-wrap]', root).concat($$('[data-price-wrap]', $('#StickyAtc') || document.createElement('div')));
    const stockEl = $('[data-stock]', root);
    const threshold = stockEl ? parseInt(stockEl.dataset.threshold || '10', 10) : 10;

    function selectedOptions() {
      return product.options.map((_, i) => {
        const checked = $(`[data-option-index="${i}"]:checked`, root);
        if (checked) return checked.value;
        const sel = $(`select[data-option-index="${i}"]`, root);
        return sel ? sel.value : null;
      });
    }

    function findVariant(opts) {
      return product.variants.find((v) => v.options.every((o, i) => o === opts[i]));
    }

    function updateAvailability(opts) {
      // Mark option values that don't produce an available variant (given other selections)
      product.options.forEach((_, i) => {
        $$(`input[data-option-index="${i}"]`, root).forEach((input) => {
          const test = opts.slice(); test[i] = input.value;
          const v = findVariant(test);
          input.classList.toggle('is-unavailable', !v || !v.available);
        });
      });
    }

    function renderPrice(v) {
      priceEls.forEach((wrap) => {
        const cur = $('[data-price]', wrap), cmp = $('[data-compare]', wrap), save = $('[data-save]', wrap);
        const onSale = v.compare_at_price && v.compare_at_price > v.price;
        wrap.classList.toggle('price--sale', !!onSale);
        if (cur) cur.textContent = formatMoney(v.price);
        if (cmp) { cmp.textContent = onSale ? formatMoney(v.compare_at_price) : ''; cmp.hidden = !onSale; }
        if (save) {
          if (onSale) {
            const pct = Math.round(((v.compare_at_price - v.price) / v.compare_at_price) * 100);
            save.textContent = save.dataset.style === 'amount'
              ? `חסכון של ${formatMoney(v.compare_at_price - v.price)}`
              : `${pct}% הנחה`;
          }
          save.hidden = !onSale;
        }
      });
    }

    function renderStock(v) {
      if (!stockEl) return;
      const qty = product.inventory[v.id];
      if (v.available && typeof qty === 'number' && qty > 0 && qty <= threshold) {
        stockEl.hidden = false;
        $('[data-stock-qty]', stockEl).textContent = qty;
        const bar = $('.stock-bar span', stockEl);
        if (bar) bar.style.width = Math.max(8, (qty / threshold) * 100) + '%';
      } else {
        stockEl.hidden = true;
      }
    }

    function onChange() {
      const opts = selectedOptions();
      $$('[data-selected-value]', root).forEach((el) => { el.textContent = opts[el.dataset.selectedValue] || ''; });
      updateAvailability(opts);
      const v = findVariant(opts);
      atcBtns.forEach((b) => {
        const label = $('[data-atc-label]', b) || b;
        if (!v) { b.disabled = true; label.textContent = window.theme.strings.unavailable; }
        else if (!v.available) { b.disabled = true; label.textContent = window.theme.strings.soldOut; }
        else { b.disabled = false; label.textContent = b.dataset.label || window.theme.strings.addToCart; }
      });
      if (!v) return;
      if (idInput) idInput.value = v.id;
      renderPrice(v);
      renderStock(v);
      if (v.featured_media) goToMedia(v.featured_media.id);
      const url = new URL(window.location.href);
      url.searchParams.set('variant', v.id);
      window.history.replaceState({}, '', url.toString());
    }

    root.addEventListener('change', (e) => { if (e.target.matches('[data-option-index]')) onChange(); });

    // Gallery
    const main = $('.gallery__main', root);
    const thumbs = $$('.gallery__thumb', root);
    const dots = $$('.gallery__dots span', root);
    function setActive(idx) {
      thumbs.forEach((t, i) => t.classList.toggle('is-active', i === idx));
      dots.forEach((d, i) => d.classList.toggle('is-active', i === idx));
    }
    function goToMedia(mediaId) {
      if (!main) return;
      const slide = $(`[data-media-id="${mediaId}"]`, main);
      if (!slide) return;
      main.scrollTo({ left: slide.offsetLeft - main.offsetLeft, behavior: 'smooth' });
    }
    thumbs.forEach((t) => t.addEventListener('click', () => goToMedia(t.dataset.target)));
    if (main && 'IntersectionObserver' in window) {
      const slides = $$('.gallery__slide', main);
      const gio = new IntersectionObserver((entries) => {
        entries.forEach((en) => { if (en.isIntersecting) setActive(slides.indexOf(en.target)); });
      }, { root: main, threshold: 0.6 });
      slides.forEach((s) => gio.observe(s));
    }

    // Initial state
    const initial = product.variants.find((v) => String(v.id) === String(idInput && idInput.value));
    if (initial) { updateAvailability(initial.options); renderStock(initial); }

    // Live viewers (social proof)
    const viewers = $('[data-viewers]', root);
    if (viewers) {
      const min = parseInt(viewers.dataset.min || '8', 10), max = parseInt(viewers.dataset.max || '30', 10);
      let n = Math.floor(min + Math.random() * (max - min));
      const out = $('[data-viewers-count]', viewers);
      out.textContent = n;
      setInterval(() => {
        n = Math.min(max, Math.max(min, n + Math.round((Math.random() - 0.5) * 4)));
        out.textContent = n;
      }, 5000);
    }

    // Delivery estimate
    $$('[data-delivery]', root).forEach((el) => {
      const minD = parseInt(el.dataset.min, 10), maxD = parseInt(el.dataset.max, 10);
      const addBusinessDays = (date, days) => {
        const d = new Date(date);
        while (days > 0) { d.setDate(d.getDate() + 1); if (d.getDay() !== 5 && d.getDay() !== 6) days--; }
        return d;
      };
      const opts = { weekday: 'long', day: 'numeric', month: 'numeric' };
      const f = (d) => d.toLocaleDateString('he-IL', opts);
      $('[data-delivery-from]', el).textContent = f(addBusinessDays(new Date(), minD));
      $('[data-delivery-to]', el).textContent = f(addBusinessDays(new Date(), maxD));
    });

    // Sticky add to cart
    const sticky = $('#StickyAtc');
    const mainAtc = $('[data-atc]', root);
    if (sticky && mainAtc && 'IntersectionObserver' in window) {
      document.body.classList.add('has-sticky-atc');
      const sio = new IntersectionObserver(([en]) => {
        const passed = !en.isIntersecting && en.boundingClientRect.top < 0;
        sticky.classList.toggle('is-visible', passed);
      });
      sio.observe(mainAtc);
      $('[data-sticky-submit]', sticky).addEventListener('click', (e) => {
        e.preventDefault();
        if (form.requestSubmit) form.requestSubmit(); else $('[type="submit"]', form).click();
      });
    }
  }
  $$('[data-product-root]').forEach(initProduct);

  /* ---------- Collection sort / filters ---------- */
  document.addEventListener('change', (e) => {
    const sort = e.target.closest('[data-sort]');
    if (sort) {
      const url = new URL(window.location.href);
      url.searchParams.set('sort_by', sort.value);
      url.searchParams.delete('page');
      window.location.href = url.toString();
      return;
    }
    const filterInput = e.target.closest('[data-filter-form] input[type="checkbox"]');
    if (filterInput) filterInput.form.submit();
  });

  /* ---------- Sales popup ---------- */
  const pop = $('#SalesPop');
  const popData = $('#SalesPopData');
  if (pop && popData) {
    let data;
    try { data = JSON.parse(popData.textContent); } catch (e) { data = null; }
    let closed = false;
    try { closed = sessionStorage.getItem('salesPopClosed') === '1'; } catch (e) { /* storage unavailable */ }
    if (data && data.products.length && !closed) {
      const pick = (arr) => arr[Math.floor(Math.random() * arr.length)].trim();
      const show = () => {
        const p = pick(data.products.map((x) => JSON.stringify(x)));
        const prod = JSON.parse(p);
        $('.sales-pop__who', pop).textContent = `${pick(data.names)} מ${pick(data.cities)} רכש/ה`;
        $('.sales-pop__what', pop).textContent = prod.title;
        $('.sales-pop__when', pop).textContent = `לפני ${2 + Math.floor(Math.random() * 40)} דקות`;
        $('.sales-pop__img', pop).style.backgroundImage = prod.image ? `url(${prod.image})` : '';
        pop.onclick = (e) => { if (!e.target.closest('.sales-pop__close')) window.location.href = prod.url; };
        pop.hidden = false;
        setTimeout(() => { pop.hidden = true; }, 6000);
      };
      $('.sales-pop__close', pop).addEventListener('click', (e) => {
        e.stopPropagation();
        pop.hidden = true;
        clearInterval(timer);
        try { sessionStorage.setItem('salesPopClosed', '1'); } catch (err) { /* ignore */ }
      });
      setTimeout(show, 8000);
      const timer = setInterval(show, 25000);
    }
  }
})();
