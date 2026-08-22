/* 아성보이스 내부 일정 보드 — 주흥돈/공찬희 공동 편집 */
(function () {
  'use strict';

  const SESSION_KEY = 'asung_ops_session';
  const LOCKOUT_KEY = 'asung_ops_lockout';
  const GITHUB_KEY = 'asung_admin_github';
  const DRAFT_KEY = 'asung_ops_draft';
  const DATA_PATH = 'data/ops-board.json';
  const CONFIG_PATH = 'data/ops-config.json';
  const SESSION_SALT = 'asung-voice-ops-v1';
  const scriptBase = document.currentScript.src.replace(/\/js\/ops-board\.js.*$/, '/');

  const PROJECTS = {
    watchdog: '워치독',
    ansimi: '마이안심이',
    switch: '일괄소등',
    bell: '비상벨',
    corp: '전사'
  };
  const LANES = { product: '제품', sales: '영업', invest: '투자' };
  const STATUSES = {
    done: '완료',
    doing: '진행',
    review: '검토',
    planned: '예정',
    ongoing: '상시'
  };
  const MONTHS = [
    '2026-08', '2026-09', '2026-10', '2026-11', '2026-12',
    '2027-01', '2027-02', '2027-03', '2027-04', '2027-05', '2027-06'
  ];
  const NOW_MONTH = '2026-08';

  let config = { sessionMinutes: 180, maxAttempts: 5, lockoutMinutes: 15, users: [] };
  let board = { tasks: [], memo: '', activity: [], updatedAt: '', updatedBy: '' };
  let currentUser = null;
  let page = 'home';
  let filterProject = '';
  let filterLane = '';
  let dirty = false;
  let idleTimer = null;
  let selectedUserId = '';

  const $ = sel => document.querySelector(sel);
  const $$ = sel => [...document.querySelectorAll(sel)];

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s ?? '';
    return d.innerHTML;
  }

  function uid(prefix) {
    return prefix + '-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
  }

  async function sha256(text) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  function nowIso() {
    const d = new Date();
    const off = 9 * 60;
    const kst = new Date(d.getTime() + (off - d.getTimezoneOffset()) * 60000);
    return kst.toISOString().replace('Z', '+09:00');
  }

  function fmtWhen(iso) {
    if (!iso) return '';
    return iso.replace('T', ' ').slice(0, 16);
  }

  async function loadJson(path) {
    const url = new URL(path, scriptBase).href + '?t=' + Date.now();
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error(path + ' 를 불러올 수 없습니다.');
    return res.json();
  }

  function userById(id) {
    return (config.users || []).find(u => u.id === id);
  }

  function displayName(id) {
    if (id === 'system') return '시스템';
    const u = userById(id);
    return u ? u.name : id;
  }

  function getLockout() {
    try { return JSON.parse(localStorage.getItem(LOCKOUT_KEY) || '{}'); }
    catch { return {}; }
  }
  function setLockout(data) { localStorage.setItem(LOCKOUT_KEY, JSON.stringify(data)); }
  function isLockedOut() {
    const lo = getLockout();
    if (!lo.lockedUntil) return false;
    if (Date.now() < lo.lockedUntil) return true;
    setLockout({ attempts: 0 });
    return false;
  }
  function recordFailedLogin() {
    const lo = getLockout();
    const attempts = (lo.attempts || 0) + 1;
    if (attempts >= config.maxAttempts) {
      setLockout({ attempts, lockedUntil: Date.now() + config.lockoutMinutes * 60 * 1000 });
    } else setLockout({ attempts });
  }

  async function createSession(user, hash) {
    const token = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(24))));
    const expires = Date.now() + config.sessionMinutes * 60 * 1000;
    const sig = await sha256(token + expires + user.id + hash + SESSION_SALT);
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({ token, expires, sig, hash, userId: user.id }));
    currentUser = user;
    resetIdle();
  }

  async function validateSession() {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return false;
    let sess;
    try { sess = JSON.parse(raw); } catch { return false; }
    if (!sess.token || !sess.expires || !sess.sig || !sess.hash || !sess.userId) return false;
    if (Date.now() > sess.expires) return false;
    const expected = await sha256(sess.token + sess.expires + sess.userId + sess.hash + SESSION_SALT);
    if (expected !== sess.sig) return false;
    const user = userById(sess.userId);
    if (!user || user.passwordHash !== sess.hash) return false;
    currentUser = user;
    return true;
  }

  function clearSession() {
    sessionStorage.removeItem(SESSION_KEY);
    currentUser = null;
    if (idleTimer) clearTimeout(idleTimer);
  }

  function resetIdle() {
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      alert('보안을 위해 세션이 만료되었습니다. 다시 로그인해 주세요.');
      clearSession();
      showLogin();
    }, config.sessionMinutes * 60 * 1000);
  }

  function getGithubCfg() {
    try { return JSON.parse(localStorage.getItem(GITHUB_KEY) || '{}'); }
    catch { return {}; }
  }
  function setGithubCfg(cfg) { localStorage.setItem(GITHUB_KEY, JSON.stringify(cfg)); }
  function githubReady() {
    const c = getGithubCfg();
    return !!(c.token && c.owner && c.repo);
  }

  async function saveToGithub(path, jsonText, message) {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      throw new Error('설정에서 GitHub 저장소와 토큰을 먼저 연결해 주세요.');
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
      message: message || 'Update ops board',
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

  function saveDraft() {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(board));
    dirty = true;
    setStatus('이 브라우저에만 저장됨 · 공유 저장을 누르면 두 분에게 반영됩니다.', '');
  }

  function restoreDraft() {
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return;
    try {
      const draft = JSON.parse(raw);
      if (draft && Array.isArray(draft.tasks)) {
        board = { ...board, ...draft };
        dirty = true;
      }
    } catch { /* ignore */ }
  }

  function logActivity(text) {
    board.activity = board.activity || [];
    board.activity.unshift({ at: nowIso(), by: currentUser.id, text });
    board.activity = board.activity.slice(0, 80);
  }

  function setStatus(msg, kind) {
    const el = $('#save-status');
    if (!el) return;
    el.textContent = msg || '';
    el.className = 'ops-status' + (kind ? ' is-' + kind : '');
  }

  function filteredTasks() {
    return (board.tasks || []).filter(t => {
      if (filterProject && t.project !== filterProject) return false;
      if (filterLane && t.lane !== filterLane) return false;
      return true;
    });
  }

  function monthIndex(ym) {
    const i = MONTHS.indexOf(ym);
    return i < 0 ? 0 : i;
  }

  function options(map, selected) {
    return Object.entries(map).map(([k, v]) =>
      `<option value="${k}"${k === selected ? ' selected' : ''}>${v}</option>`
    ).join('');
  }

  function renderLoginUsers() {
    const list = $('#user-list');
    if (!list) return;
    const users = config.users || [];
    if (!users.length) {
      list.innerHTML = '<p class="ops-err">로그인 명단을 불러오지 못했습니다. 페이지를 새로고침해 주세요.</p>';
      return;
    }
    if (!selectedUserId) selectedUserId = users[0].id;
    list.innerHTML = users.map(u => `
      <label class="ops-user${selectedUserId === u.id ? ' is-on' : ''}">
        <input type="radio" name="who" value="${esc(u.id)}"${selectedUserId === u.id ? ' checked' : ''} required>
        <span class="ops-user__av">${esc((u.name || '?').slice(0, 1))}</span>
        <span>
          <span class="ops-user__name">${esc(u.name)}</span><br>
          <span class="ops-user__role">${esc(u.role || '')}</span>
        </span>
      </label>
    `).join('');
    list.querySelectorAll('input[name="who"]').forEach(el => {
      el.addEventListener('change', () => {
        selectedUserId = el.value;
        $('#login-pass').focus();
      });
    });
  }

  function pageTitle() {
    if (page === 'home') return '홈';
    if (page === 'timeline') return '타임라인';
    if (page === 'activity') return '활동 기록';
    if (page === 'settings') return '설정';
    if (filterProject) return PROJECTS[filterProject] || '표';
    if (filterLane) return LANES[filterLane] || '표';
    return '전체 표';
  }

  function renderHome() {
    const tasks = board.tasks || [];
    const doing = tasks.filter(t => t.status === 'doing').length;
    const review = tasks.filter(t => t.status === 'review').length;
    const focus = tasks.filter(t => t.status === 'doing' || t.status === 'review');
    return `
      <div class="ops-note">비명모델은 워치독 업데이트 · 마이안심이 · 일괄소등이 같은 기간에 겹칩니다. 셀을 눌러 고치고, 공유 저장을 누르면 두 분 화면에 같이 반영됩니다.</div>
      <div class="ops-kpis">
        <div class="ops-kpi"><b>${doing}</b><span>진행 중</span></div>
        <div class="ops-kpi"><b>${review}</b><span>검토</span></div>
        <div class="ops-kpi"><b>${tasks.length}</b><span>전체 항목</span></div>
        <div class="ops-kpi"><b>${esc(displayName(board.updatedBy) || '—')}</b><span>마지막 공유 · ${esc(fmtWhen(board.updatedAt) || '아직 없음')}</span></div>
      </div>
      <h3 class="ops-h3">지금 손대는 일</h3>
      ${renderTable(focus)}
      <h3 class="ops-h3">공유 메모</h3>
      <textarea class="ops-memo" id="memo">${esc(board.memo || '')}</textarea>
    `;
  }

  function renderTable(list) {
    const rows = list.map(t => `
      <tr data-id="${t.id}">
        <td><select data-k="project">${options(PROJECTS, t.project)}</select></td>
        <td><select data-k="lane">${options(LANES, t.lane)}</select></td>
        <td><input data-k="name" value="${esc(t.name)}"></td>
        <td><select data-k="status">${options(STATUSES, t.status)}</select></td>
        <td><input type="month" data-k="start" value="${esc(t.start || '')}"></td>
        <td><input type="month" data-k="end" value="${esc(t.end || '')}"></td>
        <td><input data-k="owner" value="${esc(t.owner || '')}"></td>
        <td><input data-k="note" value="${esc(t.note || '')}"></td>
        <td><button type="button" class="ops-del" data-del="${t.id}">삭제</button></td>
      </tr>
    `).join('');
    return `
      <div class="ops-table-wrap">
        <table class="ops-table">
          <thead><tr>
            <th>제품</th><th>구분</th><th>작업</th><th>상태</th>
            <th>시작</th><th>끝</th><th>담당</th><th>비고</th><th></th>
          </tr></thead>
          <tbody>${rows || '<tr><td colspan="9">항목이 없습니다. + 행 추가로 넣으세요.</td></tr>'}</tbody>
        </table>
      </div>
    `;
  }

  function barColor(status) {
    return {
      doing: '#2383e2',
      review: '#d97706',
      planned: '#d3d1cb',
      ongoing: '#3aaf7a',
      done: '#c5c4be'
    }[status] || '#d3d1cb';
  }

  function renderTimeline() {
    const list = filteredTasks();
    const nowIdx = monthIndex(NOW_MONTH);
    const head = MONTHS.map((m, i) =>
      `<div class="ops-gantt__h${m === NOW_MONTH ? ' is-now' : ''}">${m === NOW_MONTH ? '오늘' : m.slice(2)}</div>`
    ).join('');
    const body = list.map(t => {
      const s = monthIndex(t.start);
      const e = monthIndex(t.end);
      const span = Math.max(1, e - s + 1);
      return `
        <div class="ops-gantt__name" title="${esc(t.name)}">${esc(t.name)}</div>
        <div class="ops-gantt__track">
          <div class="ops-gantt__now" style="left:calc(${nowIdx} * 100% / 11)"></div>
          <div class="ops-gantt__bar" style="grid-column:${s + 1} / span ${span};background:${barColor(t.status)}"></div>
        </div>
      `;
    }).join('');
    return `<div class="ops-gantt"><div class="ops-gantt__grid"><div></div>${head}${body}</div></div>
      <p class="ops-hint" style="margin-top:10px">막대 기간은 표에서 시작·끝을 바꾸면 같이 바뀝니다. 출처: 2026.08.22 현황 초안.</p>`;
  }

  function renderActivity() {
    const items = (board.activity || []).map(a =>
      `<div class="ops-act"><time>${esc(fmtWhen(a.at))} · ${esc(displayName(a.by))}</time>${esc(a.text)}</div>`
    ).join('');
    return items || '<p class="ops-hint">아직 활동 기록이 없습니다.</p>';
  }

  function renderSettings() {
    const cfg = getGithubCfg();
    const users = (config.users || []).map(u =>
      `<option value="${u.id}"${u.id === currentUser.id ? ' selected' : ''}>${esc(u.name)} (${esc(u.role)})</option>`
    ).join('');
    return `
      <p class="ops-hint">두 분이 같은 보드를 보려면 GitHub 연결 후 「공유 저장」이 필요합니다. 게시판 관리자에서 이미 연결했다면 이 브라우저에서 그대로 됩니다.</p>
      <div class="ops-form">
        <h3 class="ops-h3">내 이름</h3>
        <label>표시 이름</label>
        <input id="set-name" value="${esc(currentUser.name)}">
        <div class="ops-row" style="margin-top:10px"><button class="ops-btn ops-btn--ghost" id="btn-name" type="button">이름 저장</button></div>

        <h3 class="ops-h3">비밀번호 변경</h3>
        <label>현재 비밀번호</label>
        <input id="pw-cur" type="password" autocomplete="current-password">
        <label>새 비밀번호 (8자 이상)</label>
        <input id="pw-new" type="password" autocomplete="new-password">
        <label>새 비밀번호 확인</label>
        <input id="pw-ok" type="password" autocomplete="new-password">
        <div class="ops-row" style="margin-top:10px"><button class="ops-btn ops-btn--ghost" id="btn-pw" type="button">비밀번호 변경</button></div>

        <h3 class="ops-h3">GitHub 연결</h3>
        <label>사용자</label><input id="gh-owner" value="${esc(cfg.owner || 'gourry7')}">
        <label>저장소</label><input id="gh-repo" value="${esc(cfg.repo || 'asungvoice')}">
        <label>브랜치</label><input id="gh-branch" value="${esc(cfg.branch || 'main')}">
        <label>Personal Access Token</label>
        <input id="gh-token" type="password" autocomplete="off" placeholder="${cfg.token ? '저장됨 · 바꿀 때만 입력' : 'ghp_...'}">
        <div class="ops-row" style="margin-top:10px"><button class="ops-btn ops-btn--ghost" id="btn-gh" type="button">연결 저장</button></div>
        <p class="ops-hint">${githubReady() ? 'GitHub 연결됨. 공유 저장을 쓰면 사이트에 반영됩니다.' : '아직 연결되지 않았습니다.'}</p>
      </div>
      <p class="ops-hint">이 보드는 검색·메뉴에 노출되지 않습니다. 주소는 두 분만 공유하세요. GitHub 저장소가 공개면 저장된 JSON도 공개될 수 있습니다.</p>
      <select id="dummy-user" hidden>${users}</select>
    `;
  }

  function render() {
    $('#page-title').textContent = pageTitle();
    $('#me-name').textContent = currentUser.name;
    $('#me-role').textContent = currentUser.role;
    $('#btn-add').hidden = page === 'settings' || page === 'activity';
    let html = '';
    if (page === 'home') html = renderHome();
    else if (page === 'timeline') html = renderTimeline();
    else if (page === 'activity') html = renderActivity();
    else if (page === 'settings') html = renderSettings();
    else html = renderTable(filteredTasks());
    $('#view').innerHTML = html;
    bindView();
    $$('.ops-nav').forEach(btn => {
      const on = btn.dataset.page === page
        && (btn.dataset.project || '') === filterProject
        && (btn.dataset.lane || '') === filterLane;
      btn.classList.toggle('is-on', on);
    });
  }

  function patchTask(id, key, value) {
    const t = board.tasks.find(x => x.id === id);
    if (!t || t[key] === value) return;
    t[key] = value;
    t.updatedBy = currentUser.id;
    t.updatedAt = nowIso();
    logActivity(`${t.name || '항목'} · ${key} 수정`);
    saveDraft();
    if (key === 'status' || key === 'project' || key === 'lane') render();
  }

  function bindView() {
    $$('#view tr[data-id]').forEach(tr => {
      const id = tr.dataset.id;
      tr.querySelectorAll('[data-k]').forEach(el => {
        const ev = el.tagName === 'SELECT' || el.type === 'month' ? 'change' : 'change';
        el.addEventListener(ev, () => patchTask(id, el.dataset.k, el.value));
        if (el.tagName === 'INPUT' && el.type !== 'month') {
          el.addEventListener('blur', () => patchTask(id, el.dataset.k, el.value));
        }
      });
    });
    $$('#view [data-del]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.del;
        const t = board.tasks.find(x => x.id === id);
        if (!t || !confirm('이 행을 삭제할까요?')) return;
        board.tasks = board.tasks.filter(x => x.id !== id);
        logActivity(`${t.name} 삭제`);
        saveDraft();
        render();
      });
    });
    const memo = $('#memo');
    if (memo) {
      memo.addEventListener('blur', () => {
        if (board.memo === memo.value) return;
        board.memo = memo.value;
        logActivity('공유 메모 수정');
        saveDraft();
      });
    }
    const btnName = $('#btn-name');
    if (btnName) btnName.addEventListener('click', saveMyName);
    const btnPw = $('#btn-pw');
    if (btnPw) btnPw.addEventListener('click', changePassword);
    const btnGh = $('#btn-gh');
    if (btnGh) btnGh.addEventListener('click', saveGithub);
  }

  async function saveMyName() {
    const name = ($('#set-name').value || '').trim();
    if (!name) return alert('이름을 입력해 주세요.');
    const user = userById(currentUser.id);
    user.name = name;
    currentUser = user;
    logActivity('표시 이름을 ' + name + ' 으로 변경');
    try {
      if (githubReady()) {
        await saveToGithub(CONFIG_PATH, JSON.stringify(config, null, 2), 'Update ops display name');
      }
      saveDraft();
      setStatus('이름이 저장되었습니다.', 'ok');
      render();
    } catch (err) {
      alert(err.message);
    }
  }

  async function changePassword() {
    const cur = $('#pw-cur').value;
    const next = $('#pw-new').value;
    const ok = $('#pw-ok').value;
    if (!cur || !next) return alert('비밀번호를 입력해 주세요.');
    if (next.length < 8) return alert('새 비밀번호는 8자 이상이어야 합니다.');
    if (next !== ok) return alert('새 비밀번호가 일치하지 않습니다.');
    const curHash = await sha256(cur);
    if (curHash !== currentUser.passwordHash) return alert('현재 비밀번호가 올바르지 않습니다.');
    const newHash = await sha256(next);
    const user = userById(currentUser.id);
    user.passwordHash = newHash;
    currentUser = user;
    try {
      if (githubReady()) {
        await saveToGithub(CONFIG_PATH, JSON.stringify(config, null, 2), 'Update ops password hash');
      }
      await createSession(user, newHash);
      logActivity('비밀번호 변경');
      saveDraft();
      $('#pw-cur').value = $('#pw-new').value = $('#pw-ok').value = '';
      setStatus('비밀번호가 변경되었습니다. 공유 저장도 눌러 주세요.', 'ok');
    } catch (err) {
      alert(err.message);
    }
  }

  function saveGithub() {
    const prev = getGithubCfg();
    const token = $('#gh-token').value.trim() || prev.token;
    setGithubCfg({
      owner: $('#gh-owner').value.trim(),
      repo: $('#gh-repo').value.trim(),
      branch: $('#gh-branch').value.trim() || 'main',
      token
    });
    if ($('#gh-token').value) $('#gh-token').value = '';
    setStatus('GitHub 설정이 이 브라우저에 저장되었습니다.', 'ok');
    render();
  }

  function addRow() {
    const task = {
      id: uid('row'),
      name: '새 작업',
      project: filterProject || 'watchdog',
      lane: filterLane || 'product',
      status: 'planned',
      start: NOW_MONTH,
      end: NOW_MONTH,
      owner: currentUser.name,
      note: ''
    };
    board.tasks.unshift(task);
    logActivity('새 작업 추가');
    saveDraft();
    if (page === 'home') { page = 'table'; filterProject = ''; filterLane = ''; }
    render();
  }

  async function persist() {
    if (!(await validateSession())) {
      alert('세션이 만료되었습니다.');
      clearSession();
      showLogin();
      return;
    }
    board.updatedAt = nowIso();
    board.updatedBy = currentUser.id;
    const json = JSON.stringify(board, null, 2);
    setStatus('저장 중…', '');
    try {
      await saveToGithub(DATA_PATH, json, 'Update ops board (' + currentUser.name + ')');
      localStorage.removeItem(DRAFT_KEY);
      dirty = false;
      setStatus('사이트에 공유되었습니다. 반영까지 1~2분 걸릴 수 있습니다.', 'ok');
    } catch (err) {
      const blob = new Blob([json], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'ops-board.json';
      a.click();
      setStatus('GitHub 저장 실패 — JSON을 받았습니다. ' + err.message, 'err');
    }
  }

  function showLogin() {
    $('#app').hidden = true;
    $('#login').hidden = false;
    renderLoginUsers();
  }

  async function showApp() {
    $('#login').hidden = true;
    $('#app').hidden = false;
    restoreDraft();
    if (dirty) setStatus('이 브라우저에 임시 수정이 있습니다. 공유 저장을 눌러 주세요.', '');
    else setStatus(board.updatedBy ? `마지막 공유 ${displayName(board.updatedBy)} · ${fmtWhen(board.updatedAt)}` : '', '');
    render();
  }

  function bindChrome() {
    $$('.ops-nav').forEach(btn => {
      btn.addEventListener('click', () => {
        resetIdle();
        page = btn.dataset.page;
        filterProject = btn.dataset.project || '';
        filterLane = btn.dataset.lane || '';
        render();
      });
    });
    $('#btn-add').addEventListener('click', () => { resetIdle(); addRow(); });
    $('#btn-save').addEventListener('click', persist);
    $('#btn-logout').addEventListener('click', () => { clearSession(); showLogin(); });
    $('#login-form').addEventListener('submit', onLogin);
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (!$('#app').hidden) persist();
      }
    });
    document.addEventListener('click', resetIdle);
  }

  function showLoginError(msg) {
    const el = $('#login-error');
    if (el) el.textContent = msg;
    else alert(msg);
  }

  async function onLogin(e) {
    e.preventDefault();
    const btn = $('#login-submit');
    const picked = (document.querySelector('input[name="who"]:checked') || {}).value || selectedUserId;
    selectedUserId = picked;
    showLoginError('');
    if (btn) {
      btn.disabled = true;
      btn.textContent = '확인 중…';
    }
    try {
      if (isLockedOut()) {
        showLoginError('잠시 후 다시 시도해 주세요.');
        return;
      }
      if (!selectedUserId) {
        showLoginError('본인 이름을 먼저 선택해 주세요.');
        return;
      }
      const user = userById(selectedUserId);
      if (!user) {
        showLoginError('로그인 명단이 아직 준비되지 않았습니다. 새로고침 후 다시 시도해 주세요.');
        return;
      }
      const hash = await sha256($('#login-pass').value || '');
      if (hash !== user.passwordHash) {
        recordFailedLogin();
        const left = config.maxAttempts - (getLockout().attempts || 0);
        showLoginError(left > 0
          ? '비밀번호가 올바르지 않습니다. (' + left + '회 남음)'
          : '로그인이 잠시 차단되었습니다.');
        return;
      }
      setLockout({ attempts: 0 });
      await createSession(user, hash);
      $('#login-pass').value = '';
      board = await loadJson(DATA_PATH);
      await showApp();
    } catch (err) {
      clearSession();
      showLoginError(err && err.message ? err.message : '로그인 중 오류가 났습니다.');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = '들어가기';
      }
    }
  }

  async function init() {
    try {
      bindChrome();
      config = { ...config, ...(await loadJson(CONFIG_PATH)) };
      renderLoginUsers();
      if (await validateSession()) {
        try {
          board = await loadJson(DATA_PATH);
          await showApp();
          return;
        } catch {
          clearSession();
        }
      }
      showLogin();
    } catch (err) {
      showLoginError(err && err.message ? err.message : '페이지를 불러오지 못했습니다. 새로고침해 주세요.');
    }
  }

  init();
})();
