from bs4 import BeautifulSoup
import re

with open("challenge.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

result_chars = []

def match_pattern(tag):

    section_ok = False
    article_ok = False
    div_ok = False

    p = tag.parent
    while p:
        if p.name == "section":
            data_id = p.get("data-id", "")
            if data_id.startswith("92"):
                section_ok = True

        if p.name == "article":
            data_class = p.get("data-class", "")
            if data_class.endswith("45"):
                article_ok = True

        if p.name == "div":
            data_tag = p.get("data-tag", "")
            if "78" in data_tag:
                div_ok = True

        p = p.parent

    return section_ok and article_ok and div_ok


for b in soup.find_all("b", class_="ref"):
    if match_pattern(b):
        val = b.get("value")
        if val:
            result_chars.append(val)

hidden_url = "".join(result_chars)
print("Hidden URL:", hidden_url)
