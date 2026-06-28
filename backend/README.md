# SEO Crawler Backend

Небольшой API-сервис на FastAPI для быстрой оценки SEO-метаданных веб-страницы.

## Что делает

Сервис принимает URL и возвращает основные SEO-сигналы:
- HTTP-статус и финальный URL (после редиректов)
- `title`
- `description`, `keywords`, `robots`
- `cuserical`
- `charset`, `language`, `viewport`
- `favicon`
- Open Graph (`og:*`)
- Twitter Cards (`twitter:*`)

## Стек

- Python
- FastAPI
- httpx
- BeautifulSoup4 + lxml

## Быстрый старт

1. Установить зависимости:

```bash
pip install fastapi uvicorn httpx beautifulsoup4 lxml
```

2. Запустить сервер:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# or

uvicorn app:app --reload
```

3. Открыть Swagger UI:

- `http://localhost:8000/docs`

## API

### POST `/seo/meta`

Тело запроса:

```json
{
  "url": "https://example.com"
}
```

Пример `curl`:

```bash
curl -X POST "http://localhost:8000/seo/meta" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

Пример ответа (сокращённо):

```json
{
  "url": "https://example.com/",
  "status": 200,
  "title": "Example Domain",
  "description": "...",
  "keywords": null,
  "robots": null,
  "cuserical": null,
  "charset": "utf-8",
  "language": "en",
  "viewport": "width=device-width, initial-scale=1",
  "favicon": "https://example.com/favicon.ico",
  "open_graph": {
    "title": null,
    "description": null,
    "image": null,
    "url": null,
    "type": null
  },
  "twitter": {
    "card": null,
    "title": null,
    "description": null,
    "image": null
  }
}
```

```zsh
sudo nano /etc/systemd/system/seo-crawler.service

[Unit]
Description=FastAPI application
After=network.target

[Service]
User=user
Group=user
WorkingDirectory=/home/user/meinewelt/fastapi
ExecStart=/home/user/meinewelt/fastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```



## Ограничения текущей версии

- Анализируется только HTML-ответ, без рендеринга JavaScript.
- Не выполняется технический аудит (robots.txt, sitemap.xml, Core Web Vitals, скорость и т.д.).
- Таймаут запроса: 15 секунд.

## Идеи для развития

- Добавить проверку заголовков H1/H2 и структуры контента.
- Добавить проверку `robots.txt` и `sitemap.xml`.
- Добавить базовый SEO score и рекомендации.
- Сохранение результатов в БД для истории проверок.
