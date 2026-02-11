# fullsail_scanner

Minimal Sui blockchain event monitor using WebSocket RPC subscription.

## Commands

| Command | Description |
|---------|-------------|
| `python scanner.py` | Start event listener |

## Architecture

```
fullsail_scanner/
  scanner.py    # Async WebSocket listener (57 lines)
  .env          # Configuration (gitignored)
```

**Flow:** WebSocket → `suix_subscribeEvent` → Filter by Move event type → Webhook/stdout

## Environment

Required:
- `MOVE_EVENT_TYPE` - Move event struct to monitor (e.g., `0x123::pool::DepositEvent`)

Optional:
- `SUI_WS_URL=wss://fullnode.mainnet.sui.io:443` - RPC endpoint
- `WEBHOOK_URL` - POST events here; prints to console if unset

## Gotchas

- `MOVE_EVENT_TYPE` is mandatory; script fails without it
- No reconnection logic; crashes on connection loss
- No persistence or database; events are fire-and-forget
- Runs indefinitely; Ctrl+C to exit
- Defaults to Mainnet; no testnet auto-detection
- `.env` was previously tracked with Telegram token (now untracked + gitignored)
