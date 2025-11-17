from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import get_engine, get_db_session
from entities import ChatMessage

from sqlmodel import select
from typing import List

app = FastAPI(title="MiniChat v2")

# --- Archivos estáticos ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="views")

engine = get_engine()

# Conexiones WebSocket activas
clientes: List[WebSocket] = []


@app.on_event("startup")
def iniciar():
    # Crear tablas si no existen
    ChatMessage.metadata.create_all(engine)


@app.get("/", response_class=HTMLResponse)
def mostrar_chat(request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.websocket("/canal")
async def canal_chat(ws: WebSocket):
    await ws.accept()
    clientes.append(ws)

    # Enviar historial
    with get_db_session() as db:
        historial = db.exec(select(ChatMessage)).all()
        for msg in historial:
            await ws.send_text(f"{msg.nick}: {msg.cuerpo}")

    try:
        while True:
            mensaje = await ws.receive_text()

            if ":" in mensaje:
                nick, cuerpo = mensaje.split(":", 1)

                with get_db_session() as db:
                    nuevo = ChatMessage(nick=nick.strip(), cuerpo=cuerpo.strip())
                    db.add(nuevo)
                    db.commit()

            # reenviar a todos
            for c in clientes:
                await c.send_text(mensaje)

    except:
        if ws in clientes:
            clientes.remove(ws)
