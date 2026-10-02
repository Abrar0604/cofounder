import { test, expect } from '@playwright/test';

test.describe('Approvals Inbox', () => {
  test('clicking approve updates the UI status and removes the review button', async ({ page }) => {
    // Navigate to the approvals page
    await page.goto('/dashboard/approvals');
    
    // Find the first approval card
    const firstCard = page.getByTestId('approval-card').first();
    const reviewButton = firstCard.getByRole('button', { name: 'Review' });
    await expect(reviewButton).toBeVisible();

    // Verify it initially says "Pending"
    await expect(firstCard.getByText('Pending', { exact: true })).toBeVisible();

    // Click "Review" to open the dialog
    await reviewButton.click();

    // The dialog should be open
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Find and click the "Approve" button
    const approveButton = dialog.getByRole('button', { name: 'Approve', exact: true });
    await approveButton.click();

    // The dialog should close
    await expect(dialog).not.toBeVisible();

    // The badge should now say "Approved"
    await expect(firstCard.getByText('Approved', { exact: true })).toBeVisible();

    // The "Review" button should no longer be visible
    await expect(reviewButton).not.toBeVisible();
  });
});
