/**
 * Task Manager — v3
 * Cognito PKCE auth + API Gateway/Lambda backend.
 */
"use strict";

const CFG = window.APP_CONFIG || {};
const STATUSES = ["pending", "in_progress", "done"];
const EMPTY = {
  pending:     { icon: "◷", text: "Nenhuma tarefa pendente" },
  in_progress: { icon: "◐", text: "Nada em andamento" },
  done:        { icon: "●", text: "Nenhuma tarefa concluída" },
};
const PRIORITY_LABEL = { low: "Baixa", medium: "Média", high: "Alta" };

const $  = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));

/* ══════════════════════════ Auth ══════════════════════════ */
const Auth = {
  KEY: "tm_tokens",
  CV:  "tm_cv",

  async login() {
    const cv = this._verifier();
    sessionStorage.setItem(this.CV, cv);
    const ch = await this._challenge(cv);
    const p = new URLSearchParams({
      response_type: "code",
      client_id: CFG.COGNITO_CLIENT_ID,
      redirect_uri: CFG.REDIRECT_URI,
      scope: "openid email profile",
      code_challenge_method: "S256",
      code_challenge: ch,
    });
    location.href = `${CFG.COGNITO_DOMAIN}/login?${p}`;
  },

  async handleCallback() {
    const code = new URLSearchParams(location.search).get("code");
    if (!code) return false;
    const cv = sessionStorage.getItem(this.CV);
    if (!cv) return false;

    try {
      const r = await fetch(`${CFG.COGNITO_DOMAIN}/oauth2/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          grant_type: "authorization_code",
          client_id: CFG.COGNITO_CLIENT_ID,
          redirect_uri: CFG.REDIRECT_URI,
          code, code_verifier: cv,
        }),
      });
      if (!r.ok) return false;
      const t = await r.json();
      const c = this._decode(t.id_token) || {};
      localStorage.setItem(this.KEY, JSON.stringify({
        id_token: t.id_token,
        expires_at: Math.floor(Date.now() / 1000) + (t.expires_in || 3600),
        email: c.email || "",
        name:  c.name || c.email || "",
      }));
      sessionStorage.removeItem(this.CV);
      history.replaceState({}, "", CFG.REDIRECT_URI);
      return true;
    } catch { return false; }
  },

  token() {
    const t = this._load();
    if (!t) return null;
    if (t.expires_at && Date.now() / 1000 >= t.expires_at - 60) {
      localStorage.removeItem(this.KEY);
      return null;
    }
    return t.id_token || null;
  },

  user() { const t = this._load(); return t ? { email: t.email, name: t.name } : null; },
  ok()   { return this.token() !== null; },

  logout() {
    localStorage.removeItem(this.KEY);
    location.href = `${CFG.COGNITO_DOMAIN}/logout?` +
      new URLSearchParams({ client_id: CFG.COGNITO_CLIENT_ID, logout_uri: CFG.REDIRECT_URI });
  },

  _load()  { try { return JSON.parse(localStorage.getItem(this.KEY)); } catch { return null; } },
  _decode(t) { try { return JSON.parse(atob(t.split(".")[1].replace(/-/g,"+").replace(/_/g,"/"))); } catch { return null; } },
  _verifier() {
    const a = new Uint8Array(32); crypto.getRandomValues(a);
    return btoa(String.fromCharCode(...a)).replace(/[+/=]/g, (c) => ({ "+":"-","/":"_","=":"" }[c]));
  },
  async _challenge(cv) {
    const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(cv));
    return btoa(String.fromCharCode(...new Uint8Array(h))).replace(/[+/=]/g, (c) => ({ "+":"-","/":"_","=":"" }[c]));
  },
};

/* ══════════════════════════ API ══════════════════════════ */
const API = {
  base: (CFG.API_BASE_URL || "").replace(/\/$/, ""),

  async _req(method, path, body) {
    const token = Auth.token();
    if (!token) throw new Error("Sessão expirada. Faça login novamente.");
    const opts = { method, headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` } };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(this.base + path, opts);
    if (r.status === 401) throw new Error("Sessão expirada. Faça login novamente.");
    if (!r.ok) {
      let m = `Erro ${r.status}`;
      try { const e = await r.json(); m = e.error || e.message || m; } catch {}
      throw new Error(m);
    }
    return r.status === 204 ? null : r.json();
  },

  tasks()            { return this._req("GET",    "/v1/tasks"); },
  users()            { return this._req("GET",    "/v1/users"); },
  create(d)          { return this._req("POST",   "/v1/tasks", d); },
  update(id, d)      { return this._req("PUT",    `/v1/tasks/${id}`, d); },
  remove(id)         { return this._req("DELETE", `/v1/tasks/${id}`); },
};

/* ══════════════════════════ Toast ══════════════════════════ */
const Toast = {
  _timer: null,

  show(msg, kind = "error") {
    const text = String(msg ?? "").trim();
    if (!text) return;
    const el = $("toast"), m = $("toastMsg"), i = $("toastIcon");
    if (!el || !m) return;
    m.textContent = text;
    if (i) i.textContent = kind === "success" ? "✓" : "⚠";
    el.classList.toggle("toast--success", kind === "success");
    el.hidden = false;
    clearTimeout(this._timer);
    this._timer = setTimeout(() => this.hide(), kind === "success" ? 3000 : 6000);
  },

  hide() {
    const el = $("toast"), m = $("toastMsg");
    if (el) el.hidden = true;
    if (m)  m.textContent = "";
    clearTimeout(this._timer);
  },
};

/* ══════════════════════════ Theme ══════════════════════════ */
const Theme = {
  init() {
    const saved = localStorage.getItem("tm_theme") || "light";
    document.documentElement.dataset.theme = saved;
    $("themeToggle")?.addEventListener("click", () => this.toggle());
  },
  toggle() {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("tm_theme", next);
  },
};

/* ══════════════════════════ Board ══════════════════════════ */
const Board = {
  tasks: [],
  users: [],
  dragId: null,

  init() {
    STATUSES.forEach((s) => {
      const list = $(`list-${s}`);
      if (!list) return;
      list.addEventListener("dragover",  (e) => { e.preventDefault(); list.classList.add("is-over"); });
      list.addEventListener("dragleave", ()  => list.classList.remove("is-over"));
      list.addEventListener("drop",      (e) => this._onDrop(e, s, list));
    });
  },

  async load() {
    const [tRes, uRes] = await Promise.allSettled([API.tasks(), API.users()]);

    if (tRes.status === "fulfilled") {
      this.tasks = tRes.value?.tasks || [];
    } else {
      Toast.show(tRes.reason?.message || "Falha ao carregar tarefas");
      this.tasks = [];
    }
    this.users = uRes.status === "fulfilled" ? (uRes.value?.users || []) : [];

    this.render();
  },

  render() {
    const counts = { pending: 0, in_progress: 0, done: 0 };

    STATUSES.forEach((status) => {
      const list = $(`list-${status}`);
      if (!list) return;
      const items = this.tasks.filter((t) => t.status === status);
      counts[status] = items.length;

      const badge = $(`count-${status}`);
      if (badge) badge.textContent = items.length;

      if (!items.length) {
        list.innerHTML = `<div class="empty">
            <div class="empty__icon">${EMPTY[status].icon}</div>
            <div class="empty__text">${EMPTY[status].text}</div>
          </div>`;
        return;
      }

      list.innerHTML = items.map((t, i) => this._card(t, i)).join("");
      list.querySelectorAll(".task").forEach((el) => {
        el.addEventListener("click", () => {
          const t = this.tasks.find((x) => x.task_id === el.dataset.id);
          if (t) Modal.openEdit(t);
        });
        el.addEventListener("dragstart", () => { this.dragId = el.dataset.id; el.classList.add("is-dragging"); });
        el.addEventListener("dragend",   () => { el.classList.remove("is-dragging"); this.dragId = null; });
      });
    });

    // Metrics
    const total = this.tasks.length;
    const set = (id, v) => { const e = $(id); if (e) e.textContent = v; };
    set("mPending",  counts.pending);
    set("mProgress", counts.in_progress);
    set("mDone",     counts.done);
    set("mTotal",    total);

    const sub = $("pageSubtitle");
    if (sub) {
      sub.textContent = total === 0
        ? "Comece criando sua primeira tarefa"
        : `${total} tarefa${total > 1 ? "s" : ""} no quadro · ${counts.done} concluída${counts.done !== 1 ? "s" : ""}`;
    }
  },

  _card(t, idx) {
    const u = this.users.find((x) => x.user_id === t.assignee_id);
    const uName = u ? (u.name && u.name !== u.email ? u.name : (u.email || "").split("@")[0]) : null;

    let dueHtml = "";
    if (t.due_date) {
      const due = new Date(t.due_date + "T23:59:59");
      const overdue = due < new Date() && t.status !== "done";
      const fmt = due.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
      dueHtml = `<span class="pill${overdue ? " pill--overdue" : ""}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        ${esc(fmt)}</span>`;
    }

    return `<div class="task" draggable="true" data-id="${esc(t.task_id)}" role="button" tabindex="0"
      style="animation-delay:${idx * 40}ms" aria-label="Tarefa ${esc(t.title)}">
      <div class="task__top">
        <span class="task__title">${esc(t.title)}</span>
        <span class="chip chip--${esc(t.priority)}">${esc(PRIORITY_LABEL[t.priority] || t.priority)}</span>
      </div>
      ${t.description ? `<p class="task__desc">${esc(t.description)}</p>` : ""}
      ${(uName || dueHtml || t.effort_estimate != null) ? `<div class="task__meta">
        ${uName ? `<span class="pill pill--user"><span class="pill__avatar">${esc(uName[0].toUpperCase())}</span>${esc(uName)}</span>` : ""}
        ${dueHtml}
        ${t.effort_estimate != null ? `<span class="pill">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          ${esc(t.effort_estimate)}h</span>` : ""}
      </div>` : ""}
    </div>`;
  },

  async _onDrop(e, status, list) {
    e.preventDefault();
    list.classList.remove("is-over");
    const id = this.dragId;
    if (!id) return;
    const t = this.tasks.find((x) => x.task_id === id);
    if (!t || t.status === status) return;
    const prev = t.status;
    t.status = status;
    this.render();
    try {
      await API.update(id, { status });
      Toast.show("Tarefa movida", "success");
    } catch (err) {
      t.status = prev;
      this.render();
      Toast.show(err.message || "Falha ao mover tarefa");
    }
  },
};

/* ══════════════════════════ Modal ══════════════════════════ */
const Modal = {
  init() {
    document.querySelectorAll("[data-close]").forEach((el) =>
      el.addEventListener("click", () => this.close()));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !$("modal")?.hidden) this.close();
    });
    $("form")?.addEventListener("submit", (e) => { e.preventDefault(); this._save(); });
    $("newTaskBtn")?.addEventListener("click", () => this.openNew());
    // Delete button — uses custom confirm dialog
    $("deleteBtn")?.addEventListener("click", () => {
      const btn = $("deleteBtn");
      const id    = btn?.dataset.taskId;
      const title = btn?.dataset.taskTitle || "esta tarefa";
      if (!id) return;
      const msg = $("confirmMsg");
      if (msg) msg.textContent = `"${title}" será excluída permanentemente.`;
      const dlg = $("confirmDelete");
      if (dlg) dlg.hidden = false;
      document.body.style.overflow = "hidden";
    });
    $("confirmCancel")?.addEventListener("click", () => {
      const dlg = $("confirmDelete");
      if (dlg) dlg.hidden = true;
      document.body.style.overflow = "";
    });
    $("confirmOk")?.addEventListener("click", async () => {
      const dlg = $("confirmDelete");
      if (dlg) dlg.hidden = true;
      document.body.style.overflow = "";
      const id = $("deleteBtn")?.dataset.taskId;
      if (!id) return;
      const okBtn = $("confirmOk");
      if (okBtn) { okBtn.disabled = true; okBtn.textContent = "Excluindo…"; }
      try {
        await API.remove(id);
        this.close();
        Toast.show("Tarefa excluída", "success");
        await Board.load();
      } catch (err) {
        Toast.show(err.message || "Falha ao excluir tarefa");
      } finally {
        if (okBtn) { okBtn.disabled = false; okBtn.textContent = "Sim, excluir"; }
      }
    });
  },

  openNew() {
    $("modalTitle").textContent = "Nova Tarefa";
    $("form").reset();
    $("fId").value = "";
    $("fStatus").value = "pending";
    $("fPriority").value = "medium";
    this._assignees(null);
    // Hide delete button in new mode
    const del = $("deleteBtn");
    if (del) { del.hidden = true; del.dataset.taskId = ""; }
    this._open();
  },

  openEdit(t) {
    $("modalTitle").textContent = "Editar Tarefa";
    $("fId").value       = t.task_id;
    $("fTitle").value    = t.title || "";
    $("fDesc").value     = t.description || "";
    $("fPriority").value = t.priority || "medium";
    $("fStatus").value   = t.status || "pending";
    $("fDue").value      = t.due_date || "";
    $("fEffort").value   = t.effort_estimate ?? "";
    this._assignees(t.assignee_id);
    // Show delete button in edit mode
    const del = $("deleteBtn");
    if (del) { del.hidden = false; del.dataset.taskId = t.task_id; del.dataset.taskTitle = t.title; }
    this._open();
  },

  _open() {
    const m = $("modal");
    if (m) m.hidden = false;
    document.body.style.overflow = "hidden";
    requestAnimationFrame(() => $("fTitle")?.focus());
  },

  close() {
    const m = $("modal");
    if (m) m.hidden = true;
    document.body.style.overflow = "";
    $("form")?.reset();
    // Hide delete button when modal closes
    const del = $("deleteBtn");
    if (del) { del.hidden = true; del.dataset.taskId = ""; }
  },

  _assignees(selected) {
    const sel = $("fAssignee");
    if (!sel) return;
    sel.innerHTML = `<option value="">Não atribuído</option>` +
      Board.users.map((u) => {
        const label = (u.name && u.name !== u.email ? u.name : (u.email || "").split("@")[0]) || u.user_id;
        return `<option value="${esc(u.user_id)}"${u.user_id === selected ? " selected" : ""}>${esc(label)}</option>`;
      }).join("");
  },

  async _save() {
    const title = $("fTitle").value.trim();
    if (!title) { $("fTitle").focus(); Toast.show("O título é obrigatório"); return; }

    const id = $("fId").value;
    const effort = $("fEffort").value;
    const payload = {
      title,
      description:     $("fDesc").value.trim() || null,
      priority:        $("fPriority").value,
      status:          $("fStatus").value,
      assignee_id:     $("fAssignee").value || null,
      due_date:        $("fDue").value || null,
      effort_estimate: effort !== "" ? parseFloat(effort) : null,
    };

    const btn = $("saveBtn");
    if (btn) { btn.disabled = true; btn.textContent = "Salvando…"; }

    try {
      if (id) await API.update(id, payload);
      else    await API.create(payload);
      this.close();
      Toast.show(id ? "Tarefa atualizada" : "Tarefa criada", "success");
      await Board.load();
    } catch (err) {
      Toast.show(err.message || "Falha ao salvar tarefa");
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = "Salvar Tarefa"; }
    }
  },
};

/* ══════════════════════════ Bootstrap ══════════════════════════ */
function reveal() {
  const splash = $("splash"), app = $("app");
  if (splash) splash.hidden = true;
  if (app)    app.hidden    = false;
}

async function boot() {
  console.log("[TM] boot start", { hasCode: location.search.includes("code="), cfg: CFG });
  Theme.init();
  $("toastClose")?.addEventListener("click", () => Toast.hide());

  // OAuth callback
  if (location.search.includes("code=")) {
    console.log("[TM] handling OAuth callback");
    const ok = await Auth.handleCallback();
    console.log("[TM] callback result:", ok);
    if (!ok) {
      reveal();
      Toast.show("Falha na autenticação. Redirecionando para login…");
      setTimeout(() => Auth.login(), 2000);
      return;
    }
  }

  const authed = Auth.ok();
  console.log("[TM] authenticated:", authed);
  if (!authed) {
    console.log("[TM] redirecting to Cognito login");
    await Auth.login();
    return;
  }

  // User chip
  const u = Auth.user();
  if (u) {
    const name = u.name || u.email || "";
    const nameEl = $("userName"), avEl = $("userAvatar");
    if (nameEl) nameEl.textContent = name;
    if (avEl)   avEl.textContent   = (name[0] || "?").toUpperCase();
  }

  Board.init();
  Modal.init();
  $("logoutBtn")?.addEventListener("click", () => Auth.logout());

  console.log("[TM] revealing app");
  reveal();

  await Board.load();
  console.log("[TM] board loaded", { tasks: Board.tasks.length, users: Board.users.length });
}

function start() {
  console.log("[TM] DOM ready, starting…");
  // Failsafe: never leave the user stuck on the splash
  const failsafe = setTimeout(() => {
    console.warn("[TM] failsafe fired — revealing app after timeout");
    reveal();
  }, 8000);

  boot()
    .then(() => clearTimeout(failsafe))
    .catch((e) => {
      clearTimeout(failsafe);
      console.error("[TM] boot error:", e);
      reveal();
      Toast.show("Erro ao inicializar: " + (e?.message || e));
    });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start);
} else {
  start();
}
