
const { test, expect } = require('@playwright/test')
const { nanoid } = require('nanoid')


test.use({
  storageState: 'auth.json'
});

test('test', async ({ page }) => {
  const nonce = nanoid(8)
  const roomName = `playwright@${nonce}`
  await page.goto('http://localhost:3000/')

  // Click button:has-text("管理房间")
  await page.click('button:has-text("管理房间")');
  await expect(page).toHaveURL('http://localhost:3000/my-room');

  // Click menu btn
  await page.click('.v-speed-dial > button >> .mdi-menu');

  // Click create btn
  await page.click('.v-speed-dial > .v-speed-dial__list >> .mdi-plus');

  // Click input[type="text"]
  await page.click('input[type="text"]');

  // Fill input[type="text"]
  await page.fill('input[type="text"]', roomName);

  // Click button:has-text("创建")
  await page.click('button:has-text("创建")');

  // Click button:has-text("管理")
  await Promise.all([
    page.waitForNavigation(),
    page.click(`.v-card:has-text("${roomName}") .v-card__actions button:has-text("管理")`)
  ]);

  // assert text=尚未设置微信公众号AppID/AppSecret，弹幕墙头像抓取、二维码显示等功能将不会工作。 完成设置后，请点击按钮抓取现有关注者的头像等信息。
  await expect(page.locator('.v-alert.error')).toContainText( ['尚未设置微信公众号AppID/AppSecret，弹幕墙头像抓取、二维码显示等功能将不会工作。',
    '完成设置后，请点击按钮抓取现有关注者的头像等信息。']);

  // Click text=我的房间
  await page.click('text=我的房间');
  await expect(page).toHaveURL('http://localhost:3000/my-room');

  // Click menu btn
  await page.click('.v-speed-dial > button >> .mdi-menu');

  // Click delete btn
  await page.click('.v-speed-dial > .v-speed-dial__list >> .mdi-delete');

  // Click button[role="button"]:has-text("删除")
  await page.click(`.v-card:has-text("${roomName}") .v-card__actions button[role="button"]:has-text("删除")`);

  // Click input[type="text"]
  await page.click('input[type="text"]');

  // Fill input[type="text"]
  await page.fill('input[type="text"]', roomName);

  // Click div[role="document"] button:has-text("删除")
  await page.click('.v-card:has-text("输入房间名称以确认") .v-card__actions button:has-text("删除")');

  // ensure removed
  await expect(page.locator(`text="${roomName}"`)).toHaveCount(0)

  // Click back btn
  await page.click('button .mdi-chevron-left');

  // Click close btn to close fab
  await page.click('.v-speed-dial > button .mdi-close')

});
