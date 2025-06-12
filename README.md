# fullsail_scanner

Utility to subscribe to Sui on-chain events. It is designed so you can get alerts whenever
specific Move events occur (for example deposit events on your DEX).

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and adjust the values, or set the following environment variables manually:
   - Either provide `MOVE_EVENT_TYPE` with the full struct tag, **or** set all of
     `MOVE_PACKAGE_ID`, `MOVE_MODULE`, and `MOVE_EVENT_STRUCT` to build it.
   - `WEBHOOK_URL` (optional): HTTP endpoint to post events to. If not set, events are printed.
   - `SUI_WS_URL` (optional): Websocket RPC URL. Defaults to `wss://fullnode.mainnet.sui.io:443`.
   - `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (optional): if both are provided, events are also sent to the specified Telegram chat using the bot API.

3. Run the listener:
   ```bash
   python scanner.py
   ```

The script connects to the Sui websocket RPC using `suix_subscribeEvent` and forwards any
received events to the webhook if configured.

### Example

To monitor deposits from the Full Sail package you can set:

```bash
export MOVE_PACKAGE_ID=0xe1b7d5fd116fea5a8f8e85c13754248d56626a8d0a614b7d916c2348d8323149
export MOVE_MODULE=vault
export MOVE_EVENT_STRUCT=DepositEvent
python scanner.py
```

This will subscribe to `0xe1b7d5fd116fea5a8f8e85c13754248d56626a8d0a614b7d916c2348d8323149::vault::DepositEvent` and
forward any matches to Telegram or the webhook if configured.

### Example with Telegram

If you created a bot with token `YOUR_TELEGRAM_BOT_TOKEN` and know the chat ID
to post to, set these variables before running the scanner:

```bash
export MOVE_PACKAGE_ID=0xe1b7d5fd116fea5a8f8e85c13754248d56626a8d0a614b7d916c2348d8323149
export MOVE_MODULE=vault
export MOVE_EVENT_STRUCT=DepositEvent
export TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
export TELEGRAM_CHAT_ID=<your_chat_id>
python scanner.py
```

Keep your bot token private. Anyone with the token can send messages using your
bot. After creating the bot you can [join our Telegram group](https://t.me/+4ZZQ3MQWsjAyNjQx)
and add the bot to receive alerts there. Use the `/getUpdates` API method or a
test message to determine the group chat ID. New members must send a message
in the chat before their chat ID will appear in the `/getUpdates` response.

### Running continuously

For unattended operation you can run the script under `systemd`. Create an
environment file (for example `/opt/fullsail_scanner/env`) by copying
`.env.example` and editing it, then reference it from a service unit similar to:

```ini
[Unit]
Description=Full Sail event scanner

[Service]
EnvironmentFile=/opt/fullsail_scanner/env
WorkingDirectory=/opt/fullsail_scanner
ExecStart=/usr/bin/python3 scanner.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start it with:

```bash
sudo systemctl enable fullsail_scanner
sudo systemctl start fullsail_scanner
```

`systemd` will keep the process running and automatically restart it if it
exits.
