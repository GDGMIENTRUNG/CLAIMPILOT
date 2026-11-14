import { test, expect } from "@playwright/test";

test("real local workspace: settings, KB approval, decision, composer and context review", async ({
  page,
}, info) => {
  const mobile = info.project.name === "mobile";
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await page.getByLabel("Tên đăng nhập").fill("browser-tester");
  await page.getByLabel("Mật khẩu").fill("synthetic-browser-password");
  await page.getByRole("button", { name: "Vào workspace →", exact: true }).click();
  await page.getByRole("button", { name: "Cài đặt", exact: true }).click();
  await page
    .getByLabel("Tên doanh nghiệp")
    .fill(`Synthetic ${info.project.name} Shop`);
  await page
    .getByLabel("Lý do cập nhật")
    .fill("Thiết lập dữ liệu kiểm thử riêng");
  await page
    .getByRole("button", { name: "Lưu thông tin doanh nghiệp" })
    .click();
  await expect(page.getByText(/Đã lưu cấu hình phiên bản/)).toBeVisible();

  await page
    .getByRole("button", { name: "Knowledge Base", exact: true })
    .click();
  await page.getByRole("button", { name: "Tạo bài viết" }).click();
  await page
    .getByLabel("Tiêu đề", { exact: true })
    .fill(`Giao hàng trễ ${info.project.name}`);
  await page.getByLabel("Chủ đề", { exact: true }).fill("late_delivery");
  await page.getByLabel("Nguồn nội dung").fill("Chính sách kiểm thử tổng hợp");
  await page
    .getByLabel("Nội dung", { exact: true })
    .fill(
      "Giao hàng trễ: nhân viên cần kiểm tra thông tin và phản hồi khách. Không tự động hoàn tiền.",
    );
  await page.getByLabel("Hết hiệu lực lúc").fill("2099-01-01T10:00");
  await page.getByLabel("Hạn rà soát").fill("2098-12-01T10:00");
  await page.getByRole("button", { name: "Lưu bản nháp", exact: true }).click();
  await page.getByRole("button", { name: "Gửi duyệt", exact: true }).click();
  await page
    .getByRole("button", { name: "Duyệt & xuất bản", exact: true })
    .click();
  await expect(
    page.getByText("Đã cập nhật trạng thái bài viết."),
  ).toBeVisible();
  await page.getByRole("button", { name: "Xem lịch sử phiên bản" }).click();
  await expect(
    page
      .getByRole("region", { name: "Lịch sử tri thức" })
      .getByText("Lịch sử duyệt & thay đổi"),
  ).toBeVisible();

  await page.getByRole("button", { name: "Hộp thư", exact: true }).click();
  await page
    .locator(".cp-case")
    .filter({ hasText: `E2E ${info.project.name} giao hàng trễ` })
    .click();
  if (mobile)
    await page.getByRole("button", { name: "Đánh giá", exact: true }).click();
  await page.getByLabel("Thông tin cần bổ sung").fill("Mã đơn");
  await page
    .getByLabel("Lý do quyết định")
    .fill("Cần xác minh mã đơn trước khi xử lý");
  await page.getByRole("button", { name: "Ghi nhận quyết định" }).click();
  if (mobile)
    await page.getByRole("button", { name: "Hội thoại", exact: true }).click();
  await page
    .getByRole("button", { name: "Viết thủ công", exact: true })
    .click();
  const body =
    "Xin chào, chúng tôi đã tiếp nhận thông tin giao trễ. Vui lòng cung cấp mã đơn để kiểm tra. Cảm ơn bạn.";
  await page.getByLabel("Nội dung phản hồi", { exact: true }).fill(body);
  if (mobile) {
    await page.getByRole("button", { name: "Lịch sử", exact: true }).click();
    await page.getByRole("button", { name: "Hội thoại", exact: true }).click();
    await expect(
      page.getByLabel("Nội dung phản hồi", { exact: true }),
    ).toHaveValue(body);
  }
  await page.getByRole("button", { name: "Lưu nội dung", exact: true }).click();
  await page
    .getByRole("button", { name: "Kiểm tra & xem trước", exact: true })
    .click();
  await expect(page.locator(".cp-preview")).toContainText(body);
  await expect(
    page.getByRole("button", { name: "Gửi phản hồi", exact: true }),
  ).toBeDisabled();
  await page.locator(".cp-quality .cp-source-link").first().click();
  await expect(
    page.getByRole("dialog", { name: "Nguồn tri thức" }),
  ).toContainText("Chính sách kiểm thử tổng hợp");
  await page.getByRole("dialog", { name: "Nguồn tri thức" }).getByRole("button", { name: /Đóng/ }).click();

  // Settings invalidate acknowledgement while preserving the saved body.
  await page.getByRole("button", { name: "Cài đặt", exact: true }).click();
  await page.getByLabel("Giọng điệu").selectOption("formal");
  await page.getByLabel("Lý do cập nhật").fill("Đổi giọng điệu kiểm thử");
  await page
    .getByRole("button", { name: "Lưu thông tin doanh nghiệp" })
    .click();
  await expect(page.getByText(/Đã lưu cấu hình phiên bản/)).toBeVisible();
  await page.getByRole("button", { name: "Hộp thư", exact: true }).click();
  await expect(page.locator(".cp-preview")).toHaveCount(0);
  await expect(
    page.getByLabel("Nội dung phản hồi", { exact: true }),
  ).toHaveValue(body);
  await page
    .getByRole("button", { name: "Đối chiếu ngữ cảnh & nguồn", exact: true })
    .click();
  await page
    .getByLabel("Ghi chú đối chiếu")
    .fill("Đã kiểm tra lại nội dung, nguồn và giọng điệu");
  await page
    .getByRole("button", { name: "Xác nhận đã đối chiếu", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Kiểm tra & xem trước", exact: true })
    .click();
  await expect(page.locator(".cp-preview")).toContainText(body);

  // Unsaved text from decision 1 must never become the reply of decision 2.
  await page
    .getByLabel("Nội dung phản hồi", { exact: true })
    .fill("UNSAVED OLD DECISION TEXT");
  if (mobile)
    await page.getByRole("button", { name: "Đánh giá", exact: true }).click();
  await page.getByLabel("Phương án").selectOption("reject");
  await page.getByLabel("Lý do quyết định").fill("Quyết định kiểm thử thứ hai");
  await page.getByRole("button", { name: "Ghi nhận quyết định" }).click();
  if (mobile)
    await page.getByRole("button", { name: "Hội thoại", exact: true }).click();
  await page
    .getByRole("button", { name: "Viết thủ công", exact: true })
    .click();
  await expect(
    page.getByLabel("Nội dung phản hồi", { exact: true }),
  ).toHaveValue("");
  await expect(page.locator(".cp-preview")).toHaveCount(0);
  if(mobile)await page.getByRole('button',{name:'Đánh giá',exact:true}).click();
  await expect(page.locator('.cp-agent').filter({hasText:'An toàn & chất lượng'})).toContainText('Chưa có lượt chạy');
  if(mobile)await page.getByRole('button',{name:'Hội thoại',exact:true}).click();
  expect(errors).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: `test-results/workspace-${info.project.name}.png`,
    fullPage: true,
  });
});
