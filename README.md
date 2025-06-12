# fullsail_scanner

Utility to subscribe to Sui on-chain events. It is designed so you can get alerts whenever
specific Move events occur (for example deposit events on your DEX).

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   - `MOVE_EVENT_TYPE`: Struct tag of the event to monitor, e.g. `0x123::my_dex::DepositEvent`.
   - `WEBHOOK_URL` (optional): HTTP endpoint to post events to. If not set, events are printed.
   - `SUI_WS_URL` (optional): Websocket RPC URL. Defaults to `wss://fullnode.mainnet.sui.io:443`.

3. Run the listener:
   ```bash
   python scanner.py
   ```

The script connects to the Sui websocket RPC using `suix_subscribeEvent` and forwards any
received events to the webhook if configured.
