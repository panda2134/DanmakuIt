const {
  test,
  expect
} = require('@playwright/test')
const {
  createRoom,
  deleteRoom,
  gotoRoomInfoPage
} = require('./utils.js')

test.use({
  storageState: 'auth.json'
})

test.describe.serial('Censor configuration', () => {
  let roomName

  test.beforeAll(async ({ browser }) => {
    // create the test room
    const ctx = await browser.newContext()
    const page = await ctx.newPage()
    roomName = await createRoom(page)
    await ctx.close()
  })

  test('should allow adding censor words w/o wrongly triggering click:close', async ({ page }) => {
    await gotoRoomInfoPage(page, roomName)
    const censorWords = '.v-input:below(label:has-text("关键词黑名单")) input'
    await page.click(censorWords)
    await page.fill(censorWords, 'TestWord1')
    await page.press(censorWords, 'Enter')
    await page.fill(censorWords, 'TestWord2')
    await page.press(censorWords, 'Enter')
    // Click text=TestWord1
    await page.click('text=TestWord1')
    await expect(page.locator('.v-chip:has-text("TestWord1")')).toBeVisible()
    // Click text=TestWord2
    await page.click('text=TestWord2')
    await expect(page.locator('.v-chip:has-text("TestWord2")')).toBeVisible()
    // Double click text=TestWord1
    await page.dblclick('text=TestWord1')
    await expect(page.locator('.v-chip:has-text("TestWord1")')).toBeVisible()
    // Double click text=TestWord2
    await page.dblclick('text=TestWord2')
    await expect(page.locator('.v-chip:has-text("TestWord2")')).toBeVisible()
    // Click button:has-text("提交")
    await page.click('.v-card:has-text("审核管理") .v-card__actions button[type=submit]')
    await expect(page.locator('.v-snack.v-application.vts.v-snack--active .v-snack__wrapper .vts__message')).toContainText('成功')
    await expect(page.locator('.v-chip:has-text("TestWord1")')).toBeVisible()
    await expect(page.locator('.v-chip:has-text("TestWord2")')).toBeVisible()
    await page.reload()
    await page.click(censorWords)
    await expect(page.locator('.v-chip:has-text("TestWord1")')).toBeVisible()
    await expect(page.locator('.v-chip:has-text("TestWord2")')).toBeVisible()
  })

  test('should allow removing censor words', async ({ page }) => {
    await gotoRoomInfoPage(page, roomName)
    const censorWords = '.v-input:below(label:has-text("关键词黑名单")) input'
    await page.click(censorWords)
    await page.click('.v-chip:has-text("TestWord2") button')
    await expect(page.locator('.v-chip:has-text("TestWord1")')).toBeVisible()
    await expect(page.locator('.v-chip:has-text("TestWord2")')).not.toBeVisible()
    await page.click('.v-chip:has-text("TestWord1") button')
    await expect(page.locator('.v-chip:has-text("TestWord1")')).not.toBeVisible()
    await page.click('.v-card:has-text("审核管理") .v-card__actions button[type=submit]')
    await expect(page.locator('.v-snack.v-application.vts.v-snack--active .v-snack__wrapper .vts__message')).toContainText('成功')
    await expect(page.locator('.v-chip:has-text("TestWord1")')).not.toBeVisible()
    await expect(page.locator('.v-chip:has-text("TestWord2")')).not.toBeVisible()
    await page.reload()
    await page.click(censorWords)
    await expect(page.locator('.v-chip:has-text("TestWord1")')).not.toBeVisible()
    await expect(page.locator('.v-chip:has-text("TestWord2")')).not.toBeVisible()
  })

  test.afterAll(async ({ browser }) => {
    const ctx = await browser.newContext()
    const page = await ctx.newPage()
    await deleteRoom(page, roomName)
    await ctx.close()
  })
})
