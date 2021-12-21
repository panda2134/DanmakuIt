const {
  test,
  expect
} = require('@playwright/test')

test.use({
  storageState: 'auth.json'
});
test.describe('User menu',  () => {
  test('should handle logout', async ({ page }) => {
    // Go to http://localhost:3000/
    await page.goto('http://localhost:3000/');
    // Click button:has-text("管理房间")
    await page.click('button:has-text("管理房间")');
    await expect(page).toHaveURL('http://localhost:3000/my-room');
    // Click button[role="button"]
    await page.click('button[role="button"] i.mdi-account');
    // Click div[role="menuitem"] >> text=退出登录
    await page.click('div[role="menuitem"] >> text=退出登录');
    await expect(page).toHaveURL('http://localhost:3000/');

    const token = await page.evaluate("!!window.localStorage.getItem('token')");
    await expect(token).toBeFalsy()
  });
})
