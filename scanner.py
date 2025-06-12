import asyncio
import json
import os
from pathlib import Path
from typing import Any

import requests
import websockets
from dotenv import load_dotenv

# Load variables from a .env file located next to this script, if present.
env_path = Path(__file__).resolve().with_name(".env")
load_dotenv(env_path)

# Configuration via environment variables
SUI_WS_URL = os.getenv("SUI_WS_URL", "wss://fullnode.mainnet.sui.io:443")
SUI_RPC_URL = os.getenv("SUI_RPC_URL", "https://fullnode.mainnet.sui.io")
USE_WEBSOCKET = os.getenv("USE_WEBSOCKET", "true").lower() not in {"0", "false"}
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
EVENT_TYPE = os.getenv("MOVE_EVENT_TYPE")
PACKAGE_ID = os.getenv("MOVE_PACKAGE_ID")
MODULE = os.getenv("MOVE_MODULE")
EVENT_STRUCT = os.getenv("MOVE_EVENT_STRUCT")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if EVENT_TYPE is None and PACKAGE_ID and MODULE and EVENT_STRUCT:
    EVENT_TYPE = f"{PACKAGE_ID}::{MODULE}::{EVENT_STRUCT}"

if EVENT_TYPE is None:
    raise SystemExit(
        "Set MOVE_EVENT_TYPE or MOVE_PACKAGE_ID, MOVE_MODULE and MOVE_EVENT_STRUCT"
    )

async def send_alert(event: Any) -> None:
    """Send event data to the configured destinations."""
    delivered = False
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": json.dumps(event, indent=2),
        }
        try:
            resp = requests.post(tg_url, json=payload, timeout=10)
            resp.raise_for_status()
            print(f"Telegram alert delivered: {resp.status_code}")
            delivered = True
        except Exception as exc:
            print(f"Failed to send Telegram alert: {exc}")

    if WEBHOOK_URL:
        try:
            resp = requests.post(WEBHOOK_URL, json=event, timeout=10)
            resp.raise_for_status()
            print(f"Webhook alert delivered: {resp.status_code}")
            delivered = True
        except Exception as exc:
            print(f"Failed to deliver webhook alert: {exc}")

    if not delivered:
        print("No alert destination configured; event:\n", json.dumps(event, indent=2))

async def listen() -> None:
    """Subscribe to Move event type and forward events."""
    filter_payload = {"MoveEventType": EVENT_TYPE}
    sub_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "suix_subscribeEvent",
        "params": [filter_payload],
    }

    while True:
        try:
            async with websockets.connect(SUI_WS_URL) as ws:
                await ws.send(json.dumps(sub_msg))
                raw = await ws.recv()
                resp = json.loads(raw)
                sub_id = resp.get("result")
                if not sub_id:
                    raise RuntimeError(f"Subscription failed: {resp}")
                print(f"Subscribed with id {sub_id} for {EVENT_TYPE}")
                while True:
                    msg = await ws.recv()
                    event = json.loads(msg)
                    await send_alert(event)
        except Exception as exc:
            print(f"Listener error: {exc}; reconnecting in 5s")
            await asyncio.sleep(5)

async def poll() -> None:
    """Poll events over HTTP when websockets are unavailable."""
    cursor = None
    filter_payload = {"MoveEventType": EVENT_TYPE}
    while True:
        params = [filter_payload, cursor, 50, False]
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "suix_queryEvents",
            "params": params,
        }
        try:
            resp = requests.post(SUI_RPC_URL, json=payload, timeout=10)
            resp.raise_for_status()
            result = resp.json().get("result", {})
            for item in result.get("data", []):
                await send_alert(item)
            cursor = result.get("nextCursor", cursor)
        except Exception as exc:
            print(f"Poll error: {exc}")
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        if USE_WEBSOCKET:
            try:
                asyncio.run(listen())
            except websockets.InvalidStatusCode as exc:
                print(f"Websocket failed ({exc.status_code}); falling back to HTTP polling")
                asyncio.run(poll())
        else:
            asyncio.run(poll())
    except KeyboardInterrupt:
        print("Exiting")
