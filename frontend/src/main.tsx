import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { useTranslation } from "react-i18next";
import i18n from "./i18n";
import Welcome from "./Welcome";
import "@fontsource/noto-sans-bengali/400.css";
import "@fontsource/noto-sans-bengali/600.css";
import "./style.css";

type Row = Record<string, any>;
let csrf = "";
async function api(path: string, method = "GET", body?: unknown) {
  let response: Response;
  try {
    response = await fetch("/api" + path, {
      method,
      credentials: "same-origin",
      headers: {
        ...(body instanceof FormData
          ? {}
          : { "Content-Type": "application/json" }),
        "X-CSRF-Token": csrf,
      },
      body:
        body instanceof FormData
          ? body
          : body === undefined
            ? undefined
            : JSON.stringify(body),
    });
  } catch {
    throw new Error("network");
  }
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      typeof result.detail === "string" ? result.detail : "error",
    );
  return result;
}
function App() {
  const { t } = useTranslation();
  const [welcomed, setWelcomed] = useState(
    () => sessionStorage.getItem("bg_welcome_seen") === "1",
  );
  const lang = i18n.language === "bn" ? "bn" : "en";
  const [user, setUser] = useState<Row | null>(null),
    [ready, setReady] = useState(false),
    [cases, setCases] = useState<Row[]>([]),
    [locations, setLocations] = useState<Row[]>([]),
    [scenarios, setScenarios] = useState<Row[]>([]);
  const [active, setActive] = useState<Row | null>(null),
    [page, setPage] = useState("dashboard"),
    [tab, setTab] = useState("document"),
    [draft, setDraft] = useState<Row>({}),
    [confirmed, setConfirmed] = useState(false),
    [selectedDoc, setSelectedDoc] = useState(""),
    [dirty, setDirty] = useState(false);
  const [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [search, setSearch] = useState(""),
    [filter, setFilter] = useState(""),
    [locationFilter, setLocationFilter] = useState("");
  const [scenario, setScenario] = useState("valid"),
    [district, setDistrict] = useState("loc-dhaka"),
    [upazila, setUpazila] = useState("loc-savar"),
    [mouza, setMouza] = useState("loc-birulia"),
    [fictional, setFictional] = useState(false),
    [file, setFile] = useState<File | null>(null),
    [notes, setNotes] = useState(""),
    [decision, setDecision] = useState("more_information");
  const title = (r: Row) => r.title?.[lang] || r.title?.en || "";
  const loc = (id: string) =>
    locations.find((l) => l.id === id)?.["name_" + lang] || id;
  const districtOf = (mouzaId: string) => {
    const parent = locations.find((l) => l.id === mouzaId)?.parent_id;
    return locations.find((l) => l.id === parent)?.parent_id || "";
  };
  const locationCount = (kind: string) =>
    locations.filter((l) => l.kind === kind).length;
  const time = (s: string) =>
    new Intl.DateTimeFormat(lang === "bn" ? "bn-BD" : "en-GB", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "Asia/Dhaka",
    }).format(new Date(s));
  const num = (n: number) =>
    new Intl.NumberFormat(lang === "bn" ? "bn-BD" : "en-GB").format(n);
  async function act(fn: () => Promise<void>) {
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function accept(c: Row) {
    setActive(c);
    setDraft({ ...c.fields });
    setConfirmed(c.confirmed);
    setDirty(false);
    setSelectedDoc((d) =>
      c.documents.some((x: Row) => x.id === d) ? d : c.documents[0]?.id || "",
    );
    localStorage.setItem("bg_case", c.id);
  }
  async function load() {
    const [c, l, s] = await Promise.all([
      api("/cases"),
      api("/locations"),
      api("/scenarios"),
    ]);
    setCases(c);
    setLocations(l);
    setScenarios(s);
  }
  useEffect(() => {
    api("/me")
      .then(async (u) => {
        csrf = u.csrf;
        await load();
        const id = localStorage.getItem("bg_case");
        if (id) {
          try {
            accept(await api("/cases/" + id));
            setPage("case");
          } catch {
            localStorage.removeItem("bg_case");
          }
        }
        setUser(u);
      })
      .catch(() => {})
      .finally(() => setReady(true));
  }, []);
  useEffect(() => {
    document.documentElement.lang = lang;
    localStorage.setItem("bg_language", lang);
  }, [lang]);
  const latest = active?.analyses.at(-1),
    doc = active?.documents.find((d: Row) => d.id === selectedDoc);
  const open = (id: string) =>
    act(async () => {
      accept(await api("/cases/" + id));
      setPage("case");
      setTab("document");
      setNotes("");
      setFile(null);
      setFictional(false);
    });
  function leave() {
    setPage("dashboard");
    setActive(null);
    localStorage.removeItem("bg_case");
    act(load);
  }
  function newReview() {
    setPage("new");
    setFictional(false);
    setFile(null);
  }
  function sourceLink(id: string) {
    return (
      <button
        className="text-button"
        key={id}
        onClick={() => {
          setSelectedDoc(id);
          setTab("document");
        }}
      >
        {t("source")} ·{" "}
        {active?.documents.find((d: Row) => d.id === id)?.label ||
          id.slice(0, 8)}{" "}
        ↗
      </button>
    );
  }
  function values(data: Row) {
    return (
      <dl className="values">
        {Object.entries(data).map(([k, v]) => (
          <React.Fragment key={k}>
            <dt>{t(k === "record" ? "recordValue" : k)}</dt>
            <dd>
              {Array.isArray(v)
                ? v
                    .map((x) =>
                      t(x === "history" ? "historyMissing" : String(x)),
                    )
                    .join(", ")
                : typeof v === "object" && v !== null
                  ? Object.entries(v)
                      .map(([a, b]) => `${t(a)}: ${b ?? "—"}`)
                      .join(" · ")
                  : String(v ?? "—")}
            </dd>
          </React.Fragment>
        ))}
      </dl>
    );
  }
  function reportValue(v: unknown, l: string): string {
    const tr = (key: string) =>
      i18n.t(key === "history" ? "historyMissing" : key, { lng: l });
    return Array.isArray(v)
      ? v.map((x) => tr(String(x))).join(", ")
      : v && typeof v === "object"
        ? Object.entries(v)
            .map(([key, value]) => tr(key) + ": " + reportValue(value, l))
            .join(" · ")
        : String(v ?? "—");
  }
  function uploadInput() {
    return (
      <>
        <label className="check">
          <input
            type="checkbox"
            checked={fictional}
            onChange={(e) => setFictional(e.target.checked)}
          />
          {t("fictional")}
        </label>
        <label>
          {t("file")}
          <input
            type="file"
            accept="application/pdf,image/png,image/jpeg"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </label>
        <p className="muted text-sm">{t("uploadHelp")}</p>
      </>
    );
  }
  return (
    <>
      <div className="demo-strip">
        ◈ <span>{t("notice")}</span>
      </div>
      <header className="topbar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            if (user) leave();
          }}
        >
          <span className="brandmark">ভূ</span>
          <span>
            {t("brand")}
            <small>{t("tagline")}</small>
          </span>
        </a>
        <div className="header-actions">
          <span className="hackathon">
            LANDTECH 2026 <span> / P3</span>
          </span>
          <div className="language" aria-label="Language">
            <button
              className={lang === "bn" ? "selected" : ""}
              onClick={() => i18n.changeLanguage("bn")}
            >
              বাংলা
            </button>
            <span>|</span>
            <button
              className={lang === "en" ? "selected" : ""}
              onClick={() => i18n.changeLanguage("en")}
            >
              English
            </button>
          </div>
          <button className="text-button" onClick={() => setWelcomed(false)}>
            {t("aboutDemo")}
          </button>
          {user && welcomed && (
            <button
              className="text-button"
              onClick={() =>
                act(async () => {
                  await api("/logout", "POST");
                  setUser(null);
                  setActive(null);
                  localStorage.removeItem("bg_case");
                })
              }
            >
              {t("logout")}
            </button>
          )}
        </div>
      </header>
      <div className="app-shell">
        {user && welcomed && (
          <aside className="sidebar">
            <p className="eyebrow">{t("home")}</p>
            <button
              className={page === "dashboard" ? "nav active" : "nav"}
              onClick={leave}
            >
              <span>▦</span>
              {t("dashboard")}
            </button>
            <button
              className={page === "new" ? "nav active" : "nav"}
              onClick={newReview}
            >
              <span>＋</span>
              {t("newReview")}
            </button>
            <div className="sidebar-bottom">
              <span className="reference-dot" />
              {t("verified")}
              <p>
                {t("district")}: {num(locationCount("district"))}
              </p>
              <p>
                {t("upazila")}: {num(locationCount("upazila"))} · {t("mouza")}:{" "}
                {num(locationCount("mouza"))}
              </p>
              <p>{t("coverageLimit")}</p>
              <small>{t("limit")}</small>
            </div>
          </aside>
        )}
        <main
          className={
            !welcomed ? "welcome-main" : user ? "main" : "main auth-main"
          }
        >
          <div aria-live="polite">
            {error && (
              <div role="alert" className="alert error">
                {t(error, { defaultValue: t("error") })}
              </div>
            )}
            {message && (
              <div role="status" className="alert success">
                {t(message)}
              </div>
            )}
            {busy && (
              <div role="status" className="working">
                {t("busy")}
              </div>
            )}
          </div>
          {!welcomed ? (
            <Welcome
              onContinue={() => {
                sessionStorage.setItem("bg_welcome_seen", "1");
                setWelcomed(true);
              }}
            />
          ) : !ready ? (
            <p>{t("busy")}</p>
          ) : !user ? (
            <section className="login panel">
              <div className="eyebrow">LANDTECH 2026 · P3</div>
              <h1>{t("brand")}</h1>
              <p>{t("intro")}</p>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const d = new FormData(e.currentTarget);
                  act(async () => {
                    const u = await api(
                      "/login",
                      "POST",
                      Object.fromEntries(d),
                    );
                    csrf = u.csrf;
                    await load();
                    setPage("dashboard");
                    setUser(u);
                  });
                }}
              >
                <label>
                  {t("username")}
                  <input autoComplete="username" name="username" required />
                </label>
                <label>
                  {t("password")}
                  <input
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                  />
                </label>
                <button disabled={busy} className="primary">
                  {t("login")} →
                </button>
              </form>
              <p className="muted">{t("localAccount")}</p>
            </section>
          ) : (
            <>
              {page === "dashboard" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">{t("dashboard")}</div>
                      <h1>{t("welcome")}</h1>
                      <p>{t("intro")}</p>
                    </div>
                    <button className="primary" onClick={newReview}>
                      ＋ {t("newReview")}
                    </button>
                  </div>
                  <div className="stats">
                    {[
                      [t("total"), cases.length],
                      [
                        t("awaiting"),
                        cases.filter(
                          (c) =>
                            !["reviewed", "more_information"].includes(
                              c.status,
                            ),
                        ).length,
                      ],
                      [
                        t("reviewed"),
                        cases.filter((c) => c.status === "reviewed").length,
                      ],
                      [
                        t("information"),
                        cases.filter((c) => c.status === "more_information")
                          .length,
                      ],
                    ].map(([label, count]) => (
                      <div className="stat panel" key={String(label)}>
                        <span>{label}</span>
                        <strong>{num(Number(count))}</strong>
                        <span className="stat-line" />
                      </div>
                    ))}
                  </div>
                  <section className="panel queue">
                    <div className="section-heading">
                      <h2>{t("queue")}</h2>
                      <button className="text-button" onClick={() => act(load)}>
                        ↻ {t("refresh")}
                      </button>
                    </div>
                    <div className="filters">
                      <input
                        aria-label={t("search")}
                        placeholder={"⌕  " + t("search")}
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                      />
                      <select
                        aria-label={t("status")}
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                      >
                        <option value="">{t("all")}</option>
                        {[
                          "draft",
                          "confirmed",
                          "analyzed",
                          "reviewed",
                          "more_information",
                        ].map((s) => (
                          <option key={s} value={s}>
                            {t(s)}
                          </option>
                        ))}
                      </select>
                      <select
                        aria-label={t("location")}
                        value={locationFilter}
                        onChange={(e) => setLocationFilter(e.target.value)}
                      >
                        <option value="">{t("allLocations")}</option>
                        {locations
                          .filter((l) => l.kind === "mouza")
                          .map((l) => (
                            <option key={l.id} value={l.id}>
                              {loc(l.id)}
                            </option>
                          ))}
                      </select>
                    </div>
                    <div className="table-wrap">
                      <table>
                        <thead>
                          <tr>
                            {[
                              "case",
                              "location",
                              "status",
                              "created",
                              "open",
                            ].map((h) => (
                              <th key={h}>{t(h)}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {cases
                            .filter(
                              (c) =>
                                (!filter || c.status === filter) &&
                                (!locationFilter ||
                                  c.mouza_id === locationFilter) &&
                                (title(c) + " " + c.id)
                                  .toLowerCase()
                                  .includes(search.toLowerCase()),
                            )
                            .map((c) => (
                              <tr key={c.id}>
                                <td>
                                  <strong>{title(c)}</strong>
                                  <small>
                                    DEMO · {c.id.slice(0, 8).toUpperCase()}
                                  </small>
                                </td>
                                <td>
                                  {loc(c.mouza_id)}
                                  <small>
                                    {t("district")}:{" "}
                                    {loc(districtOf(c.mouza_id))}
                                  </small>
                                </td>
                                <td>
                                  <span className={"badge " + c.status}>
                                    {t(c.status)}
                                  </span>
                                </td>
                                <td className="date-cell">
                                  {time(c.created_at)}
                                </td>
                                <td>
                                  <button
                                    aria-label={t("open") + " " + title(c)}
                                    className="text-button"
                                    onClick={() => open(c.id)}
                                  >
                                    {t("open")} ↗
                                  </button>
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                    {!cases.filter(
                      (c) =>
                        (!filter || c.status === filter) &&
                        (!locationFilter || c.mouza_id === locationFilter) &&
                        (title(c) + " " + c.id)
                          .toLowerCase()
                          .includes(search.toLowerCase()),
                    ).length && <p className="empty">{t("empty")}</p>}
                  </section>
                  <section className="scenario-strip">
                    <div>
                      <h2>{t("scenarios")}</h2>
                      <p>{t("fixture")}</p>
                    </div>
                    {["valid", "excess", "missing-history"].map((id) => (
                      <button
                        className="scenario-card"
                        key={id}
                        onClick={() => {
                          setScenario(id);
                          newReview();
                        }}
                      >
                        <span>
                          {id === "valid" ? "✓" : id === "excess" ? "↗" : "…"}
                        </span>
                        {title(scenarios.find((s) => s.id === id) || {})}
                        <b>→</b>
                      </button>
                    ))}
                  </section>
                </>
              )}
              {page === "new" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">{t("newReview")}</div>
                      <h1>{t("newReview")}</h1>
                      <p>{t("verified")}</p>
                      <p>{t("coverageLimit")}</p>
                    </div>
                  </div>
                  <form
                    className="panel new-form"
                    onSubmit={(e) => {
                      e.preventDefault();
                      act(async () => {
                        let c = await api("/cases", "POST", {
                          scenario_id: scenario || null,
                          mouza_id: mouza,
                          fictional,
                        });
                        if (file) {
                          const body = new FormData();
                          body.set("file", file);
                          body.set("fictional", "true");
                          c = await api(
                            "/cases/" + c.id + "/documents",
                            "POST",
                            body,
                          );
                        }
                        accept(c);
                        setPage("case");
                        setTab("document");
                        setFictional(false);
                        setFile(null);
                        await load();
                      });
                    }}
                  >
                    <div className="form-grid">
                      <label>
                        {t("district")}
                        <select
                          value={district}
                          onChange={(e) => {
                            setDistrict(e.target.value);
                            setUpazila("");
                            setMouza("");
                          }}
                          required
                        >
                          {locations
                            .filter((l) => l.kind === "district")
                            .map((l) => (
                              <option key={l.id} value={l.id}>
                                {loc(l.id)}
                              </option>
                            ))}
                        </select>
                      </label>
                      <label>
                        {t("upazila")}
                        <select
                          value={upazila}
                          onChange={(e) => {
                            setUpazila(e.target.value);
                            setMouza("");
                          }}
                          required
                        >
                          <option value="">{t("choose")}</option>
                          {locations
                            .filter((l) => l.parent_id === district)
                            .map((l) => (
                              <option key={l.id} value={l.id}>
                                {loc(l.id)}
                              </option>
                            ))}
                        </select>
                      </label>
                      <label>
                        {t("mouza")}
                        <select
                          value={mouza}
                          onChange={(e) => setMouza(e.target.value)}
                          required
                        >
                          <option value="">{t("choose")}</option>
                          {locations
                            .filter((l) => l.parent_id === upazila)
                            .map((l) => (
                              <option key={l.id} value={l.id}>
                                {loc(l.id)}
                              </option>
                            ))}
                        </select>
                      </label>
                    </div>
                    {upazila &&
                      !locations.some(
                        (l) => l.kind === "mouza" && l.parent_id === upazila,
                      ) && (
                        <p role="status" className="notice">
                          {t("missingMouzas")}
                        </p>
                      )}
                    <label>
                      {t("scenario")}
                      <select
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                      >
                        <option value="">{t("manual")}</option>
                        {scenarios.map((s) => (
                          <option key={s.id} value={s.id}>
                            {title(s)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <div className="upload-zone">{uploadInput()}</div>
                    <div className="button-row">
                      <button
                        className="primary"
                        disabled={busy || !fictional || !mouza}
                      >
                        {t("create")} →
                      </button>
                      <button type="button" onClick={leave}>
                        {t("cancel")}
                      </button>
                    </div>
                  </form>
                </>
              )}
              {page === "case" && active && (
                <>
                  <button className="text-button back" onClick={leave}>
                    ← {t("back")}
                  </button>
                  <div className="page-heading case-heading">
                    <div>
                      <div className="eyebrow">
                        DEMO · {active.id.slice(0, 8).toUpperCase()}{" "}
                        <span className={"badge " + active.status}>
                          {t(active.status)}
                        </span>
                      </div>
                      <h1>{title(active)}</h1>
                      <p>
                        {loc(active.mouza_id)} · {t("version")}{" "}
                        {num(active.version)} · {time(active.created_at)}
                      </p>
                    </div>
                    <button onClick={() => window.print()}>{t("print")}</button>
                  </div>
                  <nav className="tabs" aria-label={t("case")}>
                    {["document", "analysis", "history"].map((s, n) => (
                      <button
                        key={s}
                        className={tab === s ? "active" : ""}
                        onClick={() => setTab(s)}
                      >
                        <span>{num(n + 1)}</span>
                        {t(s)}
                      </button>
                    ))}
                  </nav>
                  {dirty && <div className="alert warning">{t("unsaved")}</div>}
                  {tab === "document" && (
                    <div className="review-grid">
                      <section className="panel document-panel">
                        <div className="section-heading">
                          <h2>{t("source")}</h2>
                          <span className="badge">DEMO</span>
                        </div>
                        {active.documents.length > 0 ? (
                          <>
                            <label>
                              {t("selectDoc")}
                              <select
                                value={selectedDoc}
                                onChange={(e) => setSelectedDoc(e.target.value)}
                              >
                                {active.documents.map((d: Row) => (
                                  <option key={d.id} value={d.id}>
                                    {d.label}
                                  </option>
                                ))}
                              </select>
                            </label>
                            <div className="document-viewer">
                              {doc?.media_type === "application/pdf" ? (
                                <iframe
                                  title={t("source")}
                                  src={"/api/documents/" + selectedDoc}
                                />
                              ) : (
                                <img
                                  alt={t("source")}
                                  src={"/api/documents/" + selectedDoc}
                                />
                              )}
                            </div>
                            <details>
                              <summary>{t("sourceText")}</summary>
                              <p>
                                {t("sourcePage")}: {doc?.evidence.page || "—"}
                              </p>
                              {doc?.evidence.text?.map(
                                (text: string, n: number) => (
                                  <p className="source-text" key={n}>
                                    {text}
                                  </p>
                                ),
                              )}
                            </details>
                          </>
                        ) : (
                          <p className="empty">{t("noDocument")}</p>
                        )}
                        <details className="upload-details">
                          <summary>{t("upload")}</summary>
                          {uploadInput()}
                          <button
                            disabled={busy || !fictional || !file}
                            onClick={() =>
                              act(async () => {
                                const b = new FormData();
                                b.set("file", file!);
                                b.set("fictional", "true");
                                accept(
                                  await api(
                                    "/cases/" + active.id + "/documents",
                                    "POST",
                                    b,
                                  ),
                                );
                                setFile(null);
                                setFictional(false);
                                setMessage("saved");
                              })
                            }
                          >
                            {t("upload")}
                          </button>
                        </details>
                        {doc && doc.media_type !== "image/svg+xml" && (
                          <div className="extraction-box">
                            <p>{t("extractHelp")}</p>
                            <button
                              disabled={busy}
                              onClick={() =>
                                act(async () => {
                                  accept(
                                    await api(
                                      "/documents/" + doc.id + "/extract",
                                      "POST",
                                    ),
                                  );
                                  setMessage("saved");
                                })
                              }
                            >
                              {t("extract")}
                            </button>
                          </div>
                        )}
                      </section>
                      <section className="panel fields-panel">
                        <div className="section-heading">
                          <h2>{t("fields")}</h2>
                        </div>
                        <div className="extraction-status">
                          ◈{" "}
                          {t(
                            active.extractions.at(-1)?.provider ||
                              "manual_entry",
                          )}
                        </div>
                        <p className="muted">{t("original")}</p>
                        <form
                          onSubmit={(e) => {
                            e.preventDefault();
                            act(async () => {
                              accept(
                                await api(
                                  "/cases/" + active.id + "/fields",
                                  "PUT",
                                  {
                                    fields: draft,
                                    confirmed,
                                    version: active.version,
                                  },
                                ),
                              );
                              setMessage("saved");
                            });
                          }}
                        >
                          <div className="form-grid">
                            {[
                              "seller_id",
                              "holding_id",
                              "survey",
                              "dag",
                              "area",
                              "date",
                            ].map((k) => (
                              <label key={k}>
                                {t(k)}
                                <input
                                  type={k === "date" ? "date" : "text"}
                                  inputMode={
                                    k === "area" ? "decimal" : undefined
                                  }
                                  value={draft[k] || ""}
                                  placeholder={t("unresolved")}
                                  className={!draft[k] ? "unresolved" : ""}
                                  onChange={(e) => {
                                    setDraft({
                                      ...draft,
                                      [k]: e.target.value || null,
                                    });
                                    setConfirmed(false);
                                    setDirty(true);
                                  }}
                                />
                              </label>
                            ))}
                          </div>
                          <label>
                            {t("location")}
                            <input value={loc(active.mouza_id)} readOnly />
                          </label>
                          <label className="check">
                            <input
                              type="checkbox"
                              checked={confirmed}
                              onChange={(e) => {
                                setConfirmed(e.target.checked);
                                setDirty(true);
                              }}
                            />
                            {t("confirm")}
                          </label>
                          <div className="button-row">
                            <button className="primary" disabled={busy}>
                              {t("save")}
                            </button>
                            <button
                              type="button"
                              onClick={() => setTab("analysis")}
                            >
                              {t("goAnalysis")} →
                            </button>
                          </div>
                        </form>
                        <div className="field-note">{t("remaining")}</div>
                        <details>
                          <summary>{t("provenance")}</summary>
                          {locations
                            .find((l) => l.id === active.mouza_id)
                            ?.provenance.sources.map((s: Row) => (
                              <p key={s.id}>
                                <a
                                  target="_blank"
                                  rel="noreferrer"
                                  href={s.url}
                                >
                                  {s.title || s.id} ↗
                                </a>
                              </p>
                            ))}
                        </details>
                      </section>
                    </div>
                  )}
                  {tab === "analysis" && (
                    <>
                      <div
                        className={
                          "analysis-banner " +
                          (latest && !latest.stale && !dirty
                            ? latest.outcome
                            : "insufficient")
                        }
                      >
                        <div>
                          <div className="eyebrow">{t("analysis")}</div>
                          <h2>
                            {latest
                              ? t(
                                  latest.stale || dirty
                                    ? "stale"
                                    : latest.outcome,
                                )
                              : t("noAnalysis")}
                          </h2>
                          <p>{t("limit")}</p>
                        </div>
                        <button
                          className="primary"
                          disabled={busy || !active.confirmed || dirty}
                          onClick={() =>
                            act(async () => {
                              accept(
                                await api(
                                  "/cases/" + active.id + "/analyze",
                                  "POST",
                                ),
                              );
                              setMessage("saved");
                            })
                          }
                        >
                          {t("run")} ↗
                        </button>
                      </div>
                      <div className="analysis-grid">
                        <section>
                          <h2>
                            {t("findings")}{" "}
                            <span className="count">
                              {num(latest?.findings.length || 0)}
                            </span>
                          </h2>
                          {!latest ? (
                            <div className="panel empty">{t("noAnalysis")}</div>
                          ) : (
                            <>
                              {latest.findings.length === 0 && (
                                <div className="panel empty">
                                  {t("noFindings")}
                                </div>
                              )}
                              {latest.findings.map((f: Row) => (
                                <article
                                  key={f.id}
                                  className={"panel finding " + f.priority}
                                >
                                  <div className="section-heading">
                                    <code>{f.code}</code>
                                    <span className={"badge " + f.priority}>
                                      {t(f.priority + "Priority")}
                                    </span>
                                  </div>
                                  <h3>{f.explanation[lang]}</h3>
                                  {values(f.values)}
                                  <h4>{t("evidence")}</h4>
                                  <div className="source-links">
                                    {f.sources.map(sourceLink)}
                                  </div>
                                  <h4>{t("action")}</h4>
                                  <p>{f.action[lang]}</p>
                                  <p className="muted">{f.assumptions[lang]}</p>
                                </article>
                              ))}
                            </>
                          )}
                        </section>
                        <aside>
                          <section className="panel timeline">
                            <h2>{t("timeline")}</h2>
                            {active.transfers.length ? (
                              active.transfers.map((tr: Row) => (
                                <div className="timeline-item" key={tr.id}>
                                  <span className="timeline-dot" />
                                  <small>{tr.date}</small>
                                  <h3>
                                    {t(tr.status)}{" "}
                                    <span className="badge">{tr.area}</span>
                                  </h3>
                                  <small>DEMO · {tr.id.slice(0, 8)}</small>
                                  {sourceLink(tr.document_id)}
                                </div>
                              ))
                            ) : (
                              <p>{t("noTransfers")}</p>
                            )}
                            <div className="timeline-item proposed">
                              <span className="timeline-dot" />
                              <small>{active.fields.date || "—"}</small>
                              <h3>
                                {t("proposed_area")}:{" "}
                                {active.fields.area || "—"}
                              </h3>
                            </div>
                            <p className="muted">
                              {t(
                                active.holding?.history_complete
                                  ? "historyComplete"
                                  : "historyIncomplete",
                              )}
                            </p>
                          </section>
                          <section className="panel holding">
                            <h2>{t("record")}</h2>
                            {active.holding ? (
                              values({
                                holder: active.holding.party_id,
                                holding_area: active.holding.area,
                                survey: active.holding.survey,
                                dag: active.holding.dag,
                              })
                            ) : (
                              <p>{t("missing")}</p>
                            )}
                          </section>
                        </aside>
                      </div>
                    </>
                  )}
                  {tab === "history" && (
                    <div className="history-grid">
                      <section>
                        <div className="panel">
                          <h2>{t("decision")}</h2>
                          {(!latest || latest.stale || dirty) && (
                            <p className="alert warning">{t("stale")}</p>
                          )}
                          <label>
                            {t("action")}
                            <select
                              value={decision}
                              onChange={(e) => setDecision(e.target.value)}
                            >
                              <option value="more_information">
                                {t("requestAction")}
                              </option>
                              <option value="reviewed">
                                {t("reviewAction")}
                              </option>
                            </select>
                          </label>
                          <label>
                            {t("notes")}
                            <textarea
                              rows={5}
                              value={notes}
                              onChange={(e) => setNotes(e.target.value)}
                              minLength={5}
                              maxLength={5000}
                            />
                          </label>
                          <button
                            className="primary"
                            disabled={
                              busy ||
                              dirty ||
                              !latest ||
                              latest.stale ||
                              notes.trim().length < 5
                            }
                            onClick={() =>
                              act(async () => {
                                accept(
                                  await api(
                                    "/cases/" + active.id + "/decisions",
                                    "POST",
                                    {
                                      analysis_id: latest.id,
                                      action: decision,
                                      notes,
                                    },
                                  ),
                                );
                                setNotes("");
                                setMessage("saved");
                              })
                            }
                          >
                            {t("decision")}
                          </button>
                          <p className="muted">{t("limit")}</p>
                        </div>
                        <h2>{t("history")}</h2>
                        {active.decisions.length ? (
                          active.decisions.map((d: Row) => (
                            <div className="panel decision" key={d.id}>
                              <span className="badge">{t(d.action)}</span>
                              <small>{time(d.created_at)}</small>
                              <p className="notes">{d.notes}</p>
                              <small>
                                {t("analysis")} · {d.analysis_id.slice(0, 8)}
                              </small>
                            </div>
                          ))
                        ) : (
                          <p>{t("noDecisions")}</p>
                        )}
                        <section className="panel">
                          <h2>{t("versions")}</h2>
                          {active.analyses.map((r: Row) => (
                            <details key={r.id}>
                              <summary>
                                {t("version")} {num(r.version)} · {t(r.outcome)}{" "}
                                · {time(r.created_at)}{" "}
                                {r.stale ? " — " + t("stale") : ""}
                              </summary>
                              {r.findings.map((f: Row) => (
                                <p key={f.id}>
                                  {f.code}: {f.explanation[lang]}
                                </p>
                              ))}
                            </details>
                          ))}
                        </section>
                      </section>
                      <section className="panel">
                        <h2>{t("audit")}</h2>
                        {active.audit.map((a: Row) => (
                          <div className="audit-item" key={a.id}>
                            <span className="reference-dot" />
                            <div>
                              <strong>
                                {t(
                                  a.event === "created"
                                    ? "createdEvent"
                                    : a.event,
                                )}
                              </strong>
                              <small>{time(a.created_at)}</small>
                            </div>
                          </div>
                        ))}
                        <h2>{t("changes")}</h2>
                        {active.corrections.map((c: Row) => (
                          <details key={c.id}>
                            <summary>
                              {t("version")} {num(c.version)} ·{" "}
                              {time(c.created_at)}
                            </summary>
                            {values(c.after)}
                          </details>
                        ))}
                      </section>
                    </div>
                  )}
                  <article className="print-report">
                    <div className="watermark">
                      DEMO — FICTIONAL DATA — NOT AN OFFICIAL DOCUMENT
                    </div>
                    <h1>ভূমিগার্ড / BhumiGuard</h1>
                    <h2>{t("reportBilingual")}</h2>
                    <p>
                      {active.title.bn} / {active.title.en}
                    </p>
                    <p>DEMO {active.id}</p>
                    <p>
                      {loc(active.mouza_id)} · {time(active.created_at)}
                    </p>
                    {["bn", "en"].map((l) => (
                      <section key={l}>
                        <h2>{i18n.t("report", { lng: l })}</h2>
                        <p>{i18n.t("notice", { lng: l })}</p>
                        <p>{i18n.t("limit", { lng: l })}</p>
                        <h3>
                          {i18n.t(
                            latest
                              ? latest.stale || dirty
                                ? "stale"
                                : latest.outcome
                              : "noAnalysis",
                            { lng: l },
                          )}
                        </h3>
                        {Object.entries(active.fields).map(([k, v]) => (
                          <p key={k}>
                            {i18n.t(k, { lng: l })}:{" "}
                            {k === "unit"
                              ? i18n.t("decimal", { lng: l })
                              : String(v ?? "—")}
                          </p>
                        ))}
                        {latest?.findings.map((f: Row) => (
                          <div key={f.id}>
                            <h4>
                              {f.code}: {f.explanation[l]}
                            </h4>
                            <p>{f.action[l]}</p>
                            {Object.entries(f.values).map(([key, value]) => (
                              <p key={key}>
                                {i18n.t(
                                  key === "record" ? "recordValue" : key,
                                  { lng: l },
                                )}
                                : {reportValue(value, l)}
                              </p>
                            ))}
                            <p>
                              {f.sources
                                .map(
                                  (id: string) =>
                                    active.documents.find(
                                      (d: Row) => d.id === id,
                                    )?.label +
                                    " [" +
                                    id +
                                    "]",
                                )
                                .join("; ")}
                            </p>
                          </div>
                        ))}
                        {active.decisions.map((d: Row) => (
                          <p key={d.id}>
                            {i18n.t(d.action, { lng: l })}: {d.notes}
                          </p>
                        ))}
                      </section>
                    ))}
                    <p>{t("reportNotes")}</p>
                    <div className="watermark">
                      DEMO — FICTIONAL DATA — NOT AN OFFICIAL DOCUMENT
                    </div>
                  </article>
                </>
              )}
            </>
          )}
          <footer>
            <span>BHUMIGUARD / ভূমিগার্ড</span>
            <p>{t("limit")}</p>
          </footer>
        </main>
      </div>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
