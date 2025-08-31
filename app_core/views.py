import os, json, requests, time, io, base64, qrcode
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import random

# ---------- ENVIRONMENT ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", None)
QUICKNODE_RPC_URL = os.getenv("QUICKNODE_RPC_URL", settings.BASE_TESTNET_RPC_URL)


# ---------- HOME ----------
def index(request):
    """Landing page"""
    return render(request, "app_core/index.html")


# ---------- WALLET ----------
def wallet_page(request):
    """Wallet demo page"""
    return render(request, "app_core/wallet.html", {
        "rpc_url": QUICKNODE_RPC_URL
    })

def wallet_qr_page(request):
    """WalletConnect QR demo page"""
    return render(request, "app_core/wallet_qr.html")

def wallet_qr_api(request):
    """Generate WalletConnect QR code + URI"""
    wc_uri = "wc:test-session@2?relay-protocol=irn&symKey=demo123456789"

    qr = qrcode.make(wc_uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    return JsonResponse({
        "uri": wc_uri,
        "qr": f"data:image/png;base64,{img_b64}"
    })


# ---------- HEALTH ----------
def health_page(request):
    """Health check page"""
    return render(request, "app_core/health.html")

def health_data(request):
    """Return QuickNode latency metrics as JSON"""
    start = time.time()
    try:
        resp = requests.post(QUICKNODE_RPC_URL, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_blockNumber",
            "params": []
        }, timeout=3)
        web3_ok = resp.status_code == 200
    except Exception:
        web3_ok = False

    latency = round((time.time() - start) * 1000, 2)
    return JsonResponse({
        "timestamp": int(time.time()),
        "db": False,
        "web3": web3_ok,
        "latency_ms": latency
    })


# ---------- CRYPTO LATENCY (NEW) ----------
def crypto_latency_data(request):
    """Fetch crypto data (market cap < $10M) and return latency stats"""
    start = time.time()
    try:
        resp = requests.get("https://api.coinlore.net/api/tickers/?start=0&limit=20", timeout=5)
        latency = round((time.time() - start) * 1000, 2)
        data = resp.json().get("data", [])
    except Exception as e:
        return JsonResponse({"error": "API fetch failed", "details": str(e)}, status=500)

    # filter coins with market cap < $10M
    candidates = [
        {
            "symbol": c["symbol"],
            "name": c["name"],
            "price_usd": c["price_usd"],
            "market_cap_usd": float(c["market_cap_usd"])
        }
        for c in data if c.get("market_cap_usd") and float(c["market_cap_usd"]) < 10_000_000
    ]

    lowest = candidates[0] if candidates else {}

    return JsonResponse({
        "request_latency_ms": latency,
        "lowest_valued_coin": lowest,
        "all_candidates": candidates[:5]  # send top 5 small-cap coins
    })


# ---------- GROQ CHAT ----------
def groq_chat_ui(request):
    """Render Groq chatbot page"""
    return render(request, "app_core/groq_chat_ui.html")

@csrf_exempt
def groq_chat_api(request):
    """Chat endpoint to call Groq API"""
    if not GROQ_API_KEY:
        return JsonResponse({"error": "Missing GROQ_API_KEY in environment"}, status=500)

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body.decode())
        message = body.get("message", "")
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not message:
        return JsonResponse({"error": "No message provided"}, status=400)

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7
            },
            timeout=15
        )
        data = resp.json()
        answer = (
            data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "No response")
        )
        return JsonResponse({"ok": True, "answer": answer})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------- QUICKNODE SIMULATION ----------
def simulate_page(request):
    """Render QuickNode Simulation demo UI"""
    return render(request, "app_core/simulate.html")

@csrf_exempt
def simulate_api(request):
    """Perform a simple QuickNode simulation"""
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required"}, status=405)

    if not QUICKNODE_RPC_URL:
        return JsonResponse({"ok": False, "error": "Missing QUICKNODE_RPC_URL"}, status=500)

    try:
        data = json.loads(request.body)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [
                {
                    "to": data.get("to", "0x0000000000000000000000000000000000000000"),
                    "data": data.get("data", "0x")
                },
                "latest"
            ]
        }
        resp = requests.post(QUICKNODE_RPC_URL, json=payload, timeout=5)
        return JsonResponse({"ok": True, "response": resp.json()})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


# ---------- GROQ TEST UI ----------
def groq_test_ui(request):
    """Render Groq test dashboard"""
    return render(request, "app_core/groq_test_ui.html")

def upcoming(request):
    """Render the Upcoming section page"""
    return render(request, "app_core/upcoming.html")

def upcoming_page(request):
    """Render Upcoming / Future Plans section"""
    return render(request, "app_core/upcoming.html")

def upcoming_data(request):
    """Return random demo data for graphs"""
    sample = {
        "timestamp": int(time.time()),
        "gas_savings": random.randint(5, 20),       # %
        "latency_reduction": random.randint(50,200),# ms
        "autonomy_level": random.choice(["Manual","Semi-Auto","Full-Auto"])
    }
    return JsonResponse(sample)
