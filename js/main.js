/* 아성보이스 공통 스크립트 */
(function () {
  'use strict';

  const header = document.querySelector('.header');
  if (header) {
    const onScroll = () => header.classList.toggle('is-solid', window.scrollY > 50);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

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

  document.querySelectorAll('.reveal').forEach(el => {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
    obs.observe(el);
  });

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

  const path = location.pathname;
  document.querySelectorAll('.nav__link, .sidebar__nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (href && path.includes(href.replace(/^\.\./, '').replace(/^\//, ''))) {
      a.classList.add('is-active');
    }
  });

  const heroCarousel = document.querySelector('[data-hero-carousel]');
  if (heroCarousel) {
    const slides = [
      { src: 'assets/images/products/elevator.png', alt: '승강기 비명감지기', label: '승강기 비명감지기' },
      { src: 'assets/images/products/restroom-hero.png?v=1', alt: '화장실 비명감지기', label: '화장실 비명감지기' },
      { src: 'assets/images/products/control-panel.png', alt: '일괄소등스위치', label: '세대현관 · 일괄소등스위치' },
      { src: 'assets/images/products/home-keeper.png', alt: '마이안심이', label: '마이안심이' },
      { src: 'assets/images/products/pcb-module.png', alt: '비명인식 모듈', label: '비명인식 모듈' }
    ];
    const img = heroCarousel.querySelector('.hp-hero__img');
    const label = heroCarousel.querySelector('.hp-hero__label');
    const dotsWrap = heroCarousel.querySelector('.hp-hero__dots');
    let index = 0;
    let timer = null;
    const interval = 3500;

    slides.forEach((slide, i) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'hp-hero__dot' + (i === 0 ? ' is-active' : '');
      dot.setAttribute('role', 'tab');
      dot.setAttribute('aria-label', slide.label);
      dot.addEventListener('click', () => { go(i); restart(); });
      dotsWrap.appendChild(dot);
    });

    const dots = [...dotsWrap.querySelectorAll('.hp-hero__dot')];

    function go(i) {
      index = i;
      const slide = slides[i];
      img.classList.add('is-fading');
      setTimeout(() => {
        img.src = slide.src;
        img.alt = slide.alt;
        label.textContent = slide.label;
        img.classList.remove('is-fading');
      }, 220);
      dots.forEach((d, n) => {
        d.classList.toggle('is-active', n === i);
        d.setAttribute('aria-selected', n === i ? 'true' : 'false');
      });
    }

    function next() { go((index + 1) % slides.length); }

    function restart() {
      if (timer) clearInterval(timer);
      timer = setInterval(next, interval);
    }

    heroCarousel.addEventListener('mouseenter', () => { if (timer) clearInterval(timer); });
    heroCarousel.addEventListener('mouseleave', restart);
    slides.slice(1).forEach(s => { const preload = new Image(); preload.src = s.src; });
    restart();
  }
})();
