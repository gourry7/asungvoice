/* 아성보이스 내부 일정 보드 — 주흥돈/공찬희 공동 편집 */
(function () {
  'use strict';

  const SESSION_KEY = 'asung_ops_session';
  const LOCKOUT_KEY = 'asung_ops_lockout';
  const GITHUB_KEY = 'asung_admin_github';
  const GITHUB_DEFAULTS = {
    owner: 'gourry7',
    repo: 'asungvoice',
    branch: 'main',
    pagesUrl: 'https://gourry7.github.io/asungvoice'
  };
  const DRAFT_KEY = 'asung_ops_draft';
  const DATA_PATH = 'data/ops-board.json';
  const CONFIG_PATH = 'data/ops-config.json';
  const SESSION_SALT = 'asung-voice-ops-v1';
  const SESSION_DAYS = 30;
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
  let page = 'timeline';
  let filterProject = '';
  let filterLane = '';
  let dirty = false;
  let idleTimer = null;
  let selectedUserId = '';
  let editorId = '';
  let timelineFilter = '';
  let pendingShare = false;
  let ganttDrag = null;
  let rowDrag = null;

  const $ = sel => document.querySelector(sel);
  const $$ = sel => [...document.querySelectorAll(sel)];

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s == null ? '' : s;
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
    const expires = Date.now() + SESSION_DAYS * 24 * 60 * 60 * 1000;
    const sig = await sha256(token + expires + user.id + hash + SESSION_SALT);
    const sess = JSON.stringify({ token, expires, sig, hash, userId: user.id });
    localStorage.setItem(SESSION_KEY, sess);
    sessionStorage.removeItem(SESSION_KEY);
    currentUser = user;
  }

  async function validateSession() {
    const raw = localStorage.getItem(SESSION_KEY) || sessionStorage.getItem(SESSION_KEY);
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
    await createSession(user, sess.hash);
    return true;
  }

  function clearSession() {
    localStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(SESSION_KEY);
    currentUser = null;
    if (idleTimer) clearTimeout(idleTimer);
  }

  function resetIdle() {
    if (idleTimer) {
      clearTimeout(idleTimer);
      idleTimer = null;
    }
  }

  function getGithubCfg() {
    let stored = {};
    try { stored = JSON.parse(localStorage.getItem(GITHUB_KEY) || '{}'); }
    catch { stored = {}; }
    return {
      ...GITHUB_DEFAULTS,
      ...stored,
      owner: stored.owner || GITHUB_DEFAULTS.owner,
      repo: stored.repo || GITHUB_DEFAULTS.repo,
      branch: stored.branch || GITHUB_DEFAULTS.branch,
      pagesUrl: stored.pagesUrl || GITHUB_DEFAULTS.pagesUrl
    };
  }
  function setGithubCfg(cfg) { localStorage.setItem(GITHUB_KEY, JSON.stringify(cfg)); }
  function githubReady() {
    const c = getGithubCfg();
    return !!(c.token && c.owner && c.repo);
  }

  function githubHeaders(token) {
    return {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json'
    };
  }

  async function saveToGithub(path, jsonText, message) {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      const err = new Error('설정에서 GitHub 저장소와 토큰을 먼저 연결해 주세요.');
      err.code = 'no-github';
      throw err;
    }
    const api = `https://api.github.com/repos/${cfg.owner}/${cfg.repo}/contents/${path}`;
    const headers = githubHeaders(cfg.token);
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

  function clampMonthIndex(i) {
    return Math.max(0, Math.min(MONTHS.length - 1, i));
  }

  function barPositionStyle(startIdx, endIdx, status) {
    const n = MONTHS.length;
    const s = clampMonthIndex(startIdx);
    const e = Math.max(s, clampMonthIndex(endIdx));
    const span = e - s + 1;
    return 'left:calc(' + s + ' * 100% / ' + n + ' + 2px);width:calc(' + span + ' * 100% / ' + n + ' - 4px);background:' + barColor(status);
  }

  function monthFromPointer(track, clientX) {
    const r = track.getBoundingClientRect();
    if (!r.width) return 0;
    const x = Math.min(Math.max(clientX - r.left, 0), r.width - 0.001);
    return clampMonthIndex(Math.floor(x / r.width * MONTHS.length));
  }

  function renderKeepScroll() {
    const y = window.scrollY;
    render();
    window.scrollTo(0, y);
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
        <span class="ops-user__name">${esc(u.name)}</span>
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
    if (filterProject) return PROJECTS[filterProject] || '일정';
    if (filterLane) return LANES[filterLane] || '일정';
    return '전체 일정';
  }

  function monthLabel(ym) {
    if (!ym) return '';
    const p = ym.split('-');
    return (p[1] || ym).replace(/^0/, '') + '월';
  }

  function taskRange(t) {
    if (!t.start && !t.end) return '';
    if (t.start === t.end) return monthLabel(t.start);
    return monthLabel(t.start) + ' – ' + monthLabel(t.end);
  }

  function renderQuickAdd() {
    return `
      <form id="quick-add" class="ops-add">
        <div><label>할 일</label><input id="qa-name" placeholder="예: 금형 시사출" required></div>
        <div><label>프로젝트</label><select id="qa-project">${options(PROJECTS, filterProject || 'watchdog')}</select></div>
        <div><label>구분</label><select id="qa-lane">${options(LANES, filterLane || 'product')}</select></div>
        <div><label>상태</label><select id="qa-status">${options(STATUSES, 'planned')}</select></div>
        <div><label>시작</label><input type="month" id="qa-start" value="${NOW_MONTH}"></div>
        <div><label>끝</label><input type="month" id="qa-end" value="${NOW_MONTH}"></div>
        <button type="submit" class="ops-btn ops-btn--blue ops-btn--sm">일정 추가</button>
      </form>
    `;
  }

  function renderEditor() {
    const t = (board.tasks || []).find(x => x.id === editorId);
    if (!t) return '';
    return `
      <div class="ops-editor" data-id="${t.id}">
        <div class="ops-editor__grid">
          <div><label>할 일</label><input data-k="name" value="${esc(t.name)}"></div>
          <div><label>프로젝트</label><select data-k="project">${options(PROJECTS, t.project)}</select></div>
          <div><label>구분</label><select data-k="lane">${options(LANES, t.lane)}</select></div>
          <div><label>상태</label><select data-k="status">${options(STATUSES, t.status)}</select></div>
          <div><label>시작</label><input type="month" data-k="start" value="${esc(t.start || '')}"></div>
          <div><label>끝</label><input type="month" data-k="end" value="${esc(t.end || '')}"></div>
          <div><label>담당</label><input data-k="owner" value="${esc(t.owner || '')}"></div>
          <textarea data-k="note" placeholder="메모">${esc(t.note || '')}</textarea>
        </div>
        <div class="ops-row" style="margin-top:12px">
          <button type="button" class="ops-btn ops-btn--ghost ops-btn--sm" data-close-editor>닫기</button>
          <button type="button" class="ops-btn ops-btn--ghost ops-btn--sm ops-del" data-del="${t.id}">삭제</button>
        </div>
      </div>
    `;
  }

  function renderChips(current) {
    const items = [
      ['', '전체'],
      ['watchdog', '워치독'],
      ['ansimi', '마이안심이'],
      ['switch', '일괄소등'],
      ['bell', '비상벨'],
      ['sales', '영업'],
      ['invest', '투자']
    ];
    return `<div class="ops-chips">${items.map(([id, label]) =>
      `<button type="button" class="ops-chip${current === id ? ' is-on' : ''}" data-chip="${id}">${label}</button>`
    ).join('')}</div>`;
  }

  function tasksForChip(chip) {
    const all = board.tasks || [];
    if (!chip) return all;
    if (chip === 'sales' || chip === 'invest') return all.filter(t => t.lane === chip);
    return all.filter(t => t.project === chip);
  }

  function openGithubSettings(msg) {
    page = 'settings';
    filterProject = '';
    filterLane = '';
    render();
    setStatus(msg || '게시판 관리자와 같은 기존 토큰을 넣고 「연결 저장」을 누르세요.', 'err');
    const token = $('#gh-token');
    if (token) {
      token.scrollIntoView({ behavior: 'smooth', block: 'center' });
      token.focus();
    }
  }

  function renderHome() {
    const tasks = board.tasks || [];
    const doing = tasks.filter(t => t.status === 'doing').length;
    const review = tasks.filter(t => t.status === 'review').length;
    const focus = tasks.filter(t => t.status === 'doing' || t.status === 'review');
    return `
      ${renderQuickAdd()}
      ${renderEditor()}
      <div class="ops-kpis">
        <div class="ops-kpi"><b>${doing}</b><span>진행 중</span></div>
        <div class="ops-kpi"><b>${review}</b><span>검토</span></div>
        <div class="ops-kpi"><b>${tasks.length}</b><span>전체 항목</span></div>
        <div class="ops-kpi"><b>${esc(displayName(board.updatedBy) || '—')}</b><span>마지막 공유 · ${esc(fmtWhen(board.updatedAt) || '아직 없음')}</span></div>
      </div>
      <h3 class="ops-h3">지금 손대는 일</h3>
      ${renderCards(focus)}
      <h3 class="ops-h3">공유 메모</h3>
      <textarea class="ops-memo" id="memo">${esc(board.memo || '')}</textarea>
    `;
  }

  function renderCards(list) {
    if (!list.length) return '<p class="ops-hint">일정이 없습니다. 위에서 할 일과 기간을 넣고 「일정 추가」를 누르세요.</p>';
    return `<div class="ops-cards">${list.map(t => `
      <button type="button" class="ops-card" data-edit="${t.id}">
        <div class="ops-card__top">
          <strong>${esc(t.name)}</strong>
          <span class="ops-pill ops-pill--${esc(t.status)}">${esc(STATUSES[t.status] || t.status)}</span>
        </div>
        <div class="ops-card__meta">${esc(PROJECTS[t.project] || '')} · ${esc(LANES[t.lane] || '')} · ${esc(taskRange(t))} · ${esc(t.owner || '')}</div>
      </button>
    `).join('')}</div>`;
  }

  function renderGanttBlock(title, colorClass, list, group) {
    if (!list.length) {
      return `<section class="ops-block"><div class="ops-block__head"><span class="${colorClass}"></span>${esc(title)} <span style="font-weight:500;color:var(--ops-muted);font-size:.8rem">일정 없음</span></div></section>`;
    }
    const nowIdx = monthIndex(NOW_MONTH);
    const head = MONTHS.map(m =>
      `<div class="ops-gantt__h${m === NOW_MONTH ? ' is-now' : ''}">${m === NOW_MONTH ? '오늘' : monthLabel(m)}</div>`
    ).join('');
    const body = list.map(t => {
      const s = monthIndex(t.start);
      const e = monthIndex(t.end);
      return `
        <div class="ops-gantt__row" data-row="${t.id}">
          <button type="button" class="ops-gantt__name" data-row="${t.id}" title="${esc(t.name + ' · 끌어 순서 변경')}">
            <span class="ops-gantt__grip" aria-hidden="true"></span>
            <span class="ops-gantt__label">${esc(t.name)}</span>
          </button>
          <div class="ops-gantt__track">
            <div class="ops-gantt__now" style="left:calc(${nowIdx} * 100% / ${MONTHS.length})"></div>
            <div class="ops-gantt__bar" data-bar="${t.id}" style="${barPositionStyle(s, e, t.status)}" title="${esc(t.name + ' · ' + taskRange(t) + ' · 끌어 기간 조절')}">
              <span class="ops-gantt__handle ops-gantt__handle--start" data-handle="start"></span>
              <span class="ops-gantt__handle ops-gantt__handle--end" data-handle="end"></span>
            </div>
          </div>
        </div>
      `;
    }).join('');
    const project = (group && group.project) || '';
    const lane = (group && group.lane) || '';
    return `
      <section class="ops-block" data-group-project="${esc(project)}" data-group-lane="${esc(lane)}">
        <div class="ops-block__head"><span class="${colorClass}"></span>${esc(title)}</div>
        <div class="ops-gantt"><div class="ops-gantt__grid"><div></div>${head}${body}</div></div>
      </section>
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

  function projectDot(key) {
    return 'dot-' + (key === 'sales' || key === 'invest' ? 'corp' : (key || 'corp'));
  }

  function renderTimeline() {
    const chip = timelineFilter;
    const grouped = chip
      ? [[chip === 'sales' || chip === 'invest' ? LANES[chip] : PROJECTS[chip], projectDot(chip), tasksForChip(chip), chip === 'sales' || chip === 'invest' ? { lane: chip } : { project: chip }]]
      : [
          ['워치독', 'dot-watchdog', tasksForChip('watchdog'), { project: 'watchdog' }],
          ['마이안심이', 'dot-ansimi', tasksForChip('ansimi'), { project: 'ansimi' }],
          ['일괄소등', 'dot-switch', tasksForChip('switch'), { project: 'switch' }],
          ['비상벨', 'dot-bell', tasksForChip('bell'), { project: 'bell' }],
          ['영업', 'dot-corp', tasksForChip('sales'), { lane: 'sales' }],
          ['투자', 'dot-corp', tasksForChip('invest'), { lane: 'invest' }]
        ];
    return `
      ${renderQuickAdd()}
      ${renderEditor()}
      <p class="ops-hint">왼쪽 이름(제품개발·납품, 비명모델 업데이트 등)을 끌어 순서를 바꾸고, 막대를 끌어 기간을 조절하세요. 클릭하면 상세가 열립니다.</p>
      ${renderChips(chip)}
      ${grouped.map(([title, dot, list, group]) => renderGanttBlock(title, dot, list, group)).join('')}
    `;
  }

  function renderProjectPage() {
    const list = filteredTasks();
    return `
      ${renderQuickAdd()}
      ${renderEditor()}
      ${renderGanttBlock(pageTitle(), projectDot(filterProject || 'corp'), list, { project: filterProject || '', lane: filterLane || '' })}
      <h3 class="ops-h3">목록</h3>
      ${renderCards(list)}
    `;
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
      <div class="ops-form">
        <h3 class="ops-h3">GitHub 연결</h3>
        ${githubReady()
          ? '<p class="ops-hint">게시판 관리자와 같은 GitHub 연결을 쓰고 있습니다. gourry7/asungvoice · 「공유 저장」하면 사이트에 반영됩니다.</p>'
          : `<div class="ops-note">
              새 토큰을 만들지 마세요. <a href="../support/admin.html">게시판 관리자</a>에서 이미 넣은 저장소·토큰을 이 보드가 그대로 씁니다.
              이 브라우저에만 없다면 아래에 기존 토큰을 한 번 붙여넣으면 됩니다.
            </div>`}
        <label>GitHub 사용자</label><input id="gh-owner" value="${esc(cfg.owner || 'gourry7')}">
        <label>저장소</label><input id="gh-repo" value="${esc(cfg.repo || 'asungvoice')}">
        <label>브랜치</label><input id="gh-branch" value="${esc(cfg.branch || 'main')}">
        <label>기존 Personal Access Token</label>
        <input id="gh-token" type="password" autocomplete="off" placeholder="${cfg.token ? '저장됨 · 바꿀 때만 입력' : '게시판 관리자에 넣은 기존 토큰'}">
        <div class="ops-row" style="margin-top:10px"><button class="ops-btn ops-btn--blue" id="btn-gh" type="button">연결 저장</button></div>

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
    else html = renderProjectPage();
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
    if (key === 'status' || key === 'project' || key === 'lane' || key === 'start' || key === 'end') render();
  }

  function applyGanttRange(id, startIdx, endIdx, commit) {
    const t = board.tasks.find(x => x.id === id);
    const bar = document.querySelector('[data-bar="' + id + '"]');
    if (!t) return;
    const s = clampMonthIndex(startIdx);
    const e = Math.max(s, clampMonthIndex(endIdx));
    if (bar) {
      bar.style.cssText = barPositionStyle(s, e, t.status);
      bar.title = t.name + ' · ' + monthLabel(MONTHS[s]) + ' – ' + monthLabel(MONTHS[e]);
    }
    if (!commit) return;
    const start = MONTHS[s];
    const end = MONTHS[e];
    if (t.start === start && t.end === end) return;
    t.start = start;
    t.end = end;
    t.updatedBy = currentUser.id;
    t.updatedAt = nowIso();
    logActivity(t.name + ' · 기간 ' + taskRange(t));
    saveDraft();
    renderKeepScroll();
  }

  function onGanttPointerDown(e) {
    if (e.button !== 0) return;
    const bar = e.currentTarget;
    const id = bar.getAttribute('data-bar');
    const t = board.tasks.find(x => x.id === id);
    if (!t) return;
    const track = bar.parentElement;
    const handle = e.target.closest('[data-handle]');
    e.preventDefault();
    bar.setPointerCapture(e.pointerId);
    bar.classList.add('is-drag');
    ganttDrag = {
      id: id,
      mode: handle ? handle.getAttribute('data-handle') : 'move',
      startIdx: monthIndex(t.start),
      endIdx: monthIndex(t.end),
      origin: monthFromPointer(track, e.clientX),
      curS: monthIndex(t.start),
      curE: monthIndex(t.end),
      moved: false
    };
  }

  function onGanttPointerMove(e) {
    if (!ganttDrag) return;
    const bar = e.currentTarget;
    const track = bar.parentElement;
    const m = monthFromPointer(track, e.clientX);
    let s = ganttDrag.startIdx;
    let en = ganttDrag.endIdx;
    if (ganttDrag.mode === 'move') {
      const span = en - s;
      s = clampMonthIndex(ganttDrag.startIdx + (m - ganttDrag.origin));
      s = Math.min(s, MONTHS.length - 1 - span);
      en = s + span;
    } else if (ganttDrag.mode === 'start') {
      s = Math.min(m, en);
    } else {
      en = Math.max(m, s);
    }
    if (s !== ganttDrag.curS || en !== ganttDrag.curE) ganttDrag.moved = true;
    ganttDrag.curS = s;
    ganttDrag.curE = en;
    applyGanttRange(ganttDrag.id, s, en, false);
  }

  function onGanttPointerUp(e) {
    if (!ganttDrag) return;
    const d = ganttDrag;
    ganttDrag = null;
    e.currentTarget.classList.remove('is-drag');
    try { e.currentTarget.releasePointerCapture(e.pointerId); } catch { /* ignore */ }
    if (!d.moved) {
      editorId = d.id;
      renderKeepScroll();
      const box = $('.ops-editor');
      if (box) box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      return;
    }
    applyGanttRange(d.id, d.curS, d.curE, true);
  }

  function clearRowDropMarks() {
    $$('#view .ops-gantt__row').forEach(el => {
      el.classList.remove('is-drop-before', 'is-drop-after', 'is-dragging');
    });
  }

  function rowAtPoint(clientY, exceptId) {
    const rows = $$('#view .ops-gantt__row[data-row]');
    let best = null;
    let bestDist = Infinity;
    rows.forEach(row => {
      if (row.getAttribute('data-row') === exceptId) return;
      const r = row.getBoundingClientRect();
      const mid = (r.top + r.bottom) / 2;
      const dist = clientY >= r.top && clientY <= r.bottom ? 0 : Math.abs(clientY - mid);
      if (dist < bestDist) {
        bestDist = dist;
        best = row;
      }
    });
    return best;
  }

  function moveTaskRow(dragId, targetId, place, project, lane) {
    const t = board.tasks.find(x => x.id === dragId);
    if (!t || dragId === targetId) return;
    if (project && t.project !== project) t.project = project;
    if (lane && t.lane !== lane) t.lane = lane;
    const from = board.tasks.findIndex(x => x.id === dragId);
    if (from < 0) return;
    const [item] = board.tasks.splice(from, 1);
    let insert = board.tasks.findIndex(x => x.id === targetId);
    if (insert < 0) {
      board.tasks.splice(from, 0, item);
      return;
    }
    if (place === 'after') insert += 1;
    board.tasks.splice(insert, 0, item);
    t.updatedBy = currentUser.id;
    t.updatedAt = nowIso();
    logActivity(t.name + ' · 순서 변경');
    saveDraft();
    renderKeepScroll();
  }

  function onRowPointerDown(e) {
    if (e.button !== 0) return;
    if (ganttDrag) return;
    const name = e.currentTarget;
    const id = name.getAttribute('data-row');
    if (!id) return;
    e.preventDefault();
    name.setPointerCapture(e.pointerId);
    rowDrag = {
      id: id,
      y: e.clientY,
      moved: false,
      place: 'before',
      targetId: id,
      project: '',
      lane: ''
    };
  }

  function onRowPointerMove(e) {
    if (!rowDrag) return;
    if (!rowDrag.moved && Math.abs(e.clientY - rowDrag.y) < 6) return;
    rowDrag.moved = true;
    document.body.classList.add('is-row-drag');
    const src = document.querySelector('.ops-gantt__row[data-row="' + rowDrag.id + '"]');
    clearRowDropMarks();
    if (src) src.classList.add('is-dragging');
    if (src) {
      const sr = src.getBoundingClientRect();
      if (e.clientY >= sr.top && e.clientY <= sr.bottom) {
        rowDrag.targetId = rowDrag.id;
        return;
      }
    }
    const row = rowAtPoint(e.clientY, rowDrag.id);
    if (!row) return;
    const r = row.getBoundingClientRect();
    const place = e.clientY < r.top + r.height / 2 ? 'before' : 'after';
    row.classList.add(place === 'before' ? 'is-drop-before' : 'is-drop-after');
    const block = row.closest('.ops-block');
    rowDrag.targetId = row.getAttribute('data-row');
    rowDrag.place = place;
    rowDrag.project = (block && block.getAttribute('data-group-project')) || '';
    rowDrag.lane = (block && block.getAttribute('data-group-lane')) || '';
  }

  function onRowPointerUp(e) {
    if (!rowDrag) return;
    const d = rowDrag;
    rowDrag = null;
    document.body.classList.remove('is-row-drag');
    clearRowDropMarks();
    try { e.currentTarget.releasePointerCapture(e.pointerId); } catch { /* ignore */ }
    if (!d.moved) {
      editorId = d.id;
      renderKeepScroll();
      const box = $('.ops-editor');
      if (box) box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      return;
    }
    if (d.targetId && d.targetId !== d.id) {
      moveTaskRow(d.id, d.targetId, d.place, d.project, d.lane);
    }
  }

  function bindView() {
    $$('#view .ops-editor [data-k]').forEach(el => {
      const id = editorId;
      const ev = el.tagName === 'SELECT' || el.type === 'month' ? 'change' : 'change';
      el.addEventListener(ev, () => patchTask(id, el.dataset.k, el.value));
      if ((el.tagName === 'INPUT' && el.type !== 'month') || el.tagName === 'TEXTAREA') {
        el.addEventListener('blur', () => patchTask(id, el.dataset.k, el.value));
      }
    });
    $$('#view [data-edit]').forEach(btn => {
      btn.addEventListener('click', () => {
        editorId = btn.getAttribute('data-edit');
        render();
        const box = $('.ops-editor');
        if (box) box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    });
    $$('#view [data-bar]').forEach(bar => {
      bar.addEventListener('pointerdown', onGanttPointerDown);
      bar.addEventListener('pointermove', onGanttPointerMove);
      bar.addEventListener('pointerup', onGanttPointerUp);
      bar.addEventListener('pointercancel', onGanttPointerUp);
    });
    $$('#view .ops-gantt__name[data-row]').forEach(name => {
      name.addEventListener('pointerdown', onRowPointerDown);
      name.addEventListener('pointermove', onRowPointerMove);
      name.addEventListener('pointerup', onRowPointerUp);
      name.addEventListener('pointercancel', onRowPointerUp);
    });
    $$('#view [data-close-editor]').forEach(btn => {
      btn.addEventListener('click', () => { editorId = ''; render(); });
    });
    $$('#view [data-chip]').forEach(btn => {
      btn.addEventListener('click', () => {
        timelineFilter = btn.getAttribute('data-chip') || '';
        render();
      });
    });
    $$('#view [data-del]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.del;
        const t = board.tasks.find(x => x.id === id);
        if (!t || !confirm('이 일정을 삭제할까요?')) return;
        board.tasks = board.tasks.filter(x => x.id !== id);
        if (editorId === id) editorId = '';
        logActivity(t.name + ' 삭제');
        saveDraft();
        render();
      });
    });
    const qa = $('#quick-add');
    if (qa) {
      qa.addEventListener('submit', e => {
        e.preventDefault();
        const name = ($('#qa-name').value || '').trim();
        if (!name) return;
        const start = $('#qa-start').value || NOW_MONTH;
        let end = $('#qa-end').value || start;
        if (end < start) end = start;
        const task = {
          id: uid('row'),
          name: name,
          project: $('#qa-project').value,
          lane: $('#qa-lane').value,
          status: $('#qa-status').value,
          start: start,
          end: end,
          owner: currentUser.name,
          note: ''
        };
        board.tasks.unshift(task);
        editorId = task.id;
        logActivity(name + ' 추가');
        saveDraft();
        render();
      });
    }
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

  async function saveGithub() {
    const prev = getGithubCfg();
    const owner = ($('#gh-owner').value || '').trim();
    const repo = ($('#gh-repo').value || '').trim();
    const branch = ($('#gh-branch').value || '').trim() || 'main';
    const token = ($('#gh-token').value || '').trim() || prev.token;
    if (!owner || !repo) return alert('GitHub 사용자와 저장소 이름을 넣어 주세요.');
    if (!token) return alert('게시판 관리자에 넣은 기존 토큰을 붙여 넣어 주세요. 새로 발급하지 않아도 됩니다.');
    const btn = $('#btn-gh');
    if (btn) { btn.disabled = true; btn.textContent = '확인 중…'; }
    setStatus('GitHub 연결 확인 중…', '');
    try {
      const res = await fetch('https://api.github.com/repos/' + owner + '/' + repo, {
        headers: githubHeaders(token)
      });
      if (res.status === 401 || res.status === 403) {
        throw new Error('토큰이 거부되었습니다. repo 권한으로 새로 발급해 붙여 넣어 주세요.');
      }
      if (res.status === 404) {
        throw new Error('저장소를 찾을 수 없습니다. 사용자·저장소 이름과 토큰 권한을 확인해 주세요.');
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.message || 'GitHub 연결 실패');
      }
      setGithubCfg({ ...prev, owner, repo, branch, token });
      if ($('#gh-token').value) $('#gh-token').value = '';
      setStatus('GitHub 연결됨. 이제 「공유 저장」을 누르면 사이트에 반영됩니다.', 'ok');
      render();
      if (pendingShare) {
        pendingShare = false;
        await persist();
      }
    } catch (err) {
      setStatus(err.message || 'GitHub 연결 실패', 'err');
      alert(err.message || 'GitHub 연결 실패');
    } finally {
      const again = $('#btn-gh');
      if (again) { again.disabled = false; again.textContent = '연결 저장'; }
    }
  }

  function addRow() {
    if (page === 'settings' || page === 'activity') {
      page = 'timeline';
      filterProject = '';
      filterLane = '';
      render();
    }
    const name = $('#qa-name');
    if (name) {
      name.focus();
      name.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  async function persist() {
    if (!(await validateSession())) {
      alert('세션이 만료되었습니다.');
      clearSession();
      showLogin();
      return;
    }
    if (!githubReady()) {
      pendingShare = true;
      openGithubSettings('게시판 관리자에서 쓴 기존 GitHub 연결을 이 브라우저에 한 번 넣어 주세요.');
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
      pendingShare = false;
      setStatus('사이트에 공유되었습니다. 반영까지 1~2분 걸릴 수 있습니다.', 'ok');
    } catch (err) {
      if (err && err.code === 'no-github') {
        pendingShare = true;
        openGithubSettings(err.message);
        return;
      }
      const blob = new Blob([json], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'ops-board.json';
      a.click();
      setStatus('GitHub 저장 실패 — JSON을 받았습니다. ' + (err && err.message ? err.message : ''), 'err');
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
        if (page === 'timeline') timelineFilter = '';
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
      if (await validateSession()) {
        board = await loadJson(DATA_PATH);
        await showApp();
      } else {
        showLogin();
      }
    } catch (err) {
      showLoginError(err && err.message ? err.message : '페이지를 불러오지 못했습니다. 새로고침해 주세요.');
    }
  }

  init();
})();
