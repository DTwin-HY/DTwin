import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../playwright/.auth/user.json');

setup('authenticate', async ({ page }) => {
  // Perform authentication steps. Replace these actions with your own.
  await page.goto('http://localhost:5173/signin');
  await page.getByPlaceholder('Your username').fill('user');
  await page.getByPlaceholder('Your password').fill('user');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('http://localhost:5173/');

  await page.context().storageState({ path: authFile });
});