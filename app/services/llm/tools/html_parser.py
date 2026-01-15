import bs4
import urllib.request
import ssl
import certifi


def html_parser(url: str):
    ctx = ssl.create_default_context(cafile=certifi.where())

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    html = urllib.request.urlopen(req, context=ctx).read()
    soup = bs4.BeautifulSoup(html, "html.parser")

    main_tag = soup.find("main") or soup
    paragraphs = main_tag.find_all("p")

    texts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            texts.append(text)

    return "\n\n".join(texts) if texts else None