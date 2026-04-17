import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        errors = []
        page.on('console', lambda msg: errors.append(f'CONSOLE: {msg.text}') if msg.type == 'error' else None)
        page.on('pageerror', lambda err: errors.append(f'PAGE ERROR: {err}'))
        
        print('Navigating to page...')
        await page.goto('http://127.0.0.1:8000/chatbot/')
        
        print('Waiting for chat button...')
        await page.wait_for_selector('button[onclick="openChat()"]')
        
        print('Clicking chat button...')
        await page.click('button[onclick="openChat()"]')
        
        await page.wait_for_timeout(2000)
        
        print('\n--- Captured Errors ---')
        if not errors:
            print('No errors captured!')
        else:
            for err in errors:
                print(err)
        
        await browser.close()

asyncio.run(main())
