/* 자료실 · 설치사례 · 공지사항 — JSON 게시판 렌더링 */
(function () {
  'use strict';

  const CACHE_PREFIX = 'asung_board_v3';
  const PAGE_SIZE = 15;
  const CASE_PAGE_SIZE = 12;
  const DATA_FILES = {
    resources: '../data/board-resources.json',
    cases: '../data/board-cases.json',
    notices: '../data/board-notices.json'
  };

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function dataUrl(type) {
    const mount = document.querySelector('[data-board]');
    const custom = mount && mount.dataset.boardSrc;
    const rel = custom || DATA_FILES[type] || '../data/support-board.json';
    return new URL(rel, window.location.href).href;
  }

  /** support/*.html 기준 로컬 에셋 경로 */
  function assetUrl(path) {
    if (!path) return '';
    if (/^https?:\/\//i.test(path)) return path;
    const clean = path.replace(/^(\.\.\/)+/, '');
    return '../' + clean.replace(/^\/+/, '');
  }

  function isLocalPath(path) {
    return path && !/^https?:\/\//i.test(path);
  }

  function readCache(type) {
    try {
      const cached = sessionStorage.getItem(CACHE_PREFIX + ':' + type);
      if (cached) return JSON.parse(cached);
    } catch { /* ignore corrupt cache */ }
    return null;
  }

  function writeCache(type, items) {
    try {
      sessionStorage.setItem(CACHE_PREFIX + ':' + type, JSON.stringify(items));
    } catch { /* quota / private mode — fetch result still usable */ }
  }

  async function loadBoard(type) {
    if (window.location.protocol === 'file:') {
      throw new Error('로컬 파일로는 게시판을 불러올 수 없습니다. GitHub Pages 또는 로컬 서버에서 확인해 주세요.');
    }

    let items;
    try {
      const res = await fetch(dataUrl(type) + '?t=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) throw new Error('fetch failed');
      const json = await res.json();
      items = Array.isArray(json) ? json : (json[type] || []);
      if (!Array.isArray(items)) throw new Error('invalid data');
    } catch {
      items = readCache(type);
      if (items) return items;
      throw new Error('게시판 데이터를 불러올 수 없습니다.');
    }

    writeCache(type, items);
    return items;
  }

  function rewriteHtmlAssets(html) {
    if (!html) return '';
    return html.replace(
      /((?:src|href)=["'])(\.\/)?(\.\.\/)?(data\/[^"']+)(["'])/gi,
      (_, pre, _dot, _up, p, suf) => pre + assetUrl(p) + suf
    );
  }

  function openModal(title, bodyHtml, isHtml) {
    let modal = document.getElementById('board-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'board-modal';
      modal.className = 'board-modal';
      modal.innerHTML =
        '<div class="board-modal__box neu-card" role="dialog" aria-modal="true">' +
        '<button type="button" class="board-modal__close" aria-label="닫기">&times;</button>' +
        '<h3 class="board-modal__title"></h3>' +
        '<div class="board-modal__body"></div></div>';
      document.body.appendChild(modal);
      modal.addEventListener('click', e => {
        if (e.target === modal || e.target.closest('.board-modal__close')) modal.hidden = true;
      });
    }
    modal.querySelector('.board-modal__title').textContent = title;
    const body = modal.querySelector('.board-modal__body');
    if (isHtml) body.innerHTML = rewriteHtmlAssets(bodyHtml) || '<p>내용이 없습니다.</p>';
    else body.textContent = bodyHtml || '';
    modal.hidden = false;
  }

  function paginate(items, page, size) {
    const pageSize = size || PAGE_SIZE;
    const total = Math.max(1, Math.ceil(items.length / pageSize));
    const p = Math.min(Math.max(1, page), total);
    const start = (p - 1) * pageSize;
    return { page: p, total, slice: items.slice(start, start + pageSize) };
  }

  function pagerHtml(page, total, id) {
    if (total <= 1) return '';
    let btns = '';
    for (let i = 1; i <= total; i++) {
      btns += `<button type="button" class="board-page${i === page ? ' is-active' : ''}" data-board-page="${id}" data-page="${i}">${i}</button>`;
    }
    return `<nav class="board-pager" aria-label="페이지">${btns}</nav>`;
  }

  function bindPager(el, id, renderPage) {
    el.querySelectorAll(`[data-board-page="${id}"]`).forEach(btn => {
      btn.addEventListener('click', () => {
        renderPage(Number(btn.dataset.page));
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  function resourceHref(item) {
    if (item.file) return assetUrl(item.file);
    if (item.url && isLocalPath(item.url)) return assetUrl(item.url);
    return item.url || '';
  }

  function renderResources(el, items) {
    const draw = p => {
      const { slice, total, page: cp } = paginate(items, p);
      const rows = slice.map((r, i) => {
        const num = items.length - ((cp - 1) * PAGE_SIZE + i);
        const href = resourceHref(r);
        const isFile = !!(r.file || (r.url && isLocalPath(r.url)));
        const title = href
          ? `<a href="${esc(href)}"${isFile ? '' : ' target="_blank" rel="noopener"'}>${esc(r.title)}</a>`
          : esc(r.title);
        const date = r.date ? `<td>${esc(r.date)}</td>` : '<td></td>';
        const note = isFile ? '다운로드' : (r.note || '링크');
        return `<tr><td>${num}</td><td>${title}</td>${date}<td><span class="board-badge">${esc(note)}</span></td></tr>`;
      }).join('');
      el.innerHTML =
        `<table class="board-table"><thead><tr><th>번호</th><th>제목</th><th>등록일</th><th>비고</th></tr></thead>` +
        `<tbody>${rows || '<tr><td colspan="4">등록된 자료가 없습니다.</td></tr>'}</tbody></table>` +
        pagerHtml(cp, total, 'resources');
      bindPager(el, 'resources', draw);
    };
    draw(1);
  }

  function renderCases(el, items) {
    const draw = p => {
      const { slice, total, page: cp } = paginate(items, p, CASE_PAGE_SIZE);
      const cards = slice.map(c => {
        const img = c.image
          ? `<img src="${esc(assetUrl(c.image))}" alt="${esc(c.title)}" loading="lazy">`
          : '<div class="case-card__placeholder">사진 없음</div>';
        return `<a href="#" data-case-id="${esc(c.id)}" class="case-card case-card--modal">${img}<span>${esc(c.title)}</span></a>`;
      }).join('');
      el.innerHTML =
        `<div class="case-grid">${cards || '<p>등록된 설치사례가 없습니다.</p>'}</div>` +
        pagerHtml(cp, total, 'cases');
      el.querySelectorAll('[data-case-id]').forEach(a => {
        a.addEventListener('click', e => {
          e.preventDefault();
          const item = items.find(x => x.id === a.dataset.caseId);
          if (item) openModal(item.title, item.contentHtml || item.content || '', !!(item.contentHtml || item.content));
        });
      });
      bindPager(el, 'cases', draw);
    };
    draw(1);
  }

  function renderNotices(el, items) {
    const draw = p => {
      const { slice, total, page: cp } = paginate(items, p);
      const rows = slice.map(n => {
        const pin = n.pinned ? ' <span class="board-badge">공지</span>' : '';
        return `<tr><td>${esc(n.date)}</td><td><a href="#" data-notice-id="${esc(n.id)}">${esc(n.title)}</a>${pin}</td></tr>`;
      }).join('');
      el.innerHTML =
        `<table class="board-table"><thead><tr><th>날짜</th><th>제목</th></tr></thead>` +
        `<tbody>${rows || '<tr><td colspan="2">등록된 공지가 없습니다.</td></tr>'}</tbody></table>` +
        pagerHtml(cp, total, 'notices');
      el.querySelectorAll('[data-notice-id]').forEach(a => {
        a.addEventListener('click', e => {
          e.preventDefault();
          const item = items.find(x => x.id === a.dataset.noticeId);
          if (item) openModal(item.title, item.contentHtml || item.content || '', !!(item.contentHtml || item.content));
        });
      });
      bindPager(el, 'notices', draw);
    };
    draw(1);
  }

  async function init() {
    const mount = document.querySelector('[data-board]');
    if (!mount) return;
    const type = mount.dataset.board;
    if (!type) return;
    mount.innerHTML = '<p class="board-loading">불러오는 중…</p>';
    try {
      const items = await loadBoard(type);
      if (type === 'resources') renderResources(mount, items);
      else if (type === 'cases') renderCases(mount, items);
      else if (type === 'notices') renderNotices(mount, items);
      else mount.innerHTML = '<p class="board-error">알 수 없는 게시판 유형입니다.</p>';
    } catch (err) {
      mount.innerHTML = `<p class="board-error">${esc(err.message)}</p>`;
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
