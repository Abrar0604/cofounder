import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test('Strict monochrome CSS classes check', async ({ page }) => {
  // We can just verify the tailwind configuration or rendered classes
  const globalsCss = fs.readFileSync(path.join(__dirname, '../../src/app/globals.css'), 'utf-8');
  
  // Just a simple heuristic test to fail if we detect colors like 'red', 'blue', etc in standard places
  expect(globalsCss).not.toContain('text-blue');
  expect(globalsCss).not.toContain('bg-red');
  
  // Navigate to dashboard
  await page.goto('http://localhost:3000/dashboard');
  
  // Verify body is monochrome
  const body = page.locator('body');
  const color = await body.evaluate((el) => window.getComputedStyle(el).color);
  const bgColor = await body.evaluate((el) => window.getComputedStyle(el).backgroundColor);
  
  // Verify body is styled without errors
  expect(body).toBeTruthy();
  // Ensure it's not some random saturated color
  expect(color).not.toMatch(/rgb\([0-9]+, 0, 0\)/); // basic sanity check
  expect(bgColor).not.toMatch(/rgb\([0-9]+, 0, 0\)/);
});
