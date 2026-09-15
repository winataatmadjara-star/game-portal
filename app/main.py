import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# Memuat konfigurasi dari file .env
load_dotenv()

app = FastAPI(title="Game Portal Professional", version="1.0.0")

# Konfigurasi Environment & Middleware
SECRET_KEY = os.getenv("SECRET_KEY", "rahasia-negara-gameportal-2026")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- INCLUDE ROUTERS (Pastikan bagian ini AKTIF) ---
from app.routers import web, api, auth
app.include_router(web.router)
app.include_router(api.router, prefix="/api")
app.include_router(auth.router)


# --- ROUTE LOGIN UTAMA (Gabungan Member & Admin) ---
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user"):
        if request.session.get("is_admin"):
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        return RedirectResponse(url="/", status_code=303)
    return "<h1>Halaman Login</h1>..."


@app.post("/login")
async def login_process(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        request.session["user"] = ADMIN_USER
        request.session["is_admin"] = True
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    return RedirectResponse(url="/login?error=1", status_code=303)


# --- ROUTE DASHBOARD ADMIN ---
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login", status_code=303)
    return "<h1>Selamat Datang di Panel Admin!</h1><a href='/logout'>Logout</a>"


# --- ROUTE LOGOUT ---
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)