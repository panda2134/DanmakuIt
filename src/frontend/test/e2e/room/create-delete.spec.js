const { test, expect } = require('@playwright/test')
const { createRoom, deleteRoom } = require('./utils.js')


test.use({
  storageState: 'auth.json'
});

test.describe('Room list',  () => {
  test('should handle room creation & deletion', async ({ page }) => {
    const roomName = await createRoom(page)
    await page.goto('http://localhost:3000/my-room')

    // Click button:has-text("管理")
    await Promise.all([
      page.waitForNavigation(),
      page.click(`.v-card:has-text("${roomName}") .v-card__actions button:has-text("管理")`)
    ]);

    // assert text=尚未设置微信公众号AppID/AppSecret，弹幕墙头像抓取、二维码显示等功能将不会工作。 完成设置后，请点击按钮抓取现有关注者的头像等信息。
    await expect(page.locator('.v-alert.error')).toContainText(['尚未设置微信公众号AppID/AppSecret，弹幕墙头像抓取、二维码显示等功能将不会工作。',
      '完成设置后，请点击按钮抓取现有关注者的头像等信息。']);

    // Click text=我的房间
    await page.click('text=我的房间');
    await expect(page).toHaveURL('http://localhost:3000/my-room');

    await deleteRoom(page, roomName)
  });
})
