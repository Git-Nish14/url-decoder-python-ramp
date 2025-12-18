import re
import sys
import requests
from bs4 import BeautifulSoup

CHALLENGE_URL = "https://tns4lpgmziiypnxxzel5ss5nyu0nftol.lambda-url.us-east-1.on.aws/challenge"


def extract_hidden_url_bs4(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    chars = []
    for b in soup.find_all("b", class_="ref"):
        val = b.get("value")
        if not val or val == "*":
            continue

        div = b.find_parent("div", attrs={"data-tag": True})
        article = b.find_parent("article", attrs={"data-class": True})
        section = b.find_parent("section", attrs={"data-id": True})

        if not div or not article or not section:
            continue

        data_id = section.get("data-id", "")
        data_class = article.get("data-class", "")
        data_tag = div.get("data-tag", "")
        if data_id.startswith("92") and data_class.endswith("45") and ("78" in data_tag):
            chars.append(val)

    return "".join(chars).strip()


def extract_hidden_url_playwright(url: str) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError(
            "Playwright not installed.\n"
            "Install:\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium\n"
        ) from e

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        chars = page.evaluate(
            """
            () => {
              const bs = Array.from(document.querySelectorAll('b.ref[value]'));
              const ok = (b) => {
                const div = b.closest('div[data-tag]');
                const art = b.closest('article[data-class]');
                const sec = b.closest('section[data-id]');
                if (!div || !art || !sec) return false;

                const dataId = sec.getAttribute('data-id') || '';
                const dataClass = art.getAttribute('data-class') || '';
                const dataTag = div.getAttribute('data-tag') || '';

                return dataId.startsWith('92') && dataClass.endsWith('45') && dataTag.includes('78');
              };

              return bs.filter(ok).map(b => b.getAttribute('value')).filter(v => v && v !== '*');
            }
            """
        )

        browser.close()

    return "".join(chars).strip()


def main():
    print("Fetching challenge page...")
    r = requests.get(CHALLENGE_URL, timeout=30)
    r.raise_for_status()
    html = r.text

    # quick sanity debug
    print("Content-Type:", r.headers.get("Content-Type", ""))
    print("Downloaded chars:", len(html))

    hidden_url = extract_hidden_url_bs4(html)

    if not hidden_url:
        print("No hidden URL found in raw HTML. Falling back to Playwright (JS-rendered DOM)...")
        hidden_url = extract_hidden_url_playwright(CHALLENGE_URL)

    print("Hidden URL:", hidden_url)

    if not hidden_url:
        print("ERROR: still empty. Something is off with the DOM pattern or page rendering.")
        sys.exit(1)

    # If the extracted URL ever comes out schemeless, fix it:
    if not re.match(r"^https?://", hidden_url):
        hidden_url = "https://" + hidden_url.lstrip("/")

    flag_word = requests.get(hidden_url, timeout=30).text.strip()
    print("FLAG WORD:", flag_word)


if __name__ == "__main__":
    main()
