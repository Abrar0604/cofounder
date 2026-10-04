import { test, expect } from '@playwright/test';

test('Approval Inbox flow - approve action updates UI', async ({ page }) => {
  // Navigate to approvals page
  await page.goto('http://localhost:3000/dashboard/approvals');

  // Verify the pending approval card is visible
  const title = page.locator('text=Budget Increase for Q3 Marketing');
  await expect(title).toBeVisible();

  // Find the first Review button and click it to open the dialog
  const reviewButton = page.locator('button', { hasText: 'Review' }).first();
  await expect(reviewButton).toBeVisible();
  await reviewButton.click();

  // Inside the dialog, click the Approve button
  const approveButton = page.locator('button', { hasText: 'Approve' }).first();
  await expect(approveButton).toBeVisible();
  await approveButton.click();

  // Dialog should close, and the badge should change to Approved
  await expect(page.locator('text=Review Approval Request')).not.toBeVisible();
  const badge = page.locator('.inline-flex', { hasText: 'Approved' }).first();
  await expect(badge).toBeVisible();
});
