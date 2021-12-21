const { test } = require('@playwright/test')
const { createRoom } = require('./utils.js')


test.use({
  storageState: 'auth.json'
});

test.describe.parallel('Room info page', async () => {
  let roomName
  test.beforeAll(async ({ page }) => {
    // create the test room
    roomName = await createRoom(page)
    await page.goto('http://localhost:3000/')
  })
})
