import { test, expect } from '@playwright/test';

test.describe('Approvals Inbox', () => {
  test('clicking approve updates the UI status and removes the review button', async ({ page }) => {
    // Navigate to the approvals page
    await page.goto('/dashboard/approvals');
    
    // Find the first approval card
    const firstCard = page.locator('.rounded-none.shadow-none').first();
    const reviewButton = firstCard.locator('button', { hasText: 'Review' });
    await expect(reviewButton).toBeVisible();

    // Verify it initially says "Pending"
    // Using an explicit locator for the badge to avoid relying on utility classes
    await expect(firstCard.locator('span', { hasText: 'Pending' })).toBeVisible();

    // Click "Review" to open the dialog
    await reviewButton.click();

    // The dialog should be open
    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();

    // Find and click the "Approve" button
    const approveButton = dialog.locator('button:has-text("Approve")');
    await approveButton.click();

    // The dialog should close
    await expect(dialog).not.toBeVisible();

    // The badge should now say "Approved"
    await expect(firstCard.locator('span', { hasText: 'Approved' })).toBeVisible();

    // The "Review" button should no longer be visible
    await expect(reviewButton).not.toBeVisible();
  });
});
