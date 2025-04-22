# YoPhonePy - Python Client for YoPhone Bot API

YoPhonePy is a Python client library for interacting with the [YoPhone Bot API](https://yoai.yophone.com). It provides easy-to-use methods for polling messages, handling commands, sending messages with media or buttons, and configuring webhooks.

## Features

- Poll for new messages and events
- Register command and message handlers
- Send messages, media, and buttons
- Configure webhooks
- Get bot and webhook information

## Installation

Install the library from PyPI:

```bash
pip install yophonepy
```

## Getting Started

### 1. Obtain an API Key
Register on the YoPhone platform to get your API key.

### 2. Set API Key
You can set your API key as an environment variable:

```bash
export YOPHONE_API_KEY="your_api_key_here"
```

Or pass it directly to the `YoPhonePy` class:

```python
from yophonepy import YoPhonePy

bot = YoPhonePy(api_key="your_api_key_here")
```

### 3. Write Your Bot

```python
from yophonepy import YoPhonePy, Message

bot = YoPhonePy(api_key="your_api_key_here")

@bot.command_handler("start")
def start_handler(msg: Message):
    bot.send_message(msg.chat_id, "Hello! How can I assist you today?")

@bot.message_handler
def echo_handler(raw_data):
    msg = Message.from_dict(raw_data)
    bot.send_message(msg.chat_id, f"You said: {msg.text}")

if __name__ == "__main__":
    bot.start_polling(interval=2)
```

### Alternative Usage Example

You can also register handlers and initialize the bot programmatically:

```python
from yophonepy import YoPhonePy

def start_command(message: Message):
    start_text = f"""
    Welcome to YoPhonePy Bot, {message.sender.first_name}! \n
    """
    bot.send_message(message.chat_id, start_text)


def help_command(message: Message):
    help_text = f"""
    Welcome to YoPhonePy Bot, {message.sender.first_name}! \n
    """
    bot.send_message(message.chat_id, help_text)


if __name__ == "__main__":
    bot = YoPhonePy(
        api_key=your_api_key_here
    )

    bot.command_handler("start")(start_command)
    bot.command_handler("help")(help_command)

    # Start polling for updates
    bot.start_polling(interval=3)
```

## Sending Media and Buttons

### Send Files:
```python
bot.send_files(chat_id="123456", file_paths=["/path/to/file1.png"], caption="Here is your file!")
```

### Send Buttons:
```python
bot.send_message_with_buttons(
    chat_id="123456",
    text="Choose an option:",
    options=[{"text": "Option 1", "value": "opt1"}, {"text": "Option 2", "value": "opt2"}]
)
```

## Webhooks

### Set a Webhook:
```python
bot.set_webhook("https://yourdomain.com/webhook")
```

### Get Webhook Info:
```python
bot.get_webhook_info()
```

### Remove Webhook:
```python
bot.remove_webhook()
```

## Utilities

- `configure_commands(commands: List[Dict[str, str]])` — Set available slash commands
- `get_bot_info()` — Fetch bot metadata
- `get_channel_user_status(channel_id, user_id)` — Get user's status in a channel

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

For more information, refer to the official [YoPhone API Documentation](https://bots.yophone.com/docs/intro).

