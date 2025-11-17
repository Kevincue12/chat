from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import get_engine, get_db_session
from entities import ChatMessage
from sqlmodel import select
from typing import List
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="MiniChat v2")

# --- Archivos estáticos ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="views")

engine = get_engine()

# Lista de clientes WebSocket conectados
clientes: List[WebSocket] = []


@app.on_event("startup")
def startup():
    """Crear tablas al iniciar la app."""
    ChatMessage.metadata.create_all(engine)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.websocket("/canal")
async def canal_chat(ws: WebSocket):
    await ws.accept()
    clientes.append(ws)

    # --- Enviar historial persistente al nuevo cliente ---
    with get_db_session() as db:
        historial = db.exec(select(ChatMessage)).all()
        for msg in historial:
            await ws.send_text(f"{msg.nick}: {msg.cuerpo}")

    try:
        while True:
            mensaje = await ws.receive_text()

            # Guardar mensaje en la base de datos
            if ":" in mensaje:
                nick, cuerpo = mensaje.split(":", 1)

                with get_db_session() as db:
                    nuevo = ChatMessage(
                        nick=nick.strip(),
                        cuerpo=cuerpo.strip()
                    )
                    db.add(nuevo)
                    db.commit()

            # Reenviar el mensaje a TODOS los clientes conectados
            for cliente in clientes:
                await cliente.send_text(mensaje)

    except Exception:
        # Quitar cliente desconectado
        if ws in clientes:
            clientes.remove(ws)
