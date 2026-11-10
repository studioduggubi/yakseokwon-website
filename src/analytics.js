/* Official-site page statistics. Preview builds and tracking opt-outs stay untracked. */
(() => {
  'use strict';
  const script = document.currentScript;
  const id = script?.dataset.measurementId;
  const origin = script?.dataset.origin;
  if (!/^G-[A-Z0-9]+$/.test(id || '') || origin !== 'https://yakseokwon.com' || location.origin !== origin || document.documentElement.dataset.siteProfile !== 'production') return;
  const key = 'ys-analytics-disabled';
  const flag = 'ga-disable-' + id;
  const browserOptOut = navigator.globalPrivacyControl === true || navigator.doNotTrack === '1' || window.doNotTrack === '1';
  let disabled = window[flag] === true || browserOptOut;
  try { disabled = disabled || localStorage.getItem(key) === '1'; } catch (_) {}
  window[flag] = disabled;
  const button = document.querySelector('[data-analytics-choice]');
  const status = document.querySelector('[data-analytics-status]');
  const updateChoice = () => {
    if (!button) return;
    button.disabled = browserOptOut;
    button.textContent = disabled ? button.dataset.allowLabel : button.dataset.stopLabel;
    button.setAttribute('aria-pressed', String(disabled));
    if (status) status.textContent = browserOptOut ? button.dataset.blockedLabel : '';
  };
  updateChoice();
  let started = false;
  const start = () => {
    if (disabled || started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    let referrer = '';
    try { referrer = new URL(document.referrer).origin + '/'; } catch (_) {}
    window.gtag('js', new Date());
    window.gtag('config', id, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      page_location: location.origin + location.pathname,
      page_referrer: referrer,
      cookie_flags: 'SameSite=Lax;Secure',
      cookie_expires: 34128000
    });
    const loader = document.createElement('script');
    loader.async = true;
    loader.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(loader);
  };
  button?.addEventListener('click', () => {
    if (browserOptOut) return;
    disabled = !disabled;
    window[flag] = disabled;
    try { localStorage.setItem(key, disabled ? '1' : '0'); } catch (_) {}
    if (disabled) {
      for (const cookie of document.cookie.split(';')) {
        const name = cookie.trim().split('=')[0];
        if (!/^_ga(?:_|$)/.test(name)) continue;
        for (const domain of ['', ';domain=yakseokwon.com', ';domain=.yakseokwon.com']) document.cookie = name + '=;path=/;max-age=0;SameSite=Lax;Secure' + domain;
      }
    } else if (started) location.reload();
    else start();
    updateChoice();
  });
  start();
})();
