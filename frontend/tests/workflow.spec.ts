import { test, expect } from "@playwright/test";
import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
const local = existsSync(resolve("../runtime/local-account.txt"))
  ? readFileSync(resolve("../runtime/local-account.txt"), "utf8")
  : "";
const username =
  process.env.DEMO_USERNAME || local.match(/Username: (.+)/)![1].trim();
const password =
  process.env.DEMO_PASSWORD || local.match(/Password: (.+)/)![1].trim();
test.beforeEach(async ({ page }, testInfo) => {
  if (!testInfo.title.startsWith("welcome notice"))
    await page.addInitScript(() =>
      sessionStorage.setItem("bg_welcome_seen", "1"),
    );
});

test("welcome notice shows local access and leads to working login", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "ভূমিগার্ডে স্বাগতম" }),
  ).toBeVisible();
  await expect(page.getByRole("textbox")).toHaveCount(0);
  await page.getByRole("button", { name: "English", exact: true }).click();
  await expect(page.locator(".welcome-credentials")).toContainText(username);
  await expect(page.locator(".welcome-credentials")).toContainText(password);
  await page.screenshot({
    path: "test-results/welcome-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.getByRole("button", { name: "I've read this — continue" }).click();
  await page.getByLabel("Reviewer username", { exact: true }).fill(username);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in →", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "A clearer view of every transaction." }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "A clearer view of every transaction." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "About this demo" }).click();
  await expect(
    page.getByRole("heading", { name: "Welcome to BhumiGuard" }),
  ).toBeVisible();
});
test("geography coverage and missing mouzas stay honest in both languages", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "English", exact: true }).click();
  await page.getByLabel("Reviewer username", { exact: true }).fill(username);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in →", exact: true }).click();
  await page
    .getByRole("button", { name: "＋ New review", exact: true })
    .last()
    .click();
  await expect(
    page
      .getByRole("combobox", { name: "District", exact: true })
      .locator("option"),
  ).toHaveCount(64);
  await page
    .getByRole("combobox", { name: "District", exact: true })
    .selectOption("loc-chattogram");
  await expect(
    page
      .getByRole("combobox", { name: "Upazila", exact: true })
      .locator("option"),
  ).toHaveCount(16);
  await page
    .getByRole("combobox", { name: "Upazila", exact: true })
    .selectOption("loc-chattogram-anwara");
  await expect(page.getByRole("status")).toContainText("No verified mouzas");
  await page.screenshot({
    path: "test-results/geography-coverage.png",
    fullPage: true,
  });
  await expect(
    page
      .getByRole("combobox", { name: "Mouza", exact: true })
      .locator("option"),
  ).toHaveCount(1);
  await page.getByRole("checkbox").check();
  await expect(
    page.getByRole("button", { name: "Create review" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "বাংলা", exact: true }).click();
  await expect(
    page.getByRole("combobox", { name: "জেলা", exact: true }),
  ).toHaveValue("loc-chattogram");
  await expect(page.getByRole("status")).toContainText("যাচাইকৃত মৌজার তথ্য");
  await page.getByRole("button", { name: "English", exact: true }).click();
  await page
    .getByRole("combobox", { name: "District", exact: true })
    .selectOption("loc-dhaka");
  await page
    .getByRole("combobox", { name: "Upazila", exact: true })
    .selectOption("loc-savar");
  await page
    .getByRole("combobox", { name: "Mouza", exact: true })
    .selectOption("loc-birulia");
  await expect(
    page.getByRole("button", { name: "Create review" }),
  ).toBeEnabled();
});
for (const lang of ["en", "bn"])
  test("complete workflow " + lang, async ({ page }) => {
    await page.goto("/");
    if (lang === "en")
      await page.getByRole("button", { name: "English", exact: true }).click();
    await page
      .getByLabel(
        lang === "en" ? "Reviewer username" : "পর্যালোচকের ব্যবহারকারীর নাম",
        { exact: true },
      )
      .fill(username);
    await page
      .getByLabel(lang === "en" ? "Password" : "পাসওয়ার্ড", { exact: true })
      .fill(password);
    await page
      .getByRole("button", { name: lang === "en" ? "Sign in" : "প্রবেশ করুন" })
      .click();
    await page
      .getByRole("button", {
        name: lang === "en" ? "＋ New review" : "＋ নতুন পর্যালোচনা",
        exact: true,
      })
      .last()
      .click();
    await page
      .getByRole("combobox", {
        name: lang === "en" ? "Scenario" : "পরিস্থিতি",
        exact: true,
      })
      .selectOption("correction");
    await page.getByRole("checkbox").check();
    await page
      .getByRole("button", {
        name: lang === "en" ? "Create review" : "পর্যালোচনা তৈরি করুন",
      })
      .click();
    await page
      .getByLabel(
        lang === "en"
          ? "Proposed area (decimal / shotok)"
          : "প্রস্তাবিত পরিমাণ (শতক)",
        { exact: true },
      )
      .fill("১২১");
    await page
      .getByRole("button", {
        name: lang === "en" ? "বাংলা" : "English",
        exact: true,
      })
      .click();
    await expect(
      page.getByLabel(
        lang === "en"
          ? "প্রস্তাবিত পরিমাণ (শতক)"
          : "Proposed area (decimal / shotok)",
        { exact: true },
      ),
    ).toHaveValue("১২১");
    await page
      .getByRole("button", {
        name: lang === "en" ? "English" : "বাংলা",
        exact: true,
      })
      .click();
    await page.getByRole("checkbox").first().check();
    await page
      .getByRole("button", {
        name: lang === "en" ? "Save fields" : "তথ্য সংরক্ষণ করুন",
        exact: true,
      })
      .click();
    await expect(page.getByRole("status")).toContainText(
      lang === "en" ? "Saved successfully" : "সফলভাবে সংরক্ষিত",
    );
    await page
      .getByRole("button", {
        name: lang === "en" ? "Continue to analysis" : "বিশ্লেষণে যান",
      })
      .click();
    await page
      .getByRole("button", {
        name:
          lang === "en"
            ? "Run deterministic checks"
            : "নিয়মভিত্তিক যাচাই চালান",
      })
      .click();
    await expect(page.locator(".analysis-banner")).toContainText(
      lang === "en" ? "Conflict detected" : "অমিল শনাক্ত হয়েছে",
    );
    await expect(page.locator(".finding")).toContainText("EXCESS_AREA");
    await page.locator(".finding .source-links button").first().click();
    await expect(page.locator(".document-viewer img")).toBeVisible();
    await page
      .getByLabel(
        lang === "en"
          ? "Proposed area (decimal / shotok)"
          : "প্রস্তাবিত পরিমাণ (শতক)",
        { exact: true },
      )
      .fill("২০");
    await page.getByRole("checkbox").first().check();
    await page
      .getByRole("button", {
        name: lang === "en" ? "Save fields" : "তথ্য সংরক্ষণ করুন",
        exact: true,
      })
      .click();
    await expect(page.getByRole("status")).toContainText(
      lang === "en" ? "Saved successfully" : "সফলভাবে সংরক্ষিত",
    );
    await page
      .getByRole("button", {
        name: lang === "en" ? "Continue to analysis" : "বিশ্লেষণে যান",
      })
      .click();
    await expect(page.locator(".analysis-banner")).toContainText(
      lang === "en" ? "Fields or evidence changed" : "তথ্য বা প্রমাণ বদলেছে",
    );
    await page
      .getByRole("button", {
        name:
          lang === "en"
            ? "Run deterministic checks"
            : "নিয়মভিত্তিক যাচাই চালান",
      })
      .click();
    await expect(page.locator(".analysis-banner")).toContainText(
      lang === "en" ? "No conflict found" : "কোনো অমিল পাওয়া যায়নি",
    );
    await page.locator(".tabs button").nth(2).click();
    await page
      .getByLabel(
        lang === "en" ? "Reviewer explanation" : "পর্যালোচকের ব্যাখ্যা",
        { exact: true },
      )
      .fill("Demo review: corrected area and checked supplied records.");
    await page
      .getByRole("button", {
        name: lang === "en" ? "Record decision" : "সিদ্ধান্ত সংরক্ষণ করুন",
        exact: true,
      })
      .click();
    await expect(page.locator(".decision")).toContainText(
      "Demo review: corrected area",
    );
    await page.reload();
    await page.locator(".tabs button").nth(2).click();
    await expect(page.locator(".decision")).toContainText(
      "Demo review: corrected area",
    );
    await expect(page.locator(".audit-item")).toHaveCount(6);
    await page.screenshot({
      path: `test-results/history-${lang}.png`,
      fullPage: true,
    });
  });
test("API failure preserves fields and responsive dashboard", async ({
  page,
}) => {
  // A slow initial catalog must not overwrite navigation after login.
  await page.route("**/api/locations", async (route) => {
    const response = await route.fetch();
    await new Promise((resolve) => setTimeout(resolve, 300));
    await route.fulfill({ response });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "English", exact: true }).click();
  await page.getByLabel("Reviewer username", { exact: true }).fill(username);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page
    .getByRole("button", { name: "＋ New review", exact: true })
    .last()
    .click();
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Create review" }).click();
  await page
    .getByLabel("Proposed area (decimal / shotok)", { exact: true })
    .fill("33");
  await page.route("**/api/cases/*/fields", (route) => route.abort());
  await page.getByRole("button", { name: "Save fields", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Cannot reach the server",
  );
  await expect(
    page.getByLabel("Proposed area (decimal / shotok)", { exact: true }),
  ).toHaveValue("33");
  await page.getByRole("button", { name: "Back to queue" }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "test-results/mobile-dashboard.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
});
test("fictional PDF upload, unavailable extraction and manual review", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "English", exact: true }).click();
  await page.getByLabel("Reviewer username", { exact: true }).fill(username);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page
    .getByRole("button", { name: "＋ New review", exact: true })
    .last()
    .click();
  await page
    .getByRole("combobox", { name: "Scenario", exact: true })
    .selectOption("");
  await page.getByRole("checkbox").check();
  await page
    .locator("input[type=file]")
    .setInputFiles(resolve("../sample-documents/DEMO-valid.pdf"));
  await page.getByRole("button", { name: "Create review" }).click();
  await expect(page.locator(".document-viewer iframe")).toBeVisible();
  await page
    .getByRole("button", {
      name: "Send document for live extraction",
      exact: true,
    })
    .click();
  await expect(page.getByRole("alert")).toContainText(
    "Live extraction is unavailable",
  );
  for (const [label, value] of [
    ["Seller party reference", "DEMO-PARTY-A"],
    ["Holding reference", "DEMO-HOLDING"],
    ["Survey context", "DEMO-RS"],
    ["Dag reference", "DEMO-DAG-17"],
    ["Proposed area (decimal / shotok)", "20"],
    ["Proposed transaction date", "2026-09-01"],
  ])
    await page.getByLabel(label, { exact: true }).fill(value);
  await page.getByRole("checkbox").first().check();
  await page.getByRole("button", { name: "Save fields", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Saved successfully");
  await page.getByRole("button", { name: "Continue to analysis" }).click();
  await page.getByRole("button", { name: "Run deterministic checks" }).click();
  await expect(page.locator(".analysis-banner")).toContainText(
    "Insufficient information",
  );
  await expect(page.locator(".finding")).toContainText("MISSING_INFORMATION");
  await page.screenshot({
    path: "test-results/manual-analysis.png",
    fullPage: true,
  });
  await page.emulateMedia({ media: "print" });
  await expect(page.locator(".print-report")).toBeVisible();
  await expect(page.locator(".print-report")).toContainText(
    "DEMO — FICTIONAL DATA — NOT AN OFFICIAL DOCUMENT",
  );
  await expect(page.locator(".print-report")).toContainText(
    "পর্যালোচনার সারাংশ",
  );
  await expect(page.locator(".print-report")).toContainText("Review summary");
  await page.screenshot({
    path: "test-results/bilingual-print.png",
    fullPage: true,
  });
});
