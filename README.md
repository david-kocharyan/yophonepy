# 📞 YoPhonePy

**YoPhonePy** is a Python client wrapper for interacting with the **YoPhone Bot API**. It provides utility methods for
polling messages, handling commands, sending media, and managing bot configurations.

---

## 🚀 Features

- Easy polling and message handling
- Command-specific routing
- Send text messages, buttons, and files
- Support for media URLs and file uploads
- Configure webhooks and bot commands

---

## 📦 Installation

```bash
  pip install yophonepy
```

---

## ⚙️ Configuration Parameters

When initializing the `YoPhonePy` client, you can provide the following arguments:

```python
bot = YoPhonePy(
    api_key="your_api_key_here",
    base_url="https://yoai.yophone.com/api/pub",  # Optional
    verbose=True  # Optional
)
```

### 🔑 `api_key` (Required)

Your personal or project-specific API key provided by the YoPhone platform. This authenticates your bot and allows it to
interact with the API.

### 🌐 `base_url` (Optional)

Defaults to `https://yoai.yophone.com/api/pub`.

### 📣 `verbose` (Optional)

Set to `True` to enable debug logs and helpful messages printed to the console. Useful during development.

---

### 1. Function-Based (with `if __name__ == "__main__"`)

```python
from yophonepy import YoPhonePy, Message
from typing import Dict, Any


def start_command(msg: Message):
    bot.send_message(msg.chat_id, "Start Command!")


def help_command(msg: Message):
    bot.send_message(msg.chat_id, "Help Command!")


def fallback(msg_data: Dict[str, Any]):
    msg = Message.from_dict(msg_data)
    bot.send_message(msg.chat_id, f"Echo: {msg.text}")


def main():
    global bot
    bot = YoPhonePy(api_key="your_api_key")

    bot.command_handler("start")(start_command)
    bot.command_handler("help")(help_command)
    bot.message_handler(fallback)

    bot.start_polling()


if __name__ == "__main__":
    main()
```

---

### 2. Class-Based Example

```python
from yophonepy import YoPhonePy, Message
from typing import Dict, Any


class CocktailBot:
    def __init__(self, api_key: str):
        self.bot = YoPhonePy(api_key=api_key)
        self.bot.command_handler("start")(self.start)
        self.bot.command_handler("help")(self.help)
        self.bot.message_handler(self.fallback)

    def start(self, message: Message):
        self.bot.send_message(message.chat_id, "Start Command!")

    def help(self, message: Message):
        self.bot.send_message(message.chat_id, "Help Command!")

    def fallback(self, msg_data: Dict[str, Any]):
        msg = Message.from_dict(msg_data)
        self.bot.send_message(msg.chat_id, f"Echo: {msg.text}")

    def run(self):
        self.bot.start_polling()


if __name__ == "__main__":
    CocktailBot(api_key="your_api_key").run()
```

---

### 3. Decorator-Based Example

```python
from yophonepy import YoPhonePy, Message
from typing import Dict, Any

bot = YoPhonePy(api_key="your_api_key")


@bot.command_handler("start")
def start_command(msg: Message):
    bot.send_message(msg.chat_id, "Start Command!")


@bot.command_handler("help")
def help_command(msg: Message):
    bot.send_message(msg.chat_id, "Help Command!")


@bot.message_handler
def fallback(msg_data: Dict[str, Any]):
    msg = Message.from_dict(msg_data)
    bot.send_message(msg.chat_id, f"Echo: {msg.text}")


if __name__ == "__main__":
    bot.start_polling()
```

### 4. Async-Based Example

If you want full asynchronous support, you can use AsyncYoPhonePy:

```python
import asyncio
from yophonepy import AsyncYoPhonePy, Message
from typing import Dict, Any

bot = AsyncYoPhonePy(api_key="your_api_key")


@bot.command_handler("start")
async def start_command(msg: Message):
    await bot.send_message(msg.chat_id, "Start Command!")


@bot.command_handler("help")
async def help_command(msg: Message):
    await bot.send_message(msg.chat_id, "Help Command!")


@bot.message_handler
async def fallback(msg_data: Dict[str, Any]):
    msg = Message.from_dict(msg_data)
    await bot.send_message(msg.chat_id, f"Echo: {msg.text}")


async def main():
    await bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
```

🧠 Note: All handler functions must be **async def** when using **AsyncYoPhonePy**.

---

## 📌 Additional Examples

### ✅ Send a basic message

```python
bot.send_message(chat_id="123456", text="Hello from YoPhonePy!")
```

---

### 🛎 Send a message with buttons

```python
bot.send_message_with_buttons(
    chat_id="123456",
    text="Choose an option:",
    grid=2,
    options=[
        {"text": "Option 1", "callbackData": "opt1"},
        {"text": "Option 2", "callbackData": "opt2"}
    ]
)
```

---

### 📁 Send multiple files

```python
bot.send_files(
    chat_id="123456",
    file_paths=["./image.png", "./report.pdf"],
    caption="Here are your files."
)
```

---

### 🖼 Send message with external media URLs

```python
bot.send_message_with_media_url(
    chat_id="123456",
    text="Check this out:",
    media_urls=["https://example.com/photo.jpg"]
)
```

---

### 🧩 Configure bot commands list

```python
bot.configure_commands([
    {"command": "start", "description": "Start the bot"},
    {"command": "help", "description": "Display help information"}
])
```

---

### 🌐 Webhook management

```python
bot.set_webhook("https://yourdomain.com/webhook")  # Set webhook URL
info = bot.get_webhook_info()  # Get webhook info
bot.remove_webhook()  # Remove webhook
```

---

### 👤 Get bot info and channel user status

```python
info = bot.get_bot_info()

status = bot.get_channel_user_status(
    channel_id="my_channel_id",
    user_id="user_id_here"
)
```

---

### 🛑 Stop polling manually

```python
bot.stop_polling()
```

---

## 🧾 Markup Formatting

You can use murcap to easily build rich, readable, formatted messages for the YoPhone platform using Markdown-style
helpers.

#### Example: /info Command Using murcap

```python
from yophonepy import YoPhonePy, Message, murcap

bot = YoPhonePy(api_key="your_api_key_here")


@bot.command_handler("info")
def send_info(msg: Message):
    formatted = murcap.paragraph(
        murcap.header("Header"),
        murcap.subheader("Subheader"),
        murcap.bold("Bold Text Example"),
        murcap.italic("Italic Text Example"),
        murcap.underline("Underlined Text Example"),
        murcap.strikethrough("Strikethrough Text Example"),
        murcap.code("/start  /help  /info"),
        murcap.link("🔗 Markup Documentation", "https://yoai.yophone.com/docs/markup"),
        murcap.combine("Made with ❤️ using ", murcap.code("YoPhonePy"))
    )
    bot.send_message(msg.chat_id, formatted)
```

#### Renders as:

```markdown
### Header

## Subheader

** Bold Text Example **
*Italic Text Example*
__Underlined Text Example__
~Strikethrough Text Example~
`/start  /help  /info`
[🔗 Markup Documentation](https://yoai.yophone.com/docs/markup)
Made with ❤️ using `YoPhonePy`
```

---

## 📚 Documentation Reference

- **YoPhonePy GitHub**: [https://github.com/david-kocharyan/yophonepy](https://github.com/david-kocharyan/yophonepy)
- **Official API Reference (YoPhone)**: [https://yoai.yophone.com/docs/intro](https://yoai.yophone.com/docs/intro)
- **Issues & Support**: Use the [GitHub Issues page](https://github.com/david-kocharyan/yophonepy/issues) to report bugs
  or request features.

---

## 🧾 License

[MIT License](./LICENSE) — free for personal and commercial use.


