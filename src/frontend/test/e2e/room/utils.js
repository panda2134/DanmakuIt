const { nanoid } = require('nanoid')
const { expect } = require('@playwright/test')

async function createRoom (page, roomName) {
  if (!roomName) {
    roomName = `playwright@${nanoid(8)}`
  }
  await page.goto('http://localhost:3000/')

  // Click button:has-text("管理房间")
  await page.click('button:has-text("管理房间")');
  await expect(page).toHaveURL('http://localhost:3000/my-room');

  try {
    // Click menu btn
    await page.click('.v-speed-dial .mdi-menu');
  } catch (e) {
    // empty!
    await expect(page).toContainText(['什么都没有哦', '点击右下角，创建一个新房间'])
  }
  // Click create btn
  await page.click('.mdi-plus');

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

  return roomName
}

async function deleteRoom(page, roomName) {
  await page.goto('http://localhost:3000/my-room')
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
}

module.exports = {
  createRoom, deleteRoom
}
