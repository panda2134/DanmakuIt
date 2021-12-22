const { test, expect } = require('@playwright/test')
const { createRoom, deleteRoom } = require('../../room/utils.js')

test.use({
  storageState: 'auth.json'
})

test.describe.parallel('User menu', () => {
  test('should display user info popup in /my-room', async ({ page }) => {
    // Go to http://localhost:3000/
    await page.goto('http://localhost:3000/')
    // Click button:has-text("管理房间")
    await page.click('button:has-text("管理房间")')
    await expect(page).toHaveURL('http://localhost:3000/my-room')
    // Click button[role="button"]
    await page.click('button[role="button"] i.mdi-account')
    // Check that menu contains username & uid
    await expect(page.locator('div[role=menu]')).toContainText([
      'liujiang19', 'gitlab3rd:1357'
    ])
    // Check avatar
    await expect(page.locator('div[role=menu]:has-text("退出登录")  .v-image__image.v-image__image--preload')).not.toBeVisible()
    await page.waitForLoadState('networkidle')
    await expect(page.locator('div[role=menu]:has-text("退出登录") .v-image__image'))
      .toHaveCSS('background-image', /gravatar/)
    // Click div[role="menuitem"] >> text=我的房间
    await page.click('div[role="menuitem"] >> text=我的房间')
    await expect(page).toHaveURL('http://localhost:3000/my-room')
  })
  test('should have a working "/my-room" link in room detail page', async ({ page }) => {
    const roomName = await createRoom(page)
    await page.goto('http://localhost:3000/my-room')

    // Click button:has-text("管理")
    await Promise.all([
      page.waitForNavigation(),
      page.click(`.v-card:has-text("${roomName}") .v-card__actions button:has-text("管理")`)
    ])

    // Click button[role="button"]
    await page.click('button[role="button"] i.mdi-account')
    // Click div[role="menuitem"] >> text=我的房间
    await page.click('div[role="menuitem"] >> text=我的房间')
    await expect(page).toHaveURL('http://localhost:3000/my-room')

    await deleteRoom(page, roomName)
  })
})
