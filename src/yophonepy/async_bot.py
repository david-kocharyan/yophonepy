import asyncio
import aiohttp
import aiofiles
import os
from typing import Callable, Dict, Any, List, Optional
from yophonepy.utils import determine_mime_type, parse_update
from yophonepy.models import Message


class AsyncYoPhonePy:
    """
    Asynchronous Python client wrapper for interacting with the YoPhone Bot API.
    Provides utility methods for polling messages, handling commands,
    sending media, and configuring webhooks.
    """

    def __init__(self, api_key: str, base_url: str = "https://yoai.yophone.com/api/pub", verbose: bool = True):
        """
        Initializes the YoPhone bot client.

        Args:
            api_key (str): API key for authenticating with the YoPhone service.
            base_url (str): Optional custom base URL for the API.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.verbose = verbose

        self._message_callbacks: List[Callable[[Dict[str, Any]], Any]] = []
        self._command_callbacks: Dict[str, Callable[[Message], Any]] = {}

        self._polling_active = False

    def _log(self, message: str):
        if self.verbose:
            print(message)

    async def _make_request(
            self,
            method: str,
            endpoint: str,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[List[tuple]] = None,
            headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"

        # Merge default and custom headers
        default_headers = {"X-YoAI-API-Key": self.api_key}
        merged_headers = {**default_headers, **(headers or {})}

        async with aiohttp.ClientSession() as session:
            try:
                if files:
                    form = aiohttp.FormData()
                    for name, (filename, file_content, mime_type) in files:
                        form.add_field(name, file_content, filename=filename, content_type=mime_type)
                    if data:
                        form.add_field('data', str(data))
                    async with session.request(method, url, headers=merged_headers, data=form) as response:
                        response.raise_for_status()
                        if response.status == 200 and await response.text():
                            self._log(f"[AsyncYoPhonePy] ✅ Success: {endpoint}")
                            return await response.json()
                else:
                    async with session.request(method, url, headers=merged_headers, json=data) as response:
                        response.raise_for_status()
                        if response.status == 200 and await response.text():
                            self._log(f"[AsyncYoPhonePy] ✅ Success: {endpoint}")
                            return await response.json()
                return None
            except aiohttp.ClientError as err:
                self._log(f"[AsyncYoPhonePy] ❌ Error in {endpoint}: {err}")
                return None

    def message_handler(
            self,
            func: Callable[[Dict[str, Any]], None]
    ):
        """
        Registers a generic handler for incoming messages.
        """
        self._message_callbacks.append(func)
        return func

    def command_handler(self, command: str):
        """
        Registers a specific handler for a command (without leading slash).
        """

        def decorator(func: Callable[[Message], None]):
            self._command_callbacks[f"/{command}"] = func
            return func

        return decorator

    async def fetch_updates(self) -> List[Dict[str, Any]]:
        """
        Fetches new messages or events from YoPhone.
        """
        updates = await self._make_request("POST", "getUpdates")
        self._log(f"[AsyncYoPhonePy] 📦 Update received: {updates}")
        if updates and "data" in updates:
            return updates["data"]
        return []

    async def process_updates(self):
        """
        Handles and dispatches incoming updates to appropriate handlers.
        """
        for raw_update in await self.fetch_updates():
            try:
                parsed = parse_update(raw_update)
                msg_obj = Message.from_dict(parsed)

                if msg_obj.text and msg_obj.text.startswith("/"):
                    command = msg_obj.text.split()[0]
                    if command in self._command_callbacks:
                        await self._command_callbacks[command](msg_obj)
                        continue

                for handler in self._message_callbacks:
                    await handler(parsed)

            except Exception as ex:
                self._log(f"[AsyncYoPhonePy] ❌ Failed to process update: {ex}")

    async def start_polling(self, interval: int = 3):
        """
        Continuously polls for updates at a specified interval.

        Args:
            interval (int): Delay in seconds between polls.
        """
        self._log("[AsyncYoPhonePy] 🚀 Polling started. Press Ctrl+C to stop.")
        self._polling_active = True
        try:
            while self._polling_active:
                await self.process_updates()
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            self._log("\n[AsyncYoPhonePy] ⛔️ Polling stopped by user (Ctrl+C).")
            await self.stop_polling()
        finally:
            self._polling_active = False

    async def stop_polling(self):
        """
        Stops the polling loop gracefully.
        """
        self._log("[AsyncYoPhonePy] 🛑 Stopping polling loop...")
        self._polling_active = False

    async def send_message(
            self,
            chat_id: str,
            text: str
    ) -> Optional[Dict[str, Any]]:
        return await self._make_request("POST", "sendMessage", data={"to": chat_id, "text": text})

    async def send_message_with_options(
            self,
            chat_id: str,
            text: str,
            options: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        payload = {"to": chat_id, "text": text, "options": options}
        return await self._make_request("POST", "sendMessage", data=payload)

    async def send_message_with_buttons(
            self,
            chat_id: str,
            text: str,
            grid: int = 1,
            options: Optional[List[Dict[str, str]]] = None,
            inline_buttons: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "to": chat_id,
            "text": text,
            "buttons": {
                "grid": grid,
                "options": options or [],
                "inline_buttons": inline_buttons or []
            }
        }
        return await self._make_request("POST", "sendMessage", data=payload)

    async def send_files(
            self,
            chat_id: str,
            file_paths: List[str],
            caption: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        payload = {"to": chat_id, "text": caption or ""}
        file_data = []

        for path in file_paths:
            if not os.path.exists(path):
                self._log(f"[AsyncYoPhonePy] ❌ File does not exist: {path}")
                return None

            if os.path.getsize(path) > 50 * 1024 * 1024:
                self._log(f"[AsyncYoPhonePy] ❌ File exceeds 50MB limit: {path}")
                return None

            try:
                async with aiofiles.open(path, "rb") as f:
                    content = await f.read()
                mime_type = determine_mime_type(path)
                file_data.append(("file", (os.path.basename(path), content, mime_type)))
            except Exception as err:
                self._log(f"[AsyncYoPhonePy] ❌ Failed to read file {path}: {err}")
                return None

        return await self._make_request("POST", "sendMessage", data=payload, files=file_data)

    async def send_message_with_media_url(
            self,
            chat_id: str,
            text: str,
            media_urls: List[str]
    ) -> Optional[Dict[str, Any]]:
        payload = {"to": chat_id, "text": text, "mediaURLs": media_urls}
        return await self._make_request("POST", "sendMessage", data=payload)

    async def configure_commands(
            self,
            commands: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        response = await self._make_request("POST", "setCommands", data={"commands": commands})
        if response:
            self._log(f"[AsyncYoPhonePy] ✅ Commands configured successfully.")
        return response

    async def set_webhook(
            self,
            webhook_url: str
    ) -> Optional[Dict[str, Any]]:
        response = await self._make_request("POST", "setWebhook", data={"webhookURL": webhook_url})
        if response:
            self._log(f"[AsyncYoPhonePy] ✅ Webhook URL set to: {webhook_url}")
        return response

    async def get_webhook_info(self) -> Optional[Dict[str, Any]]:
        return await self._make_request("POST", "getWebhookInfo")

    async def remove_webhook(self) -> Optional[Dict[str, Any]]:
        response = await self._make_request("POST", "deleteWebhook")
        if response:
            self._log(f"[AsyncYoPhonePy] ✅ Webhook deleted successfully.")
        return response

    async def get_bot_info(self) -> Optional[Dict[str, Any]]:
        return await self._make_request("POST", "getMe")

    async def get_channel_user_status(
            self,
            channel_id: str,
            user_id: str
    ) -> Optional[Dict[str, Any]]:
        return await self._make_request("POST", "getChannelMember", data={"channelId": channel_id, "userId": user_id})
