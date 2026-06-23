/* 아성보이스 공통 스크립트 */
(function () {
  'use strict';

  // Header scroll
  const header = document.querySelector('.header');
  if (header) {
    const onScroll = () => header.classList.toggle('is-solid', window.scrollY > 50);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Mobile menu
  const menuBtn = document.querySelector('.menu-btn');
  const mobileNav = document.querySelector('.mobile-nav');
  if (menuBtn && mobileNav) {
    menuBtn.addEventListener('click', () => {
      const open = mobileNav.classList.toggle('is-open');
      menuBtn.classList.toggle('is-open', open);
      menuBtn.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    mobileNav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      mobileNav.classList.remove('is-open');
      menuBtn.classList.remove('is-open');
      document.body.style.overflow = '';
    }));
  }

  // Scroll reveal
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
    reveals.forEach(el => obs.observe(el));
  }

  // Counter
  document.querySelectorAll('[data-count]').forEach(el => {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const target = +el.dataset.count;
        const suffix = el.dataset.suffix || '';
        const dur = 1600;
        const start = performance.now();
        const tick = now => {
          const p = Math.min((now - start) / dur, 1);
          const v = Math.floor((1 - Math.pow(1 - p, 3)) * target);
          el.textContent = v.toLocaleString() + suffix;
          if (p < 1) requestAnimationFrame(tick);
          else el.textContent = target.toLocaleString() + suffix;
        };
        requestAnimationFrame(tick);
        obs.unobserve(el);
      });
    }, { threshold: 0.4 });
    obs.observe(el);
  });

  // Hero swiper
  if (typeof Swiper !== 'undefined' && document.querySelector('.hero__slider.swiper')) {
    new Swiper('.hero__slider', {
      loop: true,
      autoplay: { delay: 5000, disableOnInteraction: false },
      pagination: { el: '.swiper-pagination', clickable: true },
      effect: 'fade',
      fadeEffect: { crossFade: true }
    });
  }

  // Active nav highlight
  const path = location.pathname;
  document.querySelectorAll('.nav__link, .sidebar__nav a').forEach(a => {
    if (a.getAttribute('href') && path.includes(a.getAttribute('href').replace(/^\.\./, '').replace(/^\//, ''))) {
      a.classList.add('is-active');
    }
  });
})();
