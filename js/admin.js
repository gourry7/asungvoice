/* 고객지원 게시판 관리자 */
(function () {
  'use strict';

  const SESSION_KEY = 'asung_admin_session';
  const LOCKOUT_KEY = 'asung_admin_lockout';
  const GITHUB_KEY = 'asung_admin_github';
  const DRAFT_KEY = 'asung_admin_draft';
  const DATA_PATH = 'data/support-board.json';
  const CONFIG_PATH = 'data/admin-config.json';
  const SESSION_SALT = 'asung-voice-admin-v2';
  const scriptBase = document.currentScript.src.replace(/\/js\/admin\.js.*$/, '/');

  let board = { resources: [], cases: [], notices: [] };
  let adminConfig = { sessionMinutes: 30, maxAttempts: 5, lockoutMinutes: 15, passwordHash: '' };
  let activeTab = 'resources';
  let editingId = null;
  let sessionPasswordHash = '';
  let idleTimer = null;

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

  async function sha256(text) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  async function loadAdminConfig() {
    const url = new URL(CONFIG_PATH, scriptBase).href;
    const res = await fetch(url + '?t=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('관리자 설정을 불러올 수 없습니다.');
    adminConfig = { ...adminConfig, ...(await res.json()) };
  }

  async function loadBoard() {
    const url = new URL(DATA_PATH, scriptBase).href;
    const res = await fetch(url + '?t=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error('게시판 데이터를 불러올 수 없습니다.');
    board = await res.json();
    restoreDraft();
  }

  function getLockout() {
    try { return JSON.parse(localStorage.getItem(LOCKOUT_KEY) || '{}'); }
    catch { return {}; }
  }

  function setLockout(data) {
    localStorage.setItem(LOCKOUT_KEY, JSON.stringify(data));
  }

  function isLockedOut() {
    const lo = getLockout();
    if (!lo.lockedUntil) return false;
    if (Date.now() < lo.lockedUntil) return true;
    setLockout({ attempts: 0 });
    return false;
  }

  function lockoutRemainingMs() {
    const lo = getLockout();
    return Math.max(0, (lo.lockedUntil || 0) - Date.now());
  }

  function recordFailedLogin() {
    const lo = getLockout();
    const attempts = (lo.attempts || 0) + 1;
    if (attempts >= adminConfig.maxAttempts) {
      setLockout({
        attempts,
        lockedUntil: Date.now() + adminConfig.lockoutMinutes * 60 * 1000
      });
    } else {
      setLockout({ attempts });
    }
  }

  function clearLockout() {
    setLockout({ attempts: 0 });
  }

  async function createSession(hash) {
    const token = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(24))));
    const expires = Date.now() + adminConfig.sessionMinutes * 60 * 1000;
    const sig = await sha256(token + expires + hash + SESSION_SALT);
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({ token, expires, sig, hash }));
    sessionPasswordHash = hash;
    resetIdleTimer();
  }

  async function validateSession() {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return false;
    let sess;
    try { sess = JSON.parse(raw); } catch { return false; }
    if (!sess.token || !sess.expires || !sess.sig || !sess.hash) return false;
    if (Date.now() > sess.expires) return false;
    const expected = await sha256(sess.token + sess.expires + sess.hash + SESSION_SALT);
    if (expected !== sess.sig) return false;
    sessionPasswordHash = sess.hash;
    return true;
  }

  function clearSession() {
    sessionStorage.removeItem(SESSION_KEY);
    sessionPasswordHash = '';
    if (idleTimer) clearTimeout(idleTimer);
  }

  function resetIdleTimer() {
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      alert('보안을 위해 세션이 만료되었습니다. 다시 로그인해 주세요.');
      clearSession();
      showLogin();
    }, adminConfig.sessionMinutes * 60 * 1000);
  }

  function touchSession() {
    if (sessionPasswordHash) resetIdleTimer();
  }

  function getGithubCfg() {
    try { return JSON.parse(localStorage.getItem(GITHUB_KEY) || '{}'); }
    catch { return {}; }
  }

  function setGithubCfg(cfg) {
    localStorage.setItem(GITHUB_KEY, JSON.stringify(cfg));
  }

  function githubReady() {
    const c = getGithubCfg();
    return !!(c.token && c.owner && c.repo);
  }

  async function saveToGithub(path, jsonText, message) {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      throw new Error('GitHub 설정(저장소·토큰)을 먼저 입력해 주세요.');
    }
    const api = `https://api.github.com/repos/${cfg.owner}/${cfg.repo}/contents/${path}`;
    const headers = {
      Authorization: 'Bearer ' + cfg.token,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json'
    };
    let sha = null;
    const getRes = await fetch(api + '?ref=' + (cfg.branch || 'main'), { headers });
    if (getRes.ok) sha = (await getRes.json()).sha;
    const body = {
      message: message || 'Update via admin',
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

  async function uploadBinaryToGithub(file, folder, onProgress) {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      throw new Error('파일 업로드에는 GitHub 설정이 필요합니다. 아래 「GitHub 연결」을 먼저 완료해 주세요.');
    }
    const safeName = file.name.replace(/[^a-zA-Z0-9._가-힣-]/g, '_');
    const path = `assets/board/${folder}/${Date.now()}-${safeName}`;
    const buf = await file.arrayBuffer();
    if (onProgress) onProgress(40);
    const bytes = new Uint8Array(buf);
    let binary = '';
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    const content = btoa(binary);
    if (onProgress) onProgress(70);
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
        message: 'Upload board file via admin: ' + safeName,
        content,
        branch: cfg.branch || 'main'
      })
    });
    if (!putRes.ok) throw new Error('파일 업로드 실패 — 토큰 권한(repo)을 확인해 주세요.');
    if (onProgress) onProgress(100);
    const base = cfg.pagesUrl || `https://${cfg.owner}.github.io/${cfg.repo}`;
    return base.replace(/\/$/, '') + '/' + path;
  }

  function saveDraft() {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(board));
  }

  function restoreDraft() {
    try {
      const draft = localStorage.getItem(DRAFT_KEY);
      if (!draft) return;
      const parsed = JSON.parse(draft);
      if (parsed && parsed.resources) board = parsed;
    } catch { /* ignore */ }
  }

  function downloadJson(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function setStatus(msg, type) {
    const el = $('#save-status');
    if (!el) return;
    el.textContent = msg;
    el.className = 'admin-status' + (type ? ' admin-status--' + type : '');
  }

  function updateSessionBadge() {
    const badge = $('#session-badge');
    if (!badge) return;
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) { badge.hidden = true; return; }
    try {
      const { expires } = JSON.parse(raw);
      const left = Math.max(0, Math.ceil((expires - Date.now()) / 60000));
      badge.textContent = '세션 ' + left + '분';
      badge.hidden = false;
    } catch { badge.hidden = true; }
  }

  function updateGithubBanner() {
    const banner = $('#github-banner');
    if (!banner) return;
    banner.hidden = githubReady();
  }

  function updateLockoutUI() {
    const err = $('#login-error');
    const btn = $('#login-form button[type="submit"]');
    if (!err || !btn) return;
    if (isLockedOut()) {
      const sec = Math.ceil(lockoutRemainingMs() / 1000);
      const min = Math.floor(sec / 60);
      const s = sec % 60;
      err.textContent = `로그인 시도가 너무 많습니다. ${min}분 ${s}초 후 다시 시도해 주세요.`;
      err.hidden = false;
      btn.disabled = true;
    } else {
      err.hidden = true;
      btn.disabled = false;
    }
  }

  function showLogin() {
    $('#admin-app').hidden = true;
    $('#admin-login').hidden = false;
    updateLockoutUI();
  }

  function showApp() {
    $('#admin-login').hidden = true;
    $('#admin-app').hidden = false;
    updateGithubBanner();
    updateSessionBadge();
    renderList();
    setInterval(updateSessionBadge, 30000);
  }

  function tabLabel(tab) {
    return { resources: '자료실', cases: '설치사례', notices: '공지사항' }[tab] || tab;
  }

  function fieldVisible(field, tab) {
    if (field === 'date') return tab === 'notices';
    if (field === 'note') return tab === 'resources';
    if (field === 'file-upload') return tab === 'resources';
    if (field === 'image-upload') return tab === 'cases';
    if (field === 'url-advanced') return tab === 'resources' || tab === 'cases' || tab === 'notices';
    if (field === 'image-url') return tab === 'cases';
    if (field === 'content') return tab === 'cases' || tab === 'notices';
    return true;
  }

  function updateFormFields() {
    $$('.admin-field').forEach(f => {
      f.hidden = !fieldVisible(f.dataset.field, activeTab);
    });
    const imgUrl = document.querySelector('[data-field="image-url"]');
    if (imgUrl) imgUrl.hidden = activeTab !== 'cases';
    const guide = $('#form-guide');
    if (guide) {
      const texts = {
        resources: '제목을 입력하고 자료 파일(PDF 등)을 업로드하세요.',
        cases: '제목을 입력하고 설치 사진을 업로드하세요.',
        notices: '제목·날짜를 입력하고, 링크 또는 본문을 작성하세요.'
      };
      guide.textContent = texts[activeTab] || '';
    }
  }

  function renderList() {
    const list = $('#admin-list');
    const items = board[activeTab] || [];
    if (!items.length) {
      list.innerHTML = '<p class="admin-empty">등록된 항목이 없습니다. 「+ 새 글」을 눌러 추가하세요.</p>';
      return;
    }
    list.innerHTML = items.map(item => {
      let sub = '';
      if (activeTab === 'notices') sub = item.date || '';
      else if (activeTab === 'cases') sub = item.image ? '📷 사진 있음' : '사진 없음';
      else sub = item.url ? '📎 파일/링크 있음' : '링크 없음';
      return `<div class="admin-item neu-card" data-id="${esc(item.id)}">
        <div class="admin-item__main"><strong>${esc(item.title)}</strong><span>${esc(sub)}</span></div>
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
        saveDraft();
        renderList();
        setStatus('삭제됨 — 「사이트에 저장」을 눌러 반영하세요.', 'warn');
      });
    });
  }

  function setImagePreview(url) {
    const preview = $('#image-preview');
    const placeholder = $('#image-preview-empty');
    if (!preview) return;
    if (url) {
      preview.src = url;
      preview.hidden = false;
      if (placeholder) placeholder.hidden = true;
    } else {
      preview.hidden = true;
      preview.removeAttribute('src');
      if (placeholder) placeholder.hidden = false;
    }
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
    setImagePreview(item?.image || '');
    resetUploadZone('file');
    resetUploadZone('image');
    updateFormFields();
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function closeForm() {
    editingId = null;
    $('#admin-form').hidden = true;
  }

  function resetUploadZone(type) {
    const zone = $(`#zone-${type}`);
    if (!zone) return;
    const prog = zone.querySelector('.admin-upload__progress');
    const done = zone.querySelector('.admin-upload__done');
    const bar = zone.querySelector('.admin-upload__bar');
    if (prog) prog.hidden = true;
    if (done) { done.hidden = true; done.textContent = ''; }
    if (bar) bar.style.width = '0%';
    zone.classList.remove('is-dragover', 'is-uploading', 'is-done');
  }

  function setUploadProgress(zone, pct, label) {
    const prog = zone.querySelector('.admin-upload__progress');
    const bar = zone.querySelector('.admin-upload__bar');
    const done = zone.querySelector('.admin-upload__done');
    zone.classList.add('is-uploading');
    if (prog) prog.hidden = false;
    if (bar) bar.style.width = pct + '%';
    if (pct >= 100 && done) {
      done.hidden = false;
      done.textContent = label || '업로드 완료';
      zone.classList.remove('is-uploading');
      zone.classList.add('is-done');
    }
  }

  async function handleUpload(file, type) {
    touchSession();
    if (!file) return;
    const zone = $(`#zone-${type}`);
    if (!zone) return;

    if (type === 'image' && !file.type.startsWith('image/')) {
      alert('이미지 파일만 업로드할 수 있습니다. (JPG, PNG, WEBP 등)');
      return;
    }

    const maxMb = type === 'image' ? 8 : 20;
    if (file.size > maxMb * 1024 * 1024) {
      alert(`파일 크기는 ${maxMb}MB 이하여야 합니다.`);
      return;
    }

    if (!githubReady()) {
      alert('먼저 아래 「GitHub 연결」에서 토큰을 설정해 주세요.');
      $('#github-setup').open = true;
      return;
    }

    try {
      setUploadProgress(zone, 10, '');
      const folder = type === 'image' ? 'images' : 'files';
      const url = await uploadBinaryToGithub(file, folder, pct => setUploadProgress(zone, pct, ''));
      if (type === 'image') {
        $('#f-image').value = url;
        setImagePreview(url);
      } else {
        $('#f-url').value = url;
      }
      setUploadProgress(zone, 100, file.name + ' 업로드 완료');
      setStatus('파일 업로드 완료. 항목 저장 후 「사이트에 저장」을 눌러 주세요.', 'ok');
    } catch (err) {
      resetUploadZone(type);
      alert(err.message);
    }
  }

  function setupDropZone(type, accept) {
    const zone = $(`#zone-${type}`);
    if (!zone) return;
    const input = zone.querySelector('input[type="file"]');
    if (input) input.accept = accept;

    zone.addEventListener('click', e => {
      if (e.target.closest('a')) return;
      input?.click();
    });

    input?.addEventListener('change', e => {
      const file = e.target.files[0];
      if (file) handleUpload(file, type);
      e.target.value = '';
    });

    ['dragenter', 'dragover'].forEach(ev => {
      zone.addEventListener(ev, e => {
        e.preventDefault();
        zone.classList.add('is-dragover');
      });
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('is-dragover'));
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('is-dragover');
      const file = e.dataTransfer.files[0];
      if (file) handleUpload(file, type);
    });
  }

  function saveForm(e) {
    e.preventDefault();
    touchSession();
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
      if (!entry.image && !entry.url && !entry.content) {
        return alert('설치 사진을 업로드하거나 링크/본문을 입력해 주세요.');
      }
    }
    if (activeTab === 'notices') entry.content = $('#f-content').value.trim();
    if (activeTab === 'resources' && !entry.url) {
      return alert('자료 파일을 업로드하거나 링크 URL을 입력해 주세요.');
    }

    if (editingId) {
      const idx = board[activeTab].findIndex(x => x.id === editingId);
      if (idx >= 0) board[activeTab][idx] = { ...board[activeTab][idx], ...entry };
    } else {
      board[activeTab].unshift(entry);
    }
    saveDraft();
    closeForm();
    renderList();
    setStatus('항목이 저장되었습니다. 「사이트에 저장」을 눌러 사이트에 반영하세요.', 'ok');
  }

  async function persistAll() {
    touchSession();
    if (!(await validateSession())) {
      alert('세션이 만료되었습니다. 다시 로그인해 주세요.');
      clearSession();
      showLogin();
      return;
    }
    const json = JSON.stringify(board, null, 2);
    setStatus('저장 중…', '');
    try {
      await saveToGithub(DATA_PATH, json, 'Update support board via admin');
      localStorage.removeItem(DRAFT_KEY);
      setStatus('사이트에 저장되었습니다. 반영까지 1~2분 걸릴 수 있습니다.', 'ok');
    } catch (err) {
      downloadJson(board, 'support-board.json');
      setStatus('GitHub 저장 실패 — JSON을 다운로드했습니다. (' + err.message + ')', 'err');
    }
  }

  async function changePassword(e) {
    e.preventDefault();
    touchSession();
    const cur = $('#pw-current').value;
    const next = $('#pw-new').value;
    const confirm = $('#pw-confirm').value;
    if (!cur || !next) return alert('비밀번호를 입력해 주세요.');
    if (next.length < 8) return alert('새 비밀번호는 8자 이상이어야 합니다.');
    if (next !== confirm) return alert('새 비밀번호가 일치하지 않습니다.');
    const curHash = await sha256(cur);
    if (curHash !== adminConfig.passwordHash) {
      return alert('현재 비밀번호가 올바르지 않습니다.');
    }
    const newHash = await sha256(next);
    adminConfig.passwordHash = newHash;
    const cfgJson = JSON.stringify(adminConfig, null, 2);
    try {
      if (githubReady()) {
        await saveToGithub(CONFIG_PATH, cfgJson, 'Update admin password hash');
        await createSession(newHash);
        setStatus('비밀번호가 변경되었습니다.', 'ok');
      } else {
        downloadJson(adminConfig, 'admin-config.json');
        alert('비밀번호 해시가 변경되었습니다. admin-config.json 을 data/ 폴더에 업로드해 주세요.');
      }
      $('#pw-current').value = $('#pw-new').value = $('#pw-confirm').value = '';
    } catch (err) {
      downloadJson(adminConfig, 'admin-config.json');
      alert('GitHub 저장 실패 — admin-config.json 을 수동으로 업로드해 주세요.');
    }
  }

  function bindEvents() {
    $('#login-form').addEventListener('submit', async e => {
      e.preventDefault();
      updateLockoutUI();
      if (isLockedOut()) return;

      const pass = $('#login-pass').value;
      const hash = await sha256(pass);
      if (hash !== adminConfig.passwordHash) {
        recordFailedLogin();
        updateLockoutUI();
        const left = adminConfig.maxAttempts - (getLockout().attempts || 0);
        alert(left > 0
          ? `비밀번호가 올바르지 않습니다. (${left}회 남음)`
          : '로그인이 잠시 차단되었습니다.');
        return;
      }
      clearLockout();
      await createSession(hash);
      $('#login-pass').value = '';
      try {
        await loadBoard();
        showApp();
      } catch (err) {
        clearSession();
        alert(err.message);
      }
    });

    setInterval(updateLockoutUI, 1000);

    $$('.admin-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        touchSession();
        activeTab = tab.dataset.tab;
        $$('.admin-tab').forEach(t => t.classList.toggle('is-active', t === tab));
        closeForm();
        updateFormFields();
        renderList();
      });
    });

    $('#btn-new').addEventListener('click', () => { touchSession(); openForm(null); });
    $('#btn-cancel').addEventListener('click', closeForm);
    $('#item-form').addEventListener('submit', saveForm);
    $('#btn-save-github').addEventListener('click', persistAll);
    $('#btn-export').addEventListener('click', () => downloadJson(board, 'support-board.json'));

    $('#btn-import').addEventListener('click', () => $('#import-file').click());
    $('#import-file').addEventListener('change', e => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          board = JSON.parse(reader.result);
          saveDraft();
          renderList();
          setStatus('JSON을 불러왔습니다. 「사이트에 저장」으로 반영하세요.', 'ok');
        } catch { alert('JSON 형식이 올바르지 않습니다.'); }
      };
      reader.readAsText(file);
      e.target.value = '';
    });

    $('#github-form').addEventListener('submit', e => {
      e.preventDefault();
      touchSession();
      const token = $('#gh-token').value.trim();
      setGithubCfg({
        owner: $('#gh-owner').value.trim(),
        repo: $('#gh-repo').value.trim(),
        branch: $('#gh-branch').value.trim() || 'main',
        token,
        pagesUrl: $('#gh-pages').value.trim()
      });
      if (token) $('#gh-token').value = '';
      updateGithubBanner();
      setStatus('GitHub 설정이 저장되었습니다. (토큰은 이 브라우저에만 보관)', 'ok');
    });

    const cfg = getGithubCfg();
    if (cfg.owner) $('#gh-owner').value = cfg.owner;
    if (cfg.repo) $('#gh-repo').value = cfg.repo;
    if (cfg.branch) $('#gh-branch').value = cfg.branch;
    if (cfg.pagesUrl) $('#gh-pages').value = cfg.pagesUrl;

    $('#f-image').addEventListener('input', () => setImagePreview($('#f-image').value.trim()));
    $('#btn-clear-image').addEventListener('click', () => {
      $('#f-image').value = '';
      setImagePreview('');
      resetUploadZone('image');
    });

    $('#btn-logout').addEventListener('click', () => {
      clearSession();
      showLogin();
    });

    $('#pw-form').addEventListener('submit', changePassword);

    setupDropZone('file', '.pdf,.doc,.docx,.zip,.hwp,.ppt,.pptx,.xls,.xlsx,.txt');
    setupDropZone('image', 'image/*');

    document.addEventListener('click', touchSession);
    document.addEventListener('keydown', touchSession);
  }

  async function init() {
    bindEvents();
    try {
      await loadAdminConfig();
    } catch (err) {
      alert(err.message);
      return;
    }

    if (await validateSession()) {
      try {
        await loadBoard();
        showApp();
        return;
      } catch {
        clearSession();
      }
    }
    showLogin();
  }

  init();
})();
