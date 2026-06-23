/* 고객지원 게시판 관리자 — data/support-board.json 편집 */
(function () {
  'use strict';

  const ADMIN_PASS = 'asungvoice';
  const SESSION_KEY = 'asung_admin_ok';
  const GITHUB_KEY = 'asung_admin_github';
  const DATA_PATH = 'data/support-board.json';
  const scriptBase = document.currentScript.src.replace(/\/js\/admin\.js.*$/, '/');

  let board = { resources: [], cases: [], notices: [] };
  let activeTab = 'resources';
  let editingId = null;

  const $ = sel => document.querySelector(sel);
  const $$ = sel => [...document.querySelectorAll(sel)];

  function uid(prefix) {
    return prefix + '-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  }

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s ?? '';
    return d.innerHTML;
  }

  async function loadBoard() {
    const url = new URL(DATA_PATH, scriptBase).href;
    const res = await fetch(url + '?t=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('게시판 데이터를 불러올 수 없습니다.');
    board = await res.json();
  }

  function getGithubCfg() {
    try { return JSON.parse(localStorage.getItem(GITHUB_KEY) || '{}'); }
    catch { return {}; }
  }

  function setGithubCfg(cfg) {
    localStorage.setItem(GITHUB_KEY, JSON.stringify(cfg));
  }

  async function saveToGithub(jsonText) {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      throw new Error('GitHub 설정(저장소·토큰)을 먼저 입력해 주세요.');
    }
    const api = `https://api.github.com/repos/${cfg.owner}/${cfg.repo}/contents/${DATA_PATH}`;
    const headers = {
      Authorization: 'Bearer ' + cfg.token,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json'
    };
    let sha = null;
    const getRes = await fetch(api + '?ref=' + (cfg.branch || 'main'), { headers });
    if (getRes.ok) sha = (await getRes.json()).sha;
    const body = {
      message: 'Update support board via admin',
      content: btoa(unescape(encodeURIComponent(jsonText))),
      branch: cfg.branch || 'main'
    };
    if (sha) body.sha = sha;
    const putRes = await fetch(api, { method: 'PUT', headers, body: JSON.stringify(body) });
    if (!putRes.ok) {
      const err = await putRes.json().catch(() => ({}));
      throw new Error(err.message || 'GitHub 저장 실패');
    }
  }

  function downloadJson() {
    const blob = new Blob([JSON.stringify(board, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'support-board.json';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  async function uploadFileToGithub(file, folder) {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      throw new Error('파일 업로드에는 GitHub 토큰 설정이 필요합니다.');
    }
    const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
    const path = `assets/board/${folder}/${Date.now()}-${safeName}`;
    const buf = await file.arrayBuffer();
    const bytes = new Uint8Array(buf);
    let binary = '';
    bytes.forEach(b => { binary += String.fromCharCode(b); });
    const content = btoa(binary);
    const api = `https://api.github.com/repos/${cfg.owner}/${cfg.repo}/contents/${path}`;
    const headers = {
      Authorization: 'Bearer ' + cfg.token,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json'
    };
    const putRes = await fetch(api, {
      method: 'PUT',
      headers,
      body: JSON.stringify({
        message: 'Upload board file via admin',
        content,
        branch: cfg.branch || 'main'
      })
    });
    if (!putRes.ok) throw new Error('파일 업로드 실패');
    const base = cfg.pagesUrl || `https://${cfg.owner}.github.io/${cfg.repo}`;
    return base.replace(/\/$/, '') + '/' + path;
  }

  function showLogin() {
    $('#admin-app').hidden = true;
    $('#admin-login').hidden = false;
  }

  function showApp() {
    $('#admin-login').hidden = true;
    $('#admin-app').hidden = false;
    renderList();
  }

  function renderList() {
    const list = $('#admin-list');
    const items = board[activeTab] || [];
    if (!items.length) {
      list.innerHTML = '<p class="admin-empty">등록된 항목이 없습니다.</p>';
      return;
    }
    list.innerHTML = items.map(item => {
      const sub = activeTab === 'notices' ? item.date : (item.note || item.image ? '첨부/링크 있음' : '');
      return `<div class="admin-item neu-card" data-id="${esc(item.id)}">
        <div class="admin-item__main"><strong>${esc(item.title)}</strong>${sub ? `<span>${esc(sub)}</span>` : ''}</div>
        <div class="admin-item__actions">
          <button type="button" class="btn btn--ghost btn--sm" data-edit="${esc(item.id)}">수정</button>
          <button type="button" class="btn btn--ghost btn--sm admin-del" data-del="${esc(item.id)}">삭제</button>
        </div></div>`;
    }).join('');

    list.querySelectorAll('[data-edit]').forEach(btn => {
      btn.addEventListener('click', () => openForm(btn.dataset.edit));
    });
    list.querySelectorAll('[data-del]').forEach(btn => {
      btn.addEventListener('click', () => {
        if (!confirm('삭제하시겠습니까?')) return;
        board[activeTab] = board[activeTab].filter(x => x.id !== btn.dataset.del);
        renderList();
      });
    });
  }

  function openForm(id) {
    editingId = id || null;
    const form = $('#admin-form');
    form.hidden = false;
    const item = id ? board[activeTab].find(x => x.id === id) : null;
    $('#f-title').value = item?.title || '';
    $('#f-url').value = item?.url || '';
    $('#f-note').value = item?.note || '다운로드';
    $('#f-date').value = item?.date || new Date().toISOString().slice(0, 10);
    $('#f-image').value = item?.image || '';
    $('#f-content').value = item?.content || '';
    $('#form-title').textContent = (id ? '수정' : '새 글') + ' — ' + tabLabel(activeTab);
    $$('.admin-field').forEach(f => {
      f.hidden = !fieldVisible(f.dataset.field, activeTab);
    });
  }

  function tabLabel(tab) {
    return { resources: '자료실', cases: '설치사례', notices: '공지사항' }[tab] || tab;
  }

  function fieldVisible(field, tab) {
    if (field === 'date') return tab === 'notices';
    if (field === 'note') return tab === 'resources';
    if (field === 'image') return tab === 'cases';
    if (field === 'content') return tab === 'cases' || tab === 'notices';
    return true;
  }

  function closeForm() {
    editingId = null;
    $('#admin-form').hidden = true;
  }

  function saveForm(e) {
    e.preventDefault();
    const title = $('#f-title').value.trim();
    if (!title) return alert('제목을 입력해 주세요.');
    const entry = {
      id: editingId || uid(activeTab.slice(0, 4)),
      title,
      url: $('#f-url').value.trim()
    };
    if (activeTab === 'resources') entry.note = $('#f-note').value.trim() || '다운로드';
    if (activeTab === 'notices') entry.date = $('#f-date').value || new Date().toISOString().slice(0, 10);
    if (activeTab === 'cases') {
      entry.image = $('#f-image').value.trim();
      entry.content = $('#f-content').value.trim();
    }
    if (activeTab === 'notices') entry.content = $('#f-content').value.trim();

    if (editingId) {
      const idx = board[activeTab].findIndex(x => x.id === editingId);
      if (idx >= 0) board[activeTab][idx] = { ...board[activeTab][idx], ...entry };
    } else {
      board[activeTab].unshift(entry);
    }
    closeForm();
    renderList();
  }

  async function persistAll() {
    const json = JSON.stringify(board, null, 2);
    const status = $('#save-status');
    status.textContent = '저장 중…';
    try {
      await saveToGithub(json);
      status.textContent = 'GitHub에 저장되었습니다. 사이트 반영까지 1~2분 걸릴 수 있습니다.';
    } catch (err) {
      downloadJson();
      status.textContent = 'GitHub 저장 실패 — JSON 파일을 다운로드했습니다. data/support-board.json 으로 업로드해 주세요. (' + err.message + ')';
    }
  }

  function bindEvents() {
    $('#login-form').addEventListener('submit', e => {
      e.preventDefault();
      if ($('#login-pass').value === ADMIN_PASS) {
        sessionStorage.setItem(SESSION_KEY, '1');
        showApp();
      } else alert('비밀번호가 올바르지 않습니다.');
    });

    $$('.admin-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        activeTab = tab.dataset.tab;
        $$('.admin-tab').forEach(t => t.classList.toggle('is-active', t === tab));
        closeForm();
        renderList();
      });
    });

    $('#btn-new').addEventListener('click', () => openForm(null));
    $('#btn-cancel').addEventListener('click', closeForm);
    $('#item-form').addEventListener('submit', saveForm);
    $('#btn-save-github').addEventListener('click', persistAll);
    $('#btn-export').addEventListener('click', downloadJson);

    $('#btn-import').addEventListener('click', () => $('#import-file').click());
    $('#import-file').addEventListener('change', e => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          board = JSON.parse(reader.result);
          renderList();
          alert('JSON을 불러왔습니다. 저장 버튼을 눌러 반영하세요.');
        } catch { alert('JSON 형식이 올바르지 않습니다.'); }
      };
      reader.readAsText(file);
    });

    $('#github-form').addEventListener('submit', e => {
      e.preventDefault();
      setGithubCfg({
        owner: $('#gh-owner').value.trim(),
        repo: $('#gh-repo').value.trim(),
        branch: $('#gh-branch').value.trim() || 'main',
        token: $('#gh-token').value.trim(),
        pagesUrl: $('#gh-pages').value.trim()
      });
      alert('GitHub 설정을 저장했습니다.');
    });

    const cfg = getGithubCfg();
    if (cfg.owner) $('#gh-owner').value = cfg.owner;
    if (cfg.repo) $('#gh-repo').value = cfg.repo;
    if (cfg.branch) $('#gh-branch').value = cfg.branch;
    if (cfg.pagesUrl) $('#gh-pages').value = cfg.pagesUrl;

    $('#f-file').addEventListener('change', async e => {
      const file = e.target.files[0];
      if (!file) return;
      try {
        const folder = activeTab === 'resources' ? 'files' : 'images';
        const url = await uploadFileToGithub(file, folder);
        if (activeTab === 'cases') $('#f-image').value = url;
        else $('#f-url').value = url;
        alert('파일이 업로드되었습니다.');
      } catch (err) {
        alert(err.message);
      }
      e.target.value = '';
    });

    $('#btn-logout').addEventListener('click', () => {
      sessionStorage.removeItem(SESSION_KEY);
      showLogin();
    });
  }

  async function init() {
    bindEvents();
    if (sessionStorage.getItem(SESSION_KEY) !== '1') {
      showLogin();
      return;
    }
    try {
      await loadBoard();
      showApp();
    } catch (err) {
      alert(err.message);
      showLogin();
    }
  }

  init();
})();
