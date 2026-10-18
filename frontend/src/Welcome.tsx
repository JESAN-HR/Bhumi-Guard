import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

function safeGithub(url: unknown): string | undefined {
  if (typeof url !== "string") return;
  try {
    const parsed = new URL(url);
    if (
      parsed.protocol === "https:" &&
      parsed.hostname === "github.com" &&
      !parsed.username &&
      !parsed.password
    )
      return parsed.href;
  } catch {
    /* Unconfigured links are shown as text, never invented. */
  }
}

export default function Welcome({ onContinue }: { onContinue: () => void }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === "bn" ? "bn" : "en";
  const [info, setInfo] = useState<any>(null);
  const [failed, setFailed] = useState(false);
  async function load() {
    setFailed(false);
    try {
      const response = await fetch("/api/welcome");
      if (!response.ok) throw new Error();
      setInfo(await response.json());
    } catch {
      setFailed(true);
    }
  }
  useEffect(() => {
    void load();
  }, []);
  return (
    <section className="welcome-scene" aria-labelledby="welcome-title">
      <div className="welcome-glass">
        <div className="welcome-kicker">{t("welcomeKicker")}</div>
        <div className="welcome-symbol" aria-hidden="true">
          ভূ
        </div>
        <h1 id="welcome-title">{t("welcomeTitle")}</h1>
        <p className="welcome-lead">{t("welcomeLead")}</p>
        <div className="welcome-details">
          <div>
            <span>{t("teamLabel")}</span>
            <strong>{info?.team?.[lang] || t("brand")}</strong>
          </div>
          <div>
            <span>{t("contestLabel")}</span>
            <strong>{info?.contest?.[lang] || t("contestName")}</strong>
          </div>
          <div>
            <span>{t("challengeLabel")}</span>
            <strong>{t("challengeName")}</strong>
          </div>
        </div>
        <div className="welcome-columns">
          <section className="welcome-inset">
            <h2>{t("demoAccess")}</h2>
            <p>{t("publicDemoLogin")}</p>
            {info?.login ? (
              <dl className="welcome-credentials">
                <div>
                  <dt>{t("username")}</dt>
                  <dd>{info.login.username}</dd>
                </div>
                <div>
                  <dt>{t("password")}</dt>
                  <dd>{info.login.password}</dd>
                </div>
              </dl>
            ) : (
              <p>
                {failed
                  ? t("welcomeUnavailable")
                  : info
                    ? t("localAccount")
                    : t("busy")}
              </p>
            )}
            {failed && <button onClick={load}>{t("retryWelcome")}</button>}
          </section>
          <section className="welcome-inset">
            <h2>{t("creatorsLabel")}</h2>
            {info?.creators?.length ? (
              info.creators.map((creator: any, index: number) => (
                <div className="welcome-creator" key={index}>
                  <strong>{creator.name?.[lang] || creator.name?.en}</strong>
                  {safeGithub(creator.github_url) && (
                    <a
                      href={safeGithub(creator.github_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {t("githubProfile")} ↗
                    </a>
                  )}
                </div>
              ))
            ) : (
              <p>{t("creatorsPending")}</p>
            )}
            {safeGithub(info?.repository_url) && (
              <a
                href={safeGithub(info.repository_url)}
                target="_blank"
                rel="noopener noreferrer"
              >
                {t("githubRepository")} ↗
              </a>
            )}
          </section>
        </div>
        <p className="welcome-disclaimer">{t("limit")}</p>
        <button className="welcome-continue" onClick={onContinue}>
          {t("ackWelcome")} <span aria-hidden="true">→</span>
        </button>
        <p className="welcome-footnote">{t("welcomeRemember")}</p>
      </div>
    </section>
  );
}
