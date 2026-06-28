from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLRequest(BaseModel):
    url: str


def meta(soup, name):
    tag = soup.find("meta", attrs={"name": name})
    if tag:
        return tag.get("content")

    tag = soup.find("meta", attrs={"property": name})
    if tag:
        return tag.get("content")

    return None


@app.post("/seo/meta")
async def seo_meta(request: URLRequest):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "Chrome/137 Safari/537.36"
        )
    }

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15
    ) as client:

        try:
            response = await client.get(request.url, headers=headers)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.text, "lxml")

    favicon = None

    icon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    if icon:
        favicon = urljoin(str(response.url), icon.get("href"))

    canonical = None
    link = soup.find("link", rel="canonical")
    if link:
        canonical = link.get("href")

    result = {
        "url": str(response.url),
        "status": response.status_code,

        "title": soup.title.string.strip() if soup.title else None,

        "h1": soup.find("h1").get_text(strip=True) if soup.find("h1") else None,

        "description": meta(soup, "description"),
        "keywords": meta(soup, "keywords"),
        "robots": meta(soup, "robots"),

        "canonical": canonical,

        "charset": (
            soup.find("meta", charset=True).get("charset")
            if soup.find("meta", charset=True)
            else None
        ),

        "language": (
            soup.html.get("lang")
            if soup.html
            else None
        ),

        "viewport": meta(soup, "viewport"),

        "favicon": favicon,

        "open_graph": {
            "title": meta(soup, "og:title"),
            "description": meta(soup, "og:description"),
            "image": meta(soup, "og:image"),
            "url": meta(soup, "og:url"),
            "type": meta(soup, "og:type"),
        },

        "twitter": {
            "card": meta(soup, "twitter:card"),
            "title": meta(soup, "twitter:title"),
            "description": meta(soup, "twitter:description"),
            "image": meta(soup, "twitter:image"),
        }
    }

    return result