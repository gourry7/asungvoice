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
  const RUNTIME_PATH = 'data/ops-runtime.json';
  const SESSION_SALT = 'asung-voice-ops-v1';
  const SAVE_KEY_SALT = 'asung-voice-ops-save-v1';
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
  const RANGE_START = '2026-08-01';
  const RANGE_END = '2027-06-30';
  const DAYS = buildDayRange(RANGE_START, RANGE_END);
  const BAR_COLORS = [
    '#2383e2', '#1b6fe8', '#3aaf7a', '#0f7b3c', '#d97706',
    '#d47080', '#c0392b', '#7b61c8', '#5a5a55', '#d3d1cb'
  ];

  let config = { sessionMinutes: 180, maxAttempts: 5, lockoutMinutes: 15, users: [] };
  let runtime = null;
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
  let ganttDrag = null;
  let rowDrag = null;
  let persistBusy = false;
  let persistAgain = false;
  const githubShaCache = Object.create(null);
  let githubWriteChain = Promise.resolve();
  let loadedTaskIds = new Set();

  const $ = sel => document.querySelector(sel);
  const $$ = sel => [...document.querySelectorAll(sel)];

  function pad2(n) {
    return String(n).padStart(2, '0');
  }

  function ymdFromParts(y, m, d) {
    return y + '-' + pad2(m) + '-' + pad2(d);
  }

  function buildDayRange(start, end) {
    const out = [];
    const [sy, sm, sd] = start.split('-').map(Number);
    const [ey, em, ed] = end.split('-').map(Number);
    const cur = new Date(sy, sm - 1, sd);
    const last = new Date(ey, em - 1, ed);
    while (cur <= last) {
      out.push(ymdFromParts(cur.getFullYear(), cur.getMonth() + 1, cur.getDate()));
      cur.setDate(cur.getDate() + 1);
    }
    return out;
  }

  function kstParts(d) {
    const parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Seoul',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hourCycle: 'h23'
    }).formatToParts(d || new Date());
    const g = type => (parts.find(p => p.type === type) || {}).value || '00';
    return { y: g('year'), m: g('month'), day: g('day'), h: g('hour'), min: g('minute'), s: g('second') };
  }

  function todayYmd() {
    const p = kstParts();
    return p.y + '-' + p.m + '-' + p.day;
  }

  function lastDayOfMonth(ym) {
    const [y, m] = String(ym).split('-').map(Number);
    const dt = new Date(y, m, 0);
    return ymdFromParts(dt.getFullYear(), dt.getMonth() + 1, dt.getDate());
  }

  function normalizeDate(value, role) {
    const v = String(value || '').trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(v)) return v;
    if (/^\d{4}-\d{2}$/.test(v)) return role === 'end' ? lastDayOfMonth(v) : v + '-01';
    return role === 'end' ? RANGE_END : RANGE_START;
  }

  function normalizeBoardDates(data) {
    if (!data || !Array.isArray(data.tasks)) return data;
    data.tasks.forEach(t => {
      t.start = normalizeDate(t.start, 'start');
      t.end = normalizeDate(t.end, 'end');
      if (t.end < t.start) t.end = t.start;
    });
    return data;
  }

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
    const p = kstParts();
    return p.y + '-' + p.m + '-' + p.day + 'T' + p.h + ':' + p.min + ':' + p.s + '+09:00';
  }

  function fmtWhen(iso) {
    if (!iso) return '';
    return iso.replace('T', ' ').slice(0, 16);
  }

  function base64ToUtf8(b64) {
    const binary = atob(String(b64 || '').replace(/\s/g, ''));
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }

  async function loadJsonFromGithub(path) {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      throw new Error('no-github');
    }
    const branch = cfg.branch || 'main';
    const api = `https://api.github.com/repos/${cfg.owner}/${cfg.repo}/contents/${path}`
      + '?ref=' + encodeURIComponent(branch)
      + '&_=' + Date.now();
    const res = await fetch(api, {
      headers: githubHeaders(cfg.token, false),
      cache: 'no-store'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || ('파일 조회 실패 (' + res.status + ')'));
    }
    const data = await res.json();
    if (data && data.sha) githubShaCache[path] = data.sha;
    return JSON.parse(base64ToUtf8(data.content || ''));
  }

  async function loadJson(path) {
    // Pages CDN caches JSON ~10 minutes. After a GitHub save, refreshing from
    // Pages can look like the new schedule vanished. Prefer Contents API.
    if (githubReady()) {
      let lastErr = null;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          return await loadJsonFromGithub(path);
        } catch (err) {
          lastErr = err;
          await sleep(150 + attempt * 200);
        }
      }
      // Never fall back to Pages for the live board — that is the stale-cache bug.
      if (path === DATA_PATH) {
        throw lastErr || new Error('일정을 GitHub에서 불러오지 못했습니다.');
      }
    }
    const url = new URL(path, scriptBase).href + '?t=' + Date.now();
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error(path + ' 를 불러올 수 없습니다.');
    return res.json();
  }

  function rememberLoadedBoard(data) {
    normalizeBoardDates(data);
    loadedTaskIds = new Set((data && data.tasks || []).map(t => t.id).filter(Boolean));
  }

  function mergeRemoteTasks(remote) {
    if (!remote || !Array.isArray(remote.tasks)) return;
    const localTasks = board.tasks || [];
    const seen = new Set();
    const merged = [];
    for (const t of localTasks) {
      if (!t || !t.id || seen.has(t.id)) continue;
      merged.push(t);
      seen.add(t.id);
    }
    for (const t of remote.tasks) {
      if (!t || !t.id || seen.has(t.id)) continue;
      // Keep tasks others added since we loaded; skip ones we deleted locally.
      if (!loadedTaskIds.has(t.id)) {
        merged.push(t);
        seen.add(t.id);
      }
    }
    board.tasks = merged;
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
    localStorage.removeItem(GITHUB_KEY);
    currentUser = null;
    if (idleTimer) clearTimeout(idleTimer);
  }

  function clearGithubCfg() {
    localStorage.removeItem(GITHUB_KEY);
    Object.keys(githubShaCache).forEach(k => { delete githubShaCache[k]; });
  }

  async function verifyGithubToken() {
    const cfg = getGithubCfg();
    if (!cfg.token || !cfg.owner || !cfg.repo) return 'missing';
    try {
      const res = await fetch('https://api.github.com/user', {
        headers: githubHeaders(cfg.token, false),
        cache: 'no-store'
      });
      if (res.status === 401 || res.status === 403) {
        clearGithubCfg();
        return 'auth';
      }
      return res.ok ? 'ok' : 'auth';
    } catch {
      return 'network';
    }
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

  function b64ToBytes(b64) {
    const bin = atob(b64);
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  async function deriveSaveKey(password) {
    const enc = new TextEncoder();
    const material = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']);
    return crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt: enc.encode(SAVE_KEY_SALT), iterations: 100000, hash: 'SHA-256' },
      material,
      { name: 'AES-GCM', length: 256 },
      false,
      ['decrypt']
    );
  }

  async function decryptGithubToken(password, tokenEnc) {
    const raw = b64ToBytes(tokenEnc);
    const iv = raw.subarray(0, 12);
    const tag = raw.subarray(12, 28);
    const data = raw.subarray(28);
    const cipher = new Uint8Array(data.length + tag.length);
    cipher.set(data, 0);
    cipher.set(tag, data.length);
    const key = await deriveSaveKey(password);
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, cipher);
    return new TextDecoder().decode(plain);
  }

  async function unlockGithubWithPassword(password) {
    if (!runtime || !runtime.tokenEnc || !password) return false;
    try {
      const token = await decryptGithubToken(password, runtime.tokenEnc);
      if (!token || (token.indexOf('ghp_') !== 0 && token.indexOf('github_pat_') !== 0)) return false;
      setGithubCfg({
        owner: runtime.owner || GITHUB_DEFAULTS.owner,
        repo: runtime.repo || GITHUB_DEFAULTS.repo,
        branch: runtime.branch || GITHUB_DEFAULTS.branch,
        pagesUrl: runtime.pagesUrl || GITHUB_DEFAULTS.pagesUrl,
        token
      });
      return githubReady();
    } catch {
      return false;
    }
  }

  function githubHeaders(token, withJsonBody) {
    // Keep headers to GitHub CORS allow-list only (Authorization, Content-Type,
    // X-GitHub-Api-Version). Extra headers like Cache-Control caused Failed to fetch.
    const headers = {
      Authorization: 'Bearer ' + token,
      'X-GitHub-Api-Version': '2022-11-28'
    };
    if (withJsonBody) headers['Content-Type'] = 'application/json';
    return headers;
  }

  function utf8ToBase64(text) {
    const bytes = new TextEncoder().encode(text);
    let binary = '';
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function fetchGithubFileSha(api, token) {
    const url = api + '?_=' + Date.now() + Math.random().toString(36).slice(2);
    const getRes = await fetch(url, {
      headers: githubHeaders(token, false),
      cache: 'no-store'
    });
    if (getRes.ok) return (await getRes.json()).sha || null;
    if (getRes.status === 404) return null;
    const err = await getRes.json().catch(() => ({}));
    throw new Error(err.message || ('파일 조회 실패 (' + getRes.status + ')'));
  }

  async function saveToGithub(path, jsonText, message) {
    const run = async () => {
      const cfg = getGithubCfg();
      if (!cfg.token || !cfg.owner || !cfg.repo) {
        const err = new Error('저장 연결이 없습니다. 다시 로그인해 주세요.');
        err.code = 'no-github';
        throw err;
      }
      const api = `https://api.github.com/repos/${cfg.owner}/${cfg.repo}/contents/${path}`;
      const headers = githubHeaders(cfg.token, true);
      const branch = cfg.branch || 'main';
      const content = utf8ToBase64(jsonText);
      const commitMessage = message || 'Update ops board';
      let sha = githubShaCache[path] || null;

      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          if (!sha) sha = await fetchGithubFileSha(api, cfg.token);
          const body = { message: commitMessage, content, branch };
          if (sha) body.sha = sha;
          const putRes = await fetch(api, {
            method: 'PUT',
            headers,
            body: JSON.stringify(body),
            cache: 'no-store'
          });
          if (putRes.ok) {
            const data = await putRes.json().catch(() => ({}));
            const nextSha = data && data.content && data.content.sha;
            if (nextSha) githubShaCache[path] = nextSha;
            else delete githubShaCache[path];
            return;
          }
          if (putRes.status === 401 || putRes.status === 403) {
            clearGithubCfg();
            const err = new Error('저장 권한이 없습니다. 다시 로그인해 주세요.');
            err.code = 'no-github';
            throw err;
          }
          const err = await putRes.json().catch(() => ({}));
          const conflict = putRes.status === 409
            || putRes.status === 422
            || /does not match/i.test(err.message || '');
          if (conflict && attempt < 2) {
            delete githubShaCache[path];
            sha = null;
            await sleep(200 + attempt * 200);
            continue;
          }
          throw new Error(err.message || ('GitHub 저장 실패 (' + putRes.status + ')'));
        } catch (err) {
          if (err && err.code === 'no-github') throw err;
          if (err && /Failed to fetch|NetworkError|Load failed/i.test(err.message || '') && attempt < 2) {
            delete githubShaCache[path];
            sha = null;
            await sleep(200 + attempt * 200);
            continue;
          }
          if (err && /Failed to fetch|NetworkError|Load failed/i.test(err.message || '')) {
            throw new Error('네트워크/CORS로 저장이 막혔습니다. 새로고침 후 다시 로그인해 보세요.');
          }
          throw err;
        }
      }
    };

    const queued = githubWriteChain.then(run, run);
    githubWriteChain = queued.catch(() => {});
    return queued;
  }

  function saveDraft() {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(board));
    dirty = true;
    if (githubReady()) {
      setStatus('저장되지 않은 변경이 있습니다. 「저장」을 누르세요.', '');
    } else {
      setStatus('저장 연결이 없습니다. 다시 로그인해 주세요.', 'err');
    }
  }

  function restoreDraft() {
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return;
    try {
      const draft = JSON.parse(raw);
      if (!draft || !Array.isArray(draft.tasks)) return;
      const draftAt = Date.parse(draft.updatedAt || '') || 0;
      const boardAt = Date.parse(board.updatedAt || '') || 0;
      const boardIds = new Set((board.tasks || []).map(t => t.id));
      const draftHasNew = draft.tasks.some(t => t && t.id && !boardIds.has(t.id));
      // Drop drafts already reflected on the server so they cannot hide fresh loads.
      if (draftAt <= boardAt && !draftHasNew) {
        localStorage.removeItem(DRAFT_KEY);
        return;
      }
      board = { ...board, ...draft };
      dirty = true;
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

  function dayIndex(ymd) {
    const key = normalizeDate(ymd, 'start');
    const i = DAYS.indexOf(key);
    if (i >= 0) return i;
    if (key < DAYS[0]) return 0;
    return DAYS.length - 1;
  }

  function clampDayIndex(i) {
    return Math.max(0, Math.min(DAYS.length - 1, i));
  }

  function statusBarColor(status) {
    return {
      doing: '#2383e2',
      review: '#d97706',
      planned: '#d3d1cb',
      ongoing: '#3aaf7a',
      done: '#c5c4be'
    }[status] || '#d3d1cb';
  }

  function taskBarColor(t) {
    if (t && t.color) return t.color;
    return statusBarColor(t && t.status);
  }

  function barPositionStyle(startIdx, endIdx, taskOrStatus) {
    const n = DAYS.length;
    const s = clampDayIndex(startIdx);
    const e = Math.max(s, clampDayIndex(endIdx));
    const span = e - s + 1;
    const color = typeof taskOrStatus === 'string'
      ? statusBarColor(taskOrStatus)
      : taskBarColor(taskOrStatus);
    return 'left:calc(' + s + ' * 100% / ' + n + ' + 1px);width:calc(' + span + ' * 100% / ' + n + ' - 2px);background:' + color;
  }

  function dayFromPointer(track, clientX) {
    const r = track.getBoundingClientRect();
    if (!r.width) return 0;
    const x = Math.min(Math.max(clientX - r.left, 0), r.width - 0.001);
    return clampDayIndex(Math.floor(x / r.width * DAYS.length));
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
    const p = String(ym).split('-');
    return Number(p[1] || 0) + '월';
  }

  function dayLabel(ymd) {
    if (!ymd) return '';
    const p = String(ymd).split('-');
    if (p.length < 3) return monthLabel(ymd);
    return Number(p[1]) + '/' + Number(p[2]);
  }

  function taskRange(t) {
    if (!t.start && !t.end) return '';
    if (t.start === t.end) return dayLabel(t.start);
    return dayLabel(t.start) + ' – ' + dayLabel(t.end);
  }

  function renderQuickAdd() {
    const today = todayYmd();
    return `
      <form id="quick-add" class="ops-add">
        <div><label>할 일</label><input id="qa-name" placeholder="예: 금형 시사출" required></div>
        <div><label>프로젝트</label><select id="qa-project">${options(PROJECTS, filterProject || 'watchdog')}</select></div>
        <div><label>구분</label><select id="qa-lane">${options(LANES, filterLane || 'product')}</select></div>
        <div><label>상태</label><select id="qa-status">${options(STATUSES, 'planned')}</select></div>
        <div><label>시작</label><input type="date" id="qa-start" min="${RANGE_START}" max="${RANGE_END}" value="${today}"></div>
        <div><label>끝</label><input type="date" id="qa-end" min="${RANGE_START}" max="${RANGE_END}" value="${today}"></div>
        <button type="submit" class="ops-btn ops-btn--blue ops-btn--sm">일정 추가</button>
      </form>
    `;
  }

  function renderColorPicker(t) {
    const current = t.color || '';
    const swatches = BAR_COLORS.map(c =>
      `<button type="button" class="ops-swatch${current === c ? ' is-on' : ''}" data-set-color="${c}" style="background:${c}" title="${c}"></button>`
    ).join('');
    return `
      <div class="ops-colors">
        <label>타임라인 막대 색상 (아래에서 고르세요)</label>
        <div class="ops-swatches">
          <button type="button" class="ops-swatch ops-swatch--auto${!current ? ' is-on' : ''}" data-set-color="" title="상태에 맞춤">자동</button>
          ${swatches}
          <label class="ops-swatch ops-swatch--custom" title="직접 고르기">
            <input type="color" data-k="color" value="${esc(current || taskBarColor(t))}">
          </label>
        </div>
      </div>
    `;
  }

  function renderEditor() {
    const t = (board.tasks || []).find(x => x.id === editorId);
    if (!t) return '';
    return `
      <div class="ops-editor" data-id="${t.id}">
        <div class="ops-editor__title">「${esc(t.name)}」 편집</div>
        ${renderColorPicker(t)}
        <div class="ops-editor__grid">
          <div><label>할 일</label><input data-k="name" value="${esc(t.name)}"></div>
          <div><label>프로젝트</label><select data-k="project">${options(PROJECTS, t.project)}</select></div>
          <div><label>구분</label><select data-k="lane">${options(LANES, t.lane)}</select></div>
          <div><label>상태</label><select data-k="status">${options(STATUSES, t.status)}</select></div>
          <div><label>시작</label><input type="date" data-k="start" min="${RANGE_START}" max="${RANGE_END}" value="${esc(normalizeDate(t.start, 'start'))}"></div>
          <div><label>끝</label><input type="date" data-k="end" min="${RANGE_START}" max="${RANGE_END}" value="${esc(normalizeDate(t.end, 'end'))}"></div>
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

  function renderGanttMonthHead() {
    const today = todayYmd();
    const bands = [];
    for (let i = 0; i < DAYS.length; i++) {
      const ym = DAYS[i].slice(0, 7);
      const last = bands[bands.length - 1];
      if (last && last.ym === ym) last.count += 1;
      else bands.push({ ym, count: 1, hasToday: false });
      if (DAYS[i] === today) bands[bands.length - 1].hasToday = true;
    }
    return bands.map(b =>
      `<div class="ops-gantt__h${b.hasToday ? ' is-now' : ''}" style="flex:${b.count}">${b.hasToday ? monthLabel(b.ym) + '·오늘' : monthLabel(b.ym)}</div>`
    ).join('');
  }

  function renderGanttBlock(title, colorClass, list, group) {
    if (!list.length) {
      return `<section class="ops-block"><div class="ops-block__head"><span class="${colorClass}"></span>${esc(title)} <span style="font-weight:500;color:var(--ops-muted);font-size:.8rem">일정 없음</span></div></section>`;
    }
    const today = todayYmd();
    const nowIdx = dayIndex(today);
    const head = renderGanttMonthHead();
    const body = list.map(t => {
      const s = dayIndex(t.start);
      const e = dayIndex(t.end);
      return `
        <div class="ops-gantt__row" data-row="${t.id}">
          <button type="button" class="ops-gantt__name" data-row="${t.id}" title="${esc(t.name + ' · 끌어 순서 변경')}">
            <span class="ops-gantt__grip" aria-hidden="true"></span>
            <span class="ops-gantt__label">${esc(t.name)}</span>
          </button>
          <div class="ops-gantt__track">
            <div class="ops-gantt__now" style="left:calc(${nowIdx} * 100% / ${DAYS.length} + 100% / ${DAYS.length} / 2)"></div>
            <div class="ops-gantt__bar" data-bar="${t.id}" style="${barPositionStyle(s, e, t)}" title="${esc(t.name + ' · ' + taskRange(t) + ' · 끌어 일 단위로 조절')}">
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
        <div class="ops-gantt">
          <div class="ops-gantt__grid" style="--gantt-days:${DAYS.length}">
            <div class="ops-gantt__head">
              <div></div>
              <div class="ops-gantt__months">${head}</div>
            </div>
            ${body}
          </div>
        </div>
      </section>
    `;
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
      <p class="ops-hint">왼쪽 일정 이름을 클릭하면 위쪽에 편집 칸이 열리고, 맨 위에 색 칩이 있습니다. 막대를 끌면 일 단위로 기간이 바뀝니다.</p>
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
    return `
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
      </div>
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
    if (!t) return;
    let next = key === 'color' && !value ? '' : value;
    if (key === 'start' || key === 'end') {
      next = normalizeDate(next, key);
      if (key === 'start' && t.end && next > t.end) t.end = next;
      if (key === 'end' && t.start && next < t.start) next = t.start;
    }
    if ((t[key] || '') === next) return;
    if (key === 'color' && !next) delete t.color;
    else t[key] = next;
    t.updatedBy = currentUser.id;
    t.updatedAt = nowIso();
    logActivity(`${t.name || '항목'} · ${key === 'color' ? '막대 색' : key} 수정`);
    saveDraft();
    if (key === 'status' || key === 'project' || key === 'lane' || key === 'start' || key === 'end' || key === 'color') render();
  }

  function applyGanttRange(id, startIdx, endIdx, commit) {
    const t = board.tasks.find(x => x.id === id);
    const bar = document.querySelector('[data-bar="' + id + '"]');
    if (!t) return;
    const s = clampDayIndex(startIdx);
    const e = Math.max(s, clampDayIndex(endIdx));
    if (bar) {
      bar.style.cssText = barPositionStyle(s, e, t);
      bar.title = t.name + ' · ' + dayLabel(DAYS[s]) + ' – ' + dayLabel(DAYS[e]);
    }
    if (!commit) return;
    const start = DAYS[s];
    const end = DAYS[e];
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
      startIdx: dayIndex(t.start),
      endIdx: dayIndex(t.end),
      origin: dayFromPointer(track, e.clientX),
      curS: dayIndex(t.start),
      curE: dayIndex(t.end),
      moved: false
    };
  }

  function onGanttPointerMove(e) {
    if (!ganttDrag) return;
    const bar = e.currentTarget;
    const track = bar.parentElement;
    const m = dayFromPointer(track, e.clientX);
    let s = ganttDrag.startIdx;
    let en = ganttDrag.endIdx;
    if (ganttDrag.mode === 'move') {
      const span = en - s;
      s = clampDayIndex(ganttDrag.startIdx + (m - ganttDrag.origin));
      s = Math.min(s, DAYS.length - 1 - span);
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
      const ev = el.tagName === 'SELECT' || el.type === 'date' || el.type === 'month' || el.type === 'color' ? 'change' : 'change';
      el.addEventListener(ev, () => {
        let val = el.value;
        if (el.dataset.k === 'start' || el.dataset.k === 'end') {
          val = normalizeDate(val, el.dataset.k);
          const t = board.tasks.find(x => x.id === id);
          if (t) {
            if (el.dataset.k === 'start' && t.end && val > t.end) patchTask(id, 'end', val);
            if (el.dataset.k === 'end' && t.start && val < t.start) val = t.start;
          }
        }
        patchTask(id, el.dataset.k, val);
      });
      if ((el.tagName === 'INPUT' && el.type !== 'date' && el.type !== 'month' && el.type !== 'color') || el.tagName === 'TEXTAREA') {
        el.addEventListener('blur', () => patchTask(id, el.dataset.k, el.value));
      }
    });
    $$('#view [data-set-color]').forEach(btn => {
      btn.addEventListener('click', () => {
        const color = btn.getAttribute('data-set-color') || '';
        patchTask(editorId, 'color', color);
      });
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
        const start = normalizeDate($('#qa-start').value || todayYmd(), 'start');
        let end = normalizeDate($('#qa-end').value || start, 'end');
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
      setStatus('비밀번호가 변경되었습니다.', 'ok');
    } catch (err) {
      alert(err.message);
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
    if (persistBusy) {
      persistAgain = true;
      return;
    }
    persistBusy = true;
    persistAgain = false;
    try {
      if (!(await validateSession())) {
        alert('세션이 만료되었습니다.');
        clearSession();
        showLogin();
        return;
      }
      if (!githubReady()) {
        setStatus('저장 서버에 연결되지 않았습니다. 다시 로그인해 주세요.', 'err');
        return;
      }
      const tokenState = await verifyGithubToken();
      if (tokenState === 'auth' || tokenState === 'missing') {
        clearSession();
        showLogin();
        showLoginError('저장 연결이 만료되었습니다. 다시 로그인해 주세요.');
        return;
      }
      if (tokenState === 'network') {
        setStatus('네트워크 오류로 저장을 확인할 수 없습니다. 잠시 후 다시 눌러 주세요.', 'err');
        return;
      }
      setStatus('사이트에 저장 중…', '');
      // Pull latest first so a stale tab cannot wipe someone else's newer rows.
      try {
        const remote = await loadJsonFromGithub(DATA_PATH);
        mergeRemoteTasks(remote);
      } catch { /* save still proceeds with local board */ }
      board.updatedAt = nowIso();
      board.updatedBy = currentUser.id;
      const json = JSON.stringify(board, null, 2);
      await saveToGithub(DATA_PATH, json, 'Update ops board (' + currentUser.name + ')');
      // Confirm Contents API sees the write — do not trust a blind OK.
      const verified = await loadJsonFromGithub(DATA_PATH);
      if (!verified || verified.updatedAt !== board.updatedAt) {
        throw new Error('저장 후 확인에 실패했습니다. 다시 저장해 주세요.');
      }
      board = verified;
      rememberLoadedBoard(board);
      localStorage.removeItem(DRAFT_KEY);
      dirty = false;
      setStatus('사이트에 저장되었습니다. 다른 분도 새로고침하면 같습니다.', 'ok');
      render();
    } catch (err) {
      if (err && err.code === 'no-github') {
        setStatus('저장 서버에 연결되지 않았습니다. 다시 로그인해 주세요.', 'err');
        return;
      }
      let msg = err && err.message ? err.message : '다시 눌러 주세요.';
      if (/Failed to fetch|NetworkError|Load failed|네트워크\/CORS/i.test(msg)) {
        msg = '브라우저가 GitHub 저장을 막았습니다. 강력 새로고침 후 다시 로그인해 주세요.';
      }
      setStatus('사이트 저장 실패 — ' + msg, 'err');
    } finally {
      persistBusy = false;
      if (persistAgain) {
        persistAgain = false;
        setTimeout(() => { persist(); }, 300);
      }
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
    normalizeBoardDates(board);
    if (dirty) {
      if (githubReady()) setStatus('저장되지 않은 변경이 있습니다. 「저장」을 누르세요.', '');
      else setStatus('저장 연결이 없습니다. 다시 로그인해 주세요.', 'err');
    } else setStatus(board.updatedBy ? `마지막 저장 ${displayName(board.updatedBy)} · ${fmtWhen(board.updatedAt)}` : '', '');
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
      const pass = $('#login-pass').value || '';
      await createSession(user, hash);
      if (!runtime) {
        try { runtime = await loadJson(RUNTIME_PATH); }
        catch { runtime = null; }
      }
      await unlockGithubWithPassword(pass);
      $('#login-pass').value = '';
      board = await loadJson(DATA_PATH);
      rememberLoadedBoard(board);
      await showApp();
      if (!githubReady()) {
        setStatus('저장 연결에 실패했습니다. 비밀번호 변경 후에는 관리자에게 문의하세요.', 'err');
      }
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
      if (navigator.serviceWorker) {
        navigator.serviceWorker.getRegistrations().then(regs => {
          regs.forEach(r => r.unregister());
        }).catch(() => {});
      }
      bindChrome();
      config = { ...config, ...(await loadJson(CONFIG_PATH)) };
      try { runtime = await loadJson(RUNTIME_PATH); }
      catch { runtime = null; }
      if (await validateSession()) {
        const tokenState = githubReady() ? await verifyGithubToken() : 'missing';
        if (tokenState !== 'ok') {
          clearSession();
          showLogin();
          showLoginError(tokenState === 'network'
            ? '네트워크 오류입니다. 잠시 후 다시 로그인해 주세요.'
            : '저장을 쓰려면 한 번 더 로그인해 주세요.');
          return;
        }
        board = await loadJson(DATA_PATH);
        rememberLoadedBoard(board);
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
