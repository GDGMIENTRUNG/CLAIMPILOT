import { test, expect } from "@playwright/test";

test("real backend is reachable through Vite and missing credentials fail honestly", async ({
  page,
  request,
}) => {
  const health = await request.get("http://127.0.0.1:8000/api/health");
  expect(health.ok()).toBeTruthy();
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "A clearer view of every complaint." }),
  ).toBeVisible();
  await expect(page.getByText("Your inbox starts here")).toBeVisible();
  await page
    .getByRole("button", { name: "Sync Emails", exact: true })
    .first()
    .click();
  await expect(page.getByText("Sync could not finish")).toBeVisible();
  await expect(
    page.getByText(/gmail not authorized run authorize command/),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
});

const complaint = {
  id: 42,
  gmail_message_id: "test-only",
  sender_email: "dh001@example.com",
  email_subject: "Late delivery <script>alert(1)</script>",
  received_at: "2026-10-28T07:00:00Z",
  complaint_type: "late_delivery",
  order_id: "DH001",
  requested_action: "shipping_fee_refund",
  priority: "medium",
  policy_result: "eligible_for_review",
  case_status: "pending_review",
  processing_error: null,
};
const detail = {
  ...complaint,
  email_body: "<img src=x onerror=alert(1)> My order DH001 was late.",
  ai_summary: "Test fixture: customer requests a shipping fee refund.",
  missing_information: [],
  verification_status: "delivered",
  sender_matches_order: true,
  verified_order: {
    order_id: "DH001",
    customer_email: "dh001@example.com",
    order_status: "Delivered",
    expected_delivery_date: "2026-10-25",
    actual_delivery_date: "2026-10-27",
    shipping_fee: "40000.00",
  },
  policy_reason: "Test fixture: database dates confirm late delivery.",
};

test("fixture-based populated details render AI and database information safely", async ({
  page,
}) => {
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    let body: unknown;
    if (url.pathname.endsWith("/stats"))
      body = {
        total: 1,
        pending_review: 1,
        insufficient_information: 0,
        processed: 0,
      };
    else if (url.pathname.endsWith("/status"))
      body = {
        gmail_configured: true,
        gemini_configured: true,
        note: "Fixture only",
      };
    else if (url.pathname.endsWith("/42")) body = detail;
    else body = { items: [complaint], total: 1, page: 1, page_size: 10 };
    await route.fulfill({ json: body });
  });
  await page.goto("/");
  await page
    .getByRole("button", { name: complaint.email_subject, exact: true })
    .waitFor();
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(page.viewportSize()!.width);
  await page
    .getByRole("button", { name: complaint.email_subject, exact: true })
    .click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByText("AI-generated analysis")).toBeVisible();
  await expect(dialog.getByText("Verified database information")).toBeVisible();
  await expect(
    dialog.getByText(detail.email_body, { exact: true }),
  ).toBeVisible();
  await expect(dialog.locator("img")).toHaveCount(0);
  await expect(
    dialog.getByText("Eligible For Review", { exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await page
    .getByLabel("Status", { exact: true })
    .selectOption("pending_review");
  await expect(
    page.getByRole("button", { name: complaint.email_subject, exact: true }),
  ).toBeVisible();
});

test("backend errors show a recovery action", async ({ page }) => {
  await page.route("**/api/**", (route) =>
    route.fulfill({ status: 503, json: { detail: "Database unavailable" } }),
  );
  await page.goto("/");
  await expect(page.getByText("Workspace unavailable")).toBeVisible();
  await expect(page.getByRole("button", { name: "Try again" })).toBeVisible();
});

for (const fails of [false, true]) {
  test(`retry saved email ${fails ? "shows a provider error" : "refreshes successful analysis"} without Gmail sync`, async ({
    page,
  }) => {
    let analyzed = false;
    let calls = 0;
    let gmailCalls = 0;
    await page.route("**/api/**", async (route) => {
      const path = new URL(route.request().url()).pathname;
      if (path.endsWith("/gmail/sync")) gmailCalls++;
      if (path.endsWith("/42/analyze")) {
        calls++;
        await new Promise((resolve) => setTimeout(resolve, 300));
        if (fails)
          return route.fulfill({
            status: 503,
            json: { detail: "gemini_timeout_retry_sync" },
          });
        analyzed = true;
        return route.fulfill({ json: detail });
      }
      if (path.endsWith("/stats"))
        return route.fulfill({
          json: {
            total: 1,
            pending_review: analyzed ? 1 : 0,
            insufficient_information: 0,
            processed: 0,
          },
        });
      if (path.endsWith("/status"))
        return route.fulfill({
          json: {
            gmail_configured: true,
            gemini_configured: true,
            note: "fixture",
          },
        });
      const failed = {
        ...detail,
        case_status: "processing_failed",
        processing_error: "gemini_timeout_retry_sync",
        ai_summary: null,
        verified_order: null,
        policy_result: null,
      };
      if (path.endsWith("/42"))
        return route.fulfill({ json: analyzed ? detail : failed });
      return route.fulfill({
        json: {
          items: [analyzed ? complaint : failed],
          total: 1,
          page: 1,
          page_size: 10,
        },
      });
    });
    await page.goto("/");
    await page
      .getByRole("button", { name: complaint.email_subject, exact: true })
      .click();
    const dialog = page.getByRole("dialog");
    const retry = dialog.getByRole("button", { name: "Retry Gemini analysis" });
    await expect(retry).toBeVisible();
    await page.getByRole("button", { name: "Close details" }).focus();
    await page.keyboard.press("Tab");
    await expect(retry).toBeFocused();
    await retry.click();
    await expect(
      dialog.getByRole("button", { name: "Gemini is analyzing…" }),
    ).toBeDisabled();
    if (fails) {
      await expect(dialog.getByRole("alert")).toContainText(
        "gemini timeout retry sync",
      );
      await expect(
        dialog.getByRole("button", { name: "Retry Gemini analysis" }),
      ).toBeEnabled();
    } else {
      await expect(
        dialog.getByText("Eligible For Review", { exact: true }),
      ).toBeVisible();
      await expect(
        dialog.getByRole("button", { name: "Retry Gemini analysis" }),
      ).toHaveCount(0);
    }
    expect(calls).toBe(1);
    expect(gmailCalls).toBe(0);
  });
}

test("Groq configuration and retry action display selected provider", async ({
  page,
}) => {
  await page.route("**/api/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith("/status"))
      return route.fulfill({
        json: {
          gmail_configured: true,
          gemini_configured: true,
          ai_provider: "groq",
          ai_model: "openai/gpt-oss-120b",
          ai_configured: false,
          note: "fixture",
        },
      });
    if (path.endsWith("/stats"))
      return route.fulfill({
        json: {
          total: 1,
          pending_review: 0,
          insufficient_information: 0,
          processed: 0,
        },
      });
    const failed = {
      ...detail,
      case_status: "processing_failed",
      ai_summary: null,
      processing_error: "groq_not_configured_add_groq_api_key",
    };
    if (path.endsWith("/42")) return route.fulfill({ json: failed });
    return route.fulfill({
      json: { items: [failed], total: 1, page: 1, page_size: 10 },
    });
  });
  await page.goto("/");
  await expect(page.locator(".connection-bar")).toContainText(
    "Groq setup needed",
  );
  await expect(page.locator(".connection-bar")).toContainText(
    "openai/gpt-oss-120b",
  );
  await page
    .getByRole("button", { name: complaint.email_subject, exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Retry Groq analysis" }),
  ).toBeVisible();
});
