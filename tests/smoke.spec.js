// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('CEFR Speaking Exam Simulator - Smoke Tests', () => {
  
  test('page loads successfully with title and header', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/CEFR Speaking Exam Simulator/);
    await expect(page.locator('h1')).toContainText('🎤 CEFR Speaking Exam Simulator');
  });

  test('session info panel is present', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('📊 Session Info')).toBeVisible();
    await expect(page.getByText('Current Level')).toBeVisible();
    await expect(page.getByText('Test Status')).toBeVisible();
  });

  test('footer is present', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('CEFR Speaking Exam Simulator | Practice makes perfect!')).toBeVisible();
  });
});