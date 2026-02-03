#!/usr/bin/env python3
"""Analyze TikTok comment posting flow to understand what's really happening."""

import time
from playwright.sync_api import sync_playwright
from src.config import BROWSER_PROFILES_DIR
from pathlib import Path

def analyze_comment_flow():
    """Analyze how TikTok handles comment posting."""

    agent_id = 1
    profile_dir = BROWSER_PROFILES_DIR / f"agent_{agent_id}"
    storage_path = profile_dir / "storage_state.json"

    playwright = sync_playwright().start()

    # Track network requests
    api_requests = []

    try:
        browser = playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        # Load session
        if storage_path.exists():
            context = browser.new_context(storage_state=str(storage_path))
        else:
            context = browser.new_context()

        page = context.new_page()

        # Monitor network requests
        def handle_request(request):
            if 'comment' in request.url.lower() or 'api' in request.url.lower():
                api_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'post_data': request.post_data
                })
                print(f"\n🌐 API Request: {request.method} {request.url}")

        def handle_response(response):
            if 'comment' in response.url.lower() or 'api' in response.url.lower():
                print(f"📥 API Response: {response.status} {response.url}")
                try:
                    body = response.text()
                    print(f"   Body preview: {body[:200]}")
                except:
                    pass

        page.on('request', handle_request)
        page.on('response', handle_response)

        # Navigate to a video
        video_url = "https://www.tiktok.com/@barna3758/video/7542086143957798200"
        print(f"\n📺 Navigating to: {video_url}")
        page.goto(video_url)
        time.sleep(5)

        print("\n" + "="*70)
        print("STEP 1: Analyzing comment section HTML structure")
        print("="*70)

        # Click comment button
        print("\n🖱️  Clicking comment button...")
        comment_btn = page.locator('[data-e2e="comment-icon"]').first
        if comment_btn.count() > 0:
            comment_btn.click()
            time.sleep(2)

        # Get comment section HTML
        comment_section_html = page.evaluate("""
            () => {
                const section = document.querySelector('[data-e2e="comment-level-1"]') ||
                               document.querySelector('[class*="CommentList"]') ||
                               document.querySelector('[class*="comment"]');
                return section ? section.outerHTML.substring(0, 1000) : 'Not found';
            }
        """)
        print(f"\n📄 Comment section HTML preview:\n{comment_section_html}\n")

        # Get comment input details
        input_details = page.evaluate("""
            () => {
                const input = document.querySelector('[data-e2e="comment-input"]');
                if (!input) return {found: false};

                return {
                    found: true,
                    tagName: input.tagName,
                    type: input.type,
                    contentEditable: input.contentEditable,
                    attributes: Array.from(input.attributes).map(a => ({name: a.name, value: a.value})),
                    eventListeners: Object.keys(input).filter(k => k.startsWith('on'))
                };
            }
        """)
        print(f"\n📝 Comment input details:\n{input_details}\n")

        # Get post button details
        post_btn_details = page.evaluate("""
            () => {
                const btn = document.querySelector('[data-e2e="comment-post"]');
                if (!btn) return {found: false};

                return {
                    found: true,
                    tagName: btn.tagName,
                    disabled: btn.disabled,
                    className: btn.className,
                    attributes: Array.from(btn.attributes).map(a => ({name: a.name, value: a.value}))
                };
            }
        """)
        print(f"\n🔘 Post button details:\n{post_btn_details}\n")

        print("\n" + "="*70)
        print("STEP 2: Simulating manual comment typing")
        print("="*70)

        # Type a test comment slowly (like a human)
        test_comment = "Test comment for analysis"
        comment_input = page.locator('[data-e2e="comment-input"]').first

        print(f"\n⌨️  Typing: '{test_comment}'")
        comment_input.click()
        time.sleep(0.5)

        # Type character by character
        for char in test_comment:
            page.keyboard.type(char)
            time.sleep(0.1)

        time.sleep(1)

        # Check if post button enabled
        post_btn_enabled = page.evaluate("""
            () => {
                const btn = document.querySelector('[data-e2e="comment-post"]');
                return btn ? !btn.disabled : false;
            }
        """)
        print(f"\n✓ Post button enabled: {post_btn_enabled}")

        print("\n" + "="*70)
        print("STEP 3: Analyzing what happens when clicking Post")
        print("="*70)

        print("\n🖱️  Clicking Post button...")
        print("📡 Watching for network activity...\n")

        # Clear previous requests
        api_requests.clear()

        # Click post
        post_btn = page.locator('[data-e2e="comment-post"]').first
        post_btn.click()

        # Wait and watch
        time.sleep(5)

        print(f"\n📊 Captured {len(api_requests)} API requests")
        for req in api_requests:
            print(f"\n  Method: {req['method']}")
            print(f"  URL: {req['url']}")
            if req['post_data']:
                print(f"  Data: {req['post_data'][:200]}")

        print("\n" + "="*70)
        print("STEP 4: Checking if comment appears in DOM")
        print("="*70)

        time.sleep(3)

        # Look for the comment text in the page
        comment_found = page.locator(f'text="{test_comment}"').count() > 0
        print(f"\n🔍 Comment found in DOM: {comment_found}")

        # Check input state
        input_state = page.evaluate("""
            () => {
                const input = document.querySelector('[data-e2e="comment-input"]');
                return {
                    textContent: input?.textContent || '',
                    innerText: input?.innerText || '',
                    innerHTML: input?.innerHTML || ''
                };
            }
        """)
        print(f"\n📝 Input state after posting:\n{input_state}\n")

        # Get all comments currently visible
        existing_comments = page.evaluate("""
            () => {
                const comments = Array.from(document.querySelectorAll('[data-e2e="comment-level-1"]'));
                return comments.slice(0, 5).map(c => ({
                    text: c.textContent.substring(0, 100),
                    author: c.querySelector('[data-e2e="comment-username"]')?.textContent || 'unknown'
                }));
            }
        """)
        print(f"💬 Recent comments visible:\n")
        for i, comment in enumerate(existing_comments, 1):
            print(f"  {i}. @{comment['author']}: {comment['text'][:50]}...")

        print("\n" + "="*70)
        print("ANALYSIS COMPLETE - Browser will stay open for inspection")
        print("="*70)
        print("\nCheck:")
        print("1. Did any API request go through?")
        print("2. Did the comment appear in the comment list?")
        print("3. Are there any error messages?")
        print("4. What's different from manual posting?")

        input("\nPress Enter to close browser...")

        browser.close()
        playwright.stop()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            browser.close()
            playwright.stop()
        except:
            pass

if __name__ == "__main__":
    analyze_comment_flow()
