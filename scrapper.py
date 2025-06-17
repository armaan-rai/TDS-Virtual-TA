import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from datetime import datetime
import time
import re

# Define cutoff date
CUTOFF_DATE = datetime(2025, 4, 15)

# List of URLs to scrape
start_urls = [
    "https://tds.s-anand.net/#/2025-01/",
    "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"
]

USERNAME = ""
PASSWORD = ""

def extract_date_from_text_or_url(text, url):
    date_patterns = [
        r'(\d{1,2}\s+\w+\s+\d{4})',
        r'(\w+\s+\d{1,2},\s+\d{4})',
        r'(\d{4}-\d{2}-\d{2})'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            for fmt in ['%d %B %Y', '%B %d, %Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(match.group(1), fmt)
                except:
                    continue

    match = re.search(r'(\d{4}-\d{2}-\d{2})', url)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
        except:
            pass
    return None

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for start_url in start_urls:
            await page.goto(start_url)
            await page.wait_for_load_state("networkidle")

            login_required = False
            login_button_keywords = ["login", "sign in", "log in", "authenticate", "access account"]
            login_input_fields = ["login-account-name", "login-account-password", "username", "password", "email"]

            buttons = await page.query_selector_all("button")
            for button in buttons:
                label = (await button.inner_text() or await button.get_attribute("aria-label") or "").strip().lower()
                if any(keyword in label for keyword in login_button_keywords):
                    login_required = True
                    break

            inputs = await page.query_selector_all("input")
            for input_tag in inputs:
                name = await input_tag.get_attribute("name")
                if name and name.lower() in login_input_fields:
                    login_required = True
                    break

            if login_required:
                print("🔐 Login required. Attempting login...")
                login_links = await page.query_selector_all("a")
                for link in login_links:
                    text = (await link.inner_text() or "").strip().lower()
                    if any(keyword in text for keyword in login_button_keywords):
                        print(f"🔘 Clicking login link: {text}")
                        await link.click()
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(1)
                        break

                try:
                    await page.fill('#login-account-name', USERNAME)
                    await page.fill('#login-account-password', PASSWORD)
                    await page.click("#login-button")
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                    print("✅ Login successful.")
                except:
                    print("❌ Login failed. Skipping this URL.")
                    continue

            print("🔗 Collecting page links...")
            links = await page.query_selector_all("a")
            hrefs = []
            for link in links:
                href = await link.get_attribute("href")
                if href and not (
                    href.startswith("mailto:") or
                    "linkedin.com" in href.lower() or
                    "@" in href
                ):
                    full_url = urljoin(start_url, href)
                    hrefs.append(full_url)

            print(f"🔍 Found {len(hrefs)} valid links.")

            contents = []
            trusted_domains = ["tds.s-anand.net"]

            for href in hrefs:
                try:
                    print(f"🌐 Visiting: {href}")
                    await page.goto(href)
                    await page.wait_for_load_state("networkidle")
                    body = await page.query_selector("body")
                    content = await body.inner_text() if body else ""
                    post_date = extract_date_from_text_or_url(content, href)
                    domain = href.split("/")[2]

                    if post_date and post_date >= CUTOFF_DATE and domain not in trusted_domains:
                        print(f"⏭️ Skipped (post date {post_date.date()} after cutoff): {href}")
                        continue

                    content_with_link = f"{content}\n\n[Source]({href})"
                    contents.append(content_with_link)
                    print(f"✅ Extracted from: {href} (date: {post_date.date() if post_date else 'N/A'})")

                except Exception as e:
                    print(f"⚠️ Failed to extract from {href}: {e}")
                    continue

            with open("extracted_contents_filtered_v1.doc", "a", encoding="utf-8") as f:
                for content in contents:
                    f.write(content.strip() + "\n\n---\n\n")

            print(f"📁 Contents saved for URL: {start_url}")

        await context.close()
        await browser.close()
        print("✅ All done.")

# Run the scraping function
if __name__ == "__main__":
    asyncio.run(scrape())
