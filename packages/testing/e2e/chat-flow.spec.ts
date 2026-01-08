/**
 * Chat Flow E2E Tests
 * 
 * End-to-end tests for the chat functionality.
 * 
 * Team: QA
 */

import { test, expect } from '@playwright/test';

test.describe('Chat Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display welcome message', async ({ page }) => {
    await expect(page.getByText('Welcome to Adiyogi POC')).toBeVisible();
  });

  test('should show header with model name', async ({ page }) => {
    await expect(page.getByText('Gemini 3 Flash')).toBeVisible();
  });

  test('should have input field', async ({ page }) => {
    const input = page.getByPlaceholder('Ask about video production');
    await expect(input).toBeVisible();
  });

  test('should have send button', async ({ page }) => {
    const button = page.getByRole('button', { name: 'Send' });
    await expect(button).toBeVisible();
  });

  test('should disable button when loading', async ({ page }) => {
    const input = page.getByPlaceholder('Ask about video production');
    const button = page.getByRole('button', { name: 'Send' });
    
    await input.fill('Hello');
    await button.click();
    
    // Button should show "Thinking..."
    await expect(page.getByRole('button', { name: 'Thinking...' })).toBeVisible();
  });
});

test.describe('Chat Interaction', () => {
  test.skip('should send message and receive response', async ({ page }) => {
    // This test requires backend to be running
    await page.goto('/');
    
    const input = page.getByPlaceholder('Ask about video production');
    const button = page.getByRole('button', { name: 'Send' });
    
    await input.fill('Say hello');
    await button.click();
    
    // Wait for response
    await expect(page.getByText('🎬 Director')).toBeVisible({ timeout: 30000 });
  });
});
