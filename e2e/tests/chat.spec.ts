import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('http://localhost:5173/');

  await expect(page).toHaveTitle("DTwin");
});

test('supervisor responds to prompt', async ({ page }) => {
  await page.goto('http://localhost:5173/');
  
  await page.getByPlaceholder('Type your message...').fill("Hello");

  await page.getByRole('button', {name: 'Send Message'}).click();

  await expect(page.getByRole('button', { name: 'Supervisor:' })).toBeVisible()
});

test('new chat button works', async ({ page }) => {
  await page.goto('http://localhost:5173/');

  await page.getByPlaceholder('Type your message...').fill("Hello");

  await page.getByRole('button', {name: 'Send Message'}).click();

  await page.getByRole('button', {name: 'New chat'}).click();

  await expect(page.getByRole('button', { name: 'Supervisor:' })).toBeHidden()
});

// test('sign up link', async ({ page }) => {
//   await page.goto('http://localhost:5173/signin');

//   await page.getByRole('link', { name: 'Sign Up' }).click();

//   // Expects page to have a heading with the name of Installation.
//   await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
// });
