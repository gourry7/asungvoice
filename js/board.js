/* 자료실 · 설치사례 · 공지사항 — JSON 게시판 렌더링 */
(function () {
  'use strict';

  const DATA_URL = new URL('../data/support-board.json', document.currentScript.src).href;
  const CACHE_KEY = 'asung_board_cache';

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function linkAttrs(url) {
    if (!url || url.startsWith('#')) return '';
    return ' target="_blank" rel="noopener"';
  }

  async function loadBoard() {
    try {
      const res = await fetch(DATA_URL + '?t=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) throw new Error('fetch failed');
      const data = await res.json();
      sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
      return data;
    } catch {
      const cached = sessionStorage.getItem(CACHE_KEY);
      if (cached) return JSON.parse(cached);
      throw new Error('게시판 데이터를 불러올 수 없습니다.');
    }
  }

  function renderResources(el, items) {
    const rows = items.map((r, i) =>
      `<tr><td>${items.length - i}</td>` +
      `<td><a href="${esc(r.url || '#')}"${linkAttrs(r.url)}>${esc(r.title)}</a></td>` +
      `<td><span class="board-badge">${esc(r.note || '다운로드')}</span></td></tr>`
    ).join('');
    el.innerHTML =
      `<table class="board-table"><thead><tr><th>번호</th><th>제목</th><th>비고</th></tr></thead>` +
      `<tbody>${rows || '<tr><td colspan="3">등록된 자료가 없습니다.</td></tr>'}</tbody></table>`;
  }

  function openModal(title, body) {
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
    modal.querySelector('.board-modal__body').innerHTML = body.replace(/\n/g, '<br>');
    modal.hidden = false;
  }

  function caseHref(item) {
    if (item.url) return item.url;
    if (item.content) return '#';
    return '#';
  }

  function renderCases(el, items) {
    const cards = items.map(c => {
      const href = caseHref(c);
      const hasModal = !c.url && c.content;
      const attrs = hasModal
        ? ` href="#" data-case-id="${esc(c.id)}" class="case-card case-card--modal"`
        : ` href="${esc(href)}"${linkAttrs(href)} class="case-card"`;
      const img = c.image
        ? `<img src="${esc(c.image)}" alt="${esc(c.title)}" loading="lazy">`
        : '<div class="case-card__placeholder">사진 없음</div>';
      return `<a${attrs}>${img}<span>${esc(c.title)}</span></a>`;
    }).join('');
    el.innerHTML = `<div class="case-grid">${cards || '<p>등록된 설치사례가 없습니다.</p>'}</div>`;
    el.querySelectorAll('[data-case-id]').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const item = items.find(x => x.id === a.dataset.caseId);
        if (item) openModal(item.title, item.content || '');
      });
    });
  }

  function renderNotices(el, items) {
    const rows = items.map(n => {
      const hasModal = !n.url && n.content;
      if (hasModal) {
        return `<tr><td>${esc(n.date)}</td><td><a href="#" data-notice-id="${esc(n.id)}">${esc(n.title)}</a></td></tr>`;
      }
      return `<tr><td>${esc(n.date)}</td><td><a href="${esc(n.url || '#')}"${linkAttrs(n.url)}>${esc(n.title)}</a></td></tr>`;
    }).join('');
    el.innerHTML =
      `<table class="board-table"><thead><tr><th>날짜</th><th>제목</th></tr></thead>` +
      `<tbody>${rows || '<tr><td colspan="2">등록된 공지가 없습니다.</td></tr>'}</tbody></table>`;
    el.querySelectorAll('[data-notice-id]').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const item = items.find(x => x.id === a.dataset.noticeId);
        if (item) openModal(item.title, item.content || '');
      });
    });
  }

  async function init() {
    const mount = document.querySelector('[data-board]');
    if (!mount) return;
    const type = mount.dataset.board;
    mount.innerHTML = '<p class="board-loading">불러오는 중…</p>';
    try {
      const data = await loadBoard();
      if (type === 'resources') renderResources(mount, data.resources || []);
      else if (type === 'cases') renderCases(mount, data.cases || []);
      else if (type === 'notices') renderNotices(mount, data.notices || []);
    } catch (err) {
      mount.innerHTML = `<p class="board-error">${esc(err.message)}</p>`;
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
