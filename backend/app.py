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

    print(f"[INFO] Fetched {response.url} with status {response.status_code} \n {response.text[:200]} ...")

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
    print(f"[INFO] SEO meta extracted: {result}")

    return result



from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import lmstudio as lms
import re, random, json, asyncio
from pathlib import Path

SERVER_API_HOST = "14.0.0.5:1234"
lms.configure_default_client(SERVER_API_HOST)
model = lms.llm("google/gemma-3-4b")

REPLACEMENTS_FILE = Path("replacements.json")


SYSTEM_PROMPT = ("""
# Роль

Ты — опытный SEO-специалист с многолетним опытом технической и контентной оптимизации сайтов.

Твоя задача — объективно оценивать качество SEO страницы исключительно по предоставленным данным.

# Входные данные

Пользователь передает:

- Домен
- Title
- Meta Description
- Meta Keywords (если есть)

Не предполагай наличие других данных.

# Правила анализа

Оцени только то, что действительно присутствует во входных данных.

Не придумывай проблемы и не выдумывай достоинства.

Если данных недостаточно для какого-либо вывода — честно скажи об этом.

Во время анализа обращай внимание на:

• длину Title;
• информативность Title;
• наличие ключевых слов;
• естественность текста;
• отсутствие переспама;
• привлекательность для пользователя;
• качество Meta Description;
• соответствие Description содержанию Title;
• наличие призыва к действию;
• возможное влияние на CTR;
• использование Meta Keywords (понимай, что современные поисковые системы практически не используют этот тег);
• общее качество SEO-оптимизации META-тегов.

# Оценка

Если META-теги выполнены качественно — обязательно отметь это.

Если обнаружены недостатки — перечисли только реальные замечания.

Не ищи проблемы ради критики.

Не хвали ради похвалы.

# Стиль ответа

Ответ должен состоять из 3–10 предложений.

Не используй списки.

Пиши спокойным профессиональным языком.

Не используй эмоциональные выражения.

Не преувеличивай.

Не используй сарказм.

# Запрещено

Не оценивай:

- дизайн;
- скорость сайта;
- код страницы;
- адаптивность;
- структуру HTML;
- перелинковку;
- Core Web Vitals;
- ссылки;
- качество контента.

Если этих данных нет во входной информации, не делай никаких выводов о них.

# Итог

В конце дай краткое общее заключение одним предложением:

- Отличная SEO-оптимизация META-тегов.
- Хорошая SEO-оптимизация с небольшими рекомендациями.
- Средняя SEO-оптимизация, есть что улучшить.
- Слабая SEO-оптимизация META-тегов.

Основанием для оценки должны быть только предоставленные данные.
""")


# =========================
# HELPERS
# =========================
def log(msg: str):
    print(msg, flush=True)


def load_replacements() -> dict:
    """
    Загружает словарь замен из JSON.
    """
    if not REPLACEMENTS_FILE.exists():
        return {}

    try:
        with open(REPLACEMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {str(k).lower(): str(v) for k, v in data.items()}
    except Exception as e:
        log(f"[WARN] Не удалось загрузить replacements.json: {e}")
        return {}
    

def preserve_case(original: str, replacement: str) -> str:
    """
    Сохраняет регистр оригинального слова:
    человек -> чел
    Человек -> Чел
    ЧЕЛОВЕК -> ЧЕЛ
    """
    if original.isupper():
        return replacement.upper()
    elif original[:1].isupper():
        return replacement.capitalize()
    return replacement


def replace_words(text: str, replacements: dict) -> str:
    """
    Заменяет слова по словарю только по границам слов.
    """
    if not replacements:
        return text

    pattern = r"\b(" + "|".join(map(re.escape, replacements.keys())) + r")\b"

    def repl(match):
        original = match.group(0)
        replacement = replacements.get(original.lower(), original)
        return preserve_case(original, replacement)

    return re.sub(pattern, repl, text, flags=re.IGNORECASE)


def naturalize_blya(text: str) -> str:
    """
    Делает речь более живой и слегка ебанутой, но не слишком.
    """
    # result = []

    # for ch in text:
    #     if ch == ".":
    #         if random.random() < 0.15:
    #             result.append(" бля")
    #         result.append(".")
    #     elif ch == "!":
    #         if random.random() < 0.10:
    #             result.append(" бля")
    #         result.append("!")
    #     elif ch == "?":
    #         if random.random() < 0.10:
    #             result.append(" бля")
    #         result.append("?")
    #     else:
    #         result.append(ch)

    # text = "".join(result)

    # text = re.sub(
    #     r"\b(ну|короче|слушай|вообще|просто)\b",
    #     lambda m: m.group(1) + (" бля" if random.random() < 0.4 else ""),
    #     text,
    #     flags=re.IGNORECASE
    # )

    # text = re.sub(r"\s{2,}", " ", text)
    return text


class FinalStreamExtractor:
    """
    На лету вытаскивает только содержимое final-ответа из потока модели.
    """

    def __init__(self):
        self.raw = ""
        self.in_final = False
        self.plain_mode = False
        self.output_pos = 0

    def feed(self, chunk: str) -> str:
        self.raw += chunk

        if self.plain_mode:
            return chunk

        if not self.in_final:
            marker = "<|channel|>final<|message|>"
            idx = self.raw.find(marker)
            if idx == -1:
                if "<|channel|>" not in self.raw and "<|start|>" not in self.raw:
                    self.plain_mode = True
                    return self.raw
                return ""
            self.in_final = True
            self.output_pos = idx + len(marker)

        visible = self.raw[self.output_pos:]

        stop_markers = [
            "<|end|>",
            "<|start|>",
            "<|channel|>",
            "<|message|>",
        ]
        cut_positions = [visible.find(m) for m in stop_markers if visible.find(m) != -1]
        if cut_positions:
            visible = visible[:min(cut_positions)]

        visible = re.sub(r"<\|.*?\|>", "", visible)

        already_printed = self.raw[self.output_pos:self.output_pos + len(visible)]
        self.output_pos += len(already_printed)

        return visible


# =========================
# CLIENT CHAT SESSIONS
# =========================
class ChatSession:
    def __init__(self):
        self.chat = lms.Chat(SYSTEM_PROMPT)
        self.lock = asyncio.Lock()


# на каждый websocket-клиент будет своя сессия
# если хочешь потом хранить по user_id/token — можно вынести отдельно
sessions = {}


# =========================
# WEBSOCKET
# =========================
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)

    session = ChatSession()
    sessions[client_id] = session

    log(f"[WS] Client connected: {client_id}")

    try:
        while True:
            user_input = await websocket.receive_text()
            user_input = user_input.strip()

            if not user_input:
                await websocket.send_json({
                    "type": "error",
                    "content": "Пустой запрос"
                })
                continue

            log(f"[WS] {client_id} -> {user_input!r}")

            async with session.lock:
                replacements = load_replacements()

                # Добавляем юзерское сообщение в чат
                session.chat.add_user_message(user_input)

                # Стрим от модели
                prediction_stream = model.respond_stream(
                    session.chat,
                    on_message=session.chat.append,
                )

                extractor = FinalStreamExtractor()
                pending = ""
                full_answer = ""

                try:
                    for fragment in prediction_stream:
                        chunk = fragment.content or ""
                        if not chunk:
                            continue

                        clean_piece = extractor.feed(chunk)
                        if not clean_piece:
                            continue

                        pending += clean_piece

                        # Отдаём только на естественной границе
                        split_matches = list(re.finditer(r"[.,!?]\s+|\n", pending))
                        if split_matches:
                            last_end = split_matches[-1].end()
                            to_send = pending[:last_end]
                            pending = pending[last_end:]

                            to_send = replace_words(to_send, replacements)
                            to_send = naturalize_blya(to_send)

                            full_answer += to_send

                            await websocket.send_json({
                                "type": "chunk",
                                "content": to_send
                            })

                            # маленькая уступка event loop, чтобы не залипало
                            await asyncio.sleep(0)

                    # Хвост
                    if pending.strip():
                        pending = replace_words(pending, replacements)
                        pending = naturalize_blya(pending)
                        full_answer += pending

                        await websocket.send_json({
                            "type": "chunk",
                            "content": pending
                        })

                    await websocket.send_json({
                        "type": "done",
                        "content": full_answer
                    })

                    log(f"[WS] {client_id} <- done ({len(full_answer)} chars)")

                except Exception as e:
                    log(f"[ERR] Stream error for {client_id}: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Ошибка генерации: {str(e)}"
                    })

    except WebSocketDisconnect:
        log(f"[WS] Client disconnected: {client_id}")

    except Exception as e:
        log(f"[ERR] WebSocket fatal error {client_id}: {e}")

    finally:
        sessions.pop(client_id, None)