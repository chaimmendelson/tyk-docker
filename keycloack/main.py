from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import json
import uvicorn

app = FastAPI()

# === CONFIG ===
KEYCLOAK_BASE_URL = "http://localhost:7380"
REALM = "dev"
CLIENT_ID = "test"
CLIENT_SECRET = "yXAH74bbtooBuQtEofHbxzfgCWKXEV30"
REDIRECT_URI = "http://localhost:4000/callback"

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
    <head>
        <title>Keycloak Token Viewer</title>
    </head>
    <body>
        <h2>Access Token Viewer</h2>
        <div id="output"><i>Loading token...</i></div>
        <br>
        <button onclick="window.location='/login'">🔁 Re-authenticate</button>
        <button onclick="logout()">🚪 Log out</button>
        <script>
            function decodeJwt(token) {
                try {
                    const base64 = token.split('.')[1];
                    const json = atob(base64.replace(/-/g, '+').replace(/_/g, '/'));
                    return JSON.stringify(JSON.parse(json), null, 4);
                } catch (e) {
                    return "Invalid token";
                }
            }

            function logout() {
                localStorage.removeItem("access_token");
                location.reload();
            }

            const token = localStorage.getItem("access_token");
            const output = document.getElementById("output");

            if (!token) {
                output.innerHTML = "<b>No token found</b><br><a href='/login'>Login</a>";
            } else {
                output.innerHTML = "<pre>" + decodeJwt(token) + "</pre>";
            }
        </script>
    </body>
    </html>
    """)

@app.get("/login")
def login_redirect():
    auth_url = (
        f"{KEYCLOAK_BASE_URL}/realms/{REALM}/protocol/openid-connect/auth"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("<h2>Error: Missing code</h2>")

    token_url = f"{KEYCLOAK_BASE_URL}/realms/{REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(token_url, data=data, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

    if res.status_code != 200:
        return HTMLResponse(f"<h2>Token exchange failed</h2><pre>{res.text}</pre>", status_code=res.status_code)

    tokens = res.json()
    access_token = tokens.get("access_token")

    return HTMLResponse(f"""
    <html>
    <body>
        <script>
            localStorage.setItem("access_token", {json.dumps(access_token)});
            window.location = "/";
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
