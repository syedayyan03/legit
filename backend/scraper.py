import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import re

# Max characters sent downstream — keeps AI prompts lean
MAX_CONTENT_CHARS = 8000

# Tags that hold meaningful job posting content
CONTENT_TAGS = ["article", "main", "section", "div", "p", "li", "h1", "h2", "h3", "h4", "td"]

# Tags that are structural noise
NOISE_TAGS = ["script", "style", "noscript", "header", "footer", "nav",
              "aside", "form", "iframe", "svg", "button", "input"]


def extract_main_content(soup: BeautifulSoup) -> str:
    """
    Prefer <main>, <article>, or a high-density content div.
    Falls back to full body text. Strips nav/footer/script noise first.
    """
    # Remove noise tags before any extraction
    for tag in soup(NOISE_TAGS):
        tag.decompose()

    # Try semantic containers first
    for selector in ["main", "article", "[role='main']", ".job-description",
                     "#job-description", ".description", "#description",
                     ".posting-description", ".details"]:
        node = soup.select_one(selector)
        if node:
            return _clean_text(node.get_text(separator="\n"))

    # Heuristic: find the <div> with the most paragraph children
    best_div, best_score = None, 0
    for div in soup.find_all("div"):
        score = len(div.find_all(["p", "li", "h2", "h3"]))
        if score > best_score:
            best_score, best_div = score, div

    if best_div and best_score >= 3:
        return _clean_text(best_div.get_text(separator="\n"))

    # Full-body fallback
    body = soup.find("body")
    return _clean_text((body or soup).get_text(separator="\n"))


def _clean_text(raw: str) -> str:
    """Collapse blank lines and strip leading/trailing whitespace per line."""
    lines = [ln.strip() for ln in raw.splitlines()]
    # Remove duplicate blank lines
    cleaned, prev_blank = [], False
    for ln in lines:
        is_blank = ln == ""
        if is_blank and prev_blank:
            continue
        cleaned.append(ln)
        prev_blank = is_blank
    return "\n".join(cleaned).strip()


def detect_is_job(title: str, text: str) -> bool:
    """
    Three-tier job detection — must pass at least one strong signal.
    Uses the first 3000 chars of text to avoid footer noise swamping the score.
    """
    sample = text[:3000].lower()
    title_lower = title.lower()

    # Tier 1 — title clearly says "job"
    title_job_words = ["job", "career", "hiring", "opening", "position",
                       "vacancy", "recruitment", "opportunity", "role"]
    if any(w in title_lower for w in title_job_words):
        return True

    # Tier 2 — unmistakable job-posting phrases in the top of the page
    strong_phrases = [
        "job description", "key responsibilities", "what you will do",
        "what we're looking for", "years of experience", "equal opportunity employer",
        "we are hiring", "join our team", "salary range", "apply now",
        "minimum qualifications", "preferred qualifications", "about the role",
        "about this role", "you will be responsible", "full-time", "part-time",
        "remote work", "work from home", "hybrid role",
    ]
    if any(phrase in sample for phrase in strong_phrases):
        return True

    # Tier 3 — cluster of generic job words (must have 4+, not 3, to reduce false positives)
    generic_words = [
        "candidate", "applicant", "resume", "cv", "interview",
        "hiring", "vacancy", "benefits", "compensation", "onboarding",
        "department", "reporting to", "qualification", "requirement",
    ]
    if sum(1 for w in generic_words if w in sample) >= 4:
        return True

    return False


async def scrape_job_page(url: str) -> dict:
    try:
        print(f"Scraping URL with Playwright: {url}", flush=True)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()

            # --- Navigation ---
            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            except Exception as e:
                await browser.close()
                return {
                    "success": False,
                    "error": "Link Does Not Exist",
                    "not_found": True,
                    "status_code": 404,
                }

            if not response or response.status == 404:
                await browser.close()
                return {
                    "success": False,
                    "error": "Link Does Not Exist",
                    "not_found": True,
                    "status_code": 404,
                }

            status_code = int(response.status)

            if status_code >= 400:
                await browser.close()
                if status_code in [400, 401, 403, 429]:
                    return {
                        "success": True,
                        "title": f"Access Restricted ({status_code})",
                        "description": "",
                        "content": (
                            f"The website returned a {status_code} error, "
                            f"typically indicating anti-bot protection or rate limiting. URL: {url}"
                        ),
                        "type": "Protected Website",
                        "sensitive_fields": [],
                        "status_code": status_code,
                        "is_job": True,
                    }
                return {
                    "success": False,
                    "error": f"HTTP Error: {status_code}",
                    "status_code": status_code,
                }

            # --- Wait for JS-heavy content ---
            # Use a combined strategy: try networkidle, fall back to a timed wait.
            # This avoids hanging on sites that never fully reach networkidle.
            try:
                await asyncio.wait_for(
                    page.wait_for_load_state("networkidle"),
                    timeout=8,          # seconds (asyncio, not ms)
                )
            except (asyncio.TimeoutError, Exception):
                pass  # Timed out — proceed with what's loaded

            # Extra pause for lazy-rendered content (Workday, Greenhouse, etc.)
            await page.wait_for_timeout(2500)

            # Scroll to bottom once to trigger lazy-load sections
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            html_content = await page.content()
            await browser.close()

        # --- Parsing ---
        soup = BeautifulSoup(html_content, "html.parser")

        # Title
        title = "Untitled Job"
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        elif soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()

        # Main content (structured, noise-stripped)
        content = extract_main_content(soup)

        # Trim to avoid bloating downstream AI calls
        if len(content) > MAX_CONTENT_CHARS:
            content = content[:MAX_CONTENT_CHARS] + "\n...[truncated]"

        # Meta description
        meta_description = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if not meta:
            meta = soup.find("meta", property="og:description")
        if meta and meta.get("content"):
            meta_description = meta["content"].strip()

        # URL type
        url_type = "Website"
        if "forms.google.com" in url or "docs.google.com/forms" in url:
            url_type = "Google Form"

        # Sensitive field detection — run on full content, not just title
        sensitive_fields = []
        content_lower = content.lower()
        if re.search(r"\bphone\b|\bmobile\b|\bcontact number\b", content_lower):
            sensitive_fields.append("Phone Number")
        if re.search(r"\bemail\b|\be-mail\b", content_lower):
            sensitive_fields.append("Email")
        if re.search(r"\bbank\b|\baccount\b|\bupi\b|\baadhaar\b|\bpan\b|\bcard number\b", content_lower):
            sensitive_fields.append("Financial/Identity Info")

        # Job detection
        is_job = detect_is_job(title, content)

        print(f"Scrape successful: {title} (is_job: {is_job})")
        return {
            "success": True,
            "title": title,
            "description": meta_description,
            "content": content,
            "type": url_type,
            "sensitive_fields": sensitive_fields,
            "status_code": status_code,
            "is_job": is_job,
        }

    except PlaywrightTimeoutError:
        return {
            "success": False,
            "error": "Timeout Error: The website took too long to respond.",
            "status_code": 504,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}",
            "status_code": 500,
        }


if __name__ == "__main__":
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.linkedin.com/jobs/view/123456789"
    print(asyncio.run(scrape_job_page(test_url)))