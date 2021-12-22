const { test, expect } = require('@playwright/test')
const { createRoom, deleteRoom } = require('./utils.js')

test.use({
  storageState: 'auth.json'
})

test.describe.serial('Room info page', () => {
  let roomName
  test.beforeAll(async ({ browser }) => {
    // create the test room
    const ctx = await browser.newContext()
    const page = await ctx.newPage()
    roomName = await createRoom(page)
    await ctx.close()
  })

  async function gotoRoomInfoPage (page) {
    await page.goto('http://localhost:3000/my-room')
    await Promise.all([
      page.waitForNavigation(),
      page.click(`.v-card:has-text("${roomName}") .v-card__actions button:has-text("管理")`)
    ])
  }

  test('should show room name', async ({ page }) => {
    await gotoRoomInfoPage(page)
    await expect(page.locator('.v-input:has-text("房间名称") input[type=text]')).toHaveValue(roomName)
  })

  test('should allow danmaku by default', async ({ page }) => {
    await gotoRoomInfoPage(page)
    await expect(page.locator('.v-input:has-text("允许弹幕") input[type=checkbox]')).toBeChecked()
  })

  test('should allow turning danmaku off', async ({ page }) => {
    await gotoRoomInfoPage(page)
    await expect(page.locator('.v-input:has-text("允许弹幕") input[type=checkbox]')).toBeChecked()
    await page.click('.v-input:has-text("允许弹幕")')
    await expect(page.locator('.v-input:has-text("允许弹幕") input[type=checkbox]')).not.toBeChecked()
    await page.click('.v-card:has-text("基本信息") .v-card__actions button[type=submit]')
    await expect(page.locator('.v-snack.v-application.vts.v-snack--active .v-snack__wrapper .vts__message')).toContainText('成功')
    await expect(page.locator('.v-input:has-text("允许弹幕") input[type=checkbox]')).not.toBeChecked()
    await page.reload()
    await expect(page.locator('.v-input:has-text("允许弹幕") input[type=checkbox]')).not.toBeChecked()
  })

  test('should allow adding danmaku colors w/o wrongly triggering click:close (issue #18)', async ({ page }) => {
    await gotoRoomInfoPage(page)
    await page.click('.v-input:below(label:has-text("用户弹幕颜色")) .v-input__append-inner .mdi-plus')
    // Click text=RGB >> button
    await page.click('.v-card:has-text("选择一种弹幕颜色") .v-card__text .v-color-picker__edit button')
    // Click text=HSL >> button
    await page.click('.v-card:has-text("选择一种弹幕颜色") .v-card__text .v-color-picker__edit button')
    await page.fill('.v-card:has-text("选择一种弹幕颜色") .v-card__text .v-color-picker__edit input', '#abcdef')
    // Click button:has-text("添加")
    await page.click('.v-card:has-text("选择一种弹幕颜色") .v-card__actions button:has-text("添加")')
    await page.click('.v-input:below(label:has-text("用户弹幕颜色")) .v-input__append-inner .mdi-plus')
    await page.fill('.v-card:has-text("选择一种弹幕颜色") .v-card__text .v-color-picker__edit input', '#fedcba')
    // Click button:has-text("添加")
    await page.click('.v-card:has-text("选择一种弹幕颜色") .v-card__actions button:has-text("添加")')
    // Click text=#ABCDEF
    await page.click('text=#ABCDEF')
    await expect(page.locator('.v-chip:has-text("#ABCDEF")')).toBeVisible()
    // Click text=#FEDCBA
    await page.click('text=#FEDCBA')
    await expect(page.locator('.v-chip:has-text("#FEDCBA")')).toBeVisible()
    // Double click text=#ABCDEF
    await page.dblclick('text=#ABCDEF')
    await expect(page.locator('.v-chip:has-text("#ABCDEF")')).toBeVisible()
    // Double click text=#FEDCBA
    await page.dblclick('text=#FEDCBA')
    await expect(page.locator('.v-chip:has-text("#FEDCBA")')).toBeVisible()
    // Click button:has-text("提交")
    await page.click('.v-card:has-text("基本信息") .v-card__actions button[type=submit]')
    await expect(page.locator('.v-snack.v-application.vts.v-snack--active .v-snack__wrapper .vts__message')).toContainText('成功')
    await expect(page.locator('.v-chip:has-text("#ABCDEF")')).toBeVisible()
    await expect(page.locator('.v-chip:has-text("#FEDCBA")')).toBeVisible()
    await page.reload()
    await expect(page.locator('.v-chip:has-text("#ABCDEF")')).toBeVisible()
    await expect(page.locator('.v-chip:has-text("#FEDCBA")')).toBeVisible()
  })

  test('should allow removing colors', async ({ page }) => {
    await gotoRoomInfoPage(page)
    await page.click('.v-chip:has-text("#FEDCBA") button')
    await expect(page.locator('.v-chip:has-text("#ABCDEF")')).toBeVisible()
    await expect(page.locator('.v-chip:has-text("#FEDCBA")')).not.toBeVisible()
    await page.click('.v-chip:has-text("#ABCDEF") button')
    await expect(page.locator('.v-chip:has-text("#ABCDEF")')).not.toBeVisible()
    await page.click('.v-card:has-text("基本信息") .v-card__actions button[type=submit]')
    await expect(page.locator('.v-snack.v-application.vts.v-snack--active .v-snack__wrapper .vts__message')).toContainText('成功')
    await expect(page.locator('.v-chip:has-text("#ABCDEF")')).not.toBeVisible()
    await expect(page.locator('.v-chip:has-text("#FEDCBA")')).not.toBeVisible()
  })

  test.afterAll(async ({ browser }) => {
    const ctx = await browser.newContext()
    const page = await ctx.newPage()
    await deleteRoom(page, roomName)
    await ctx.close()
  })
})
