import io
import os
import time
import requests
import logging

from typing import Callable, Dict, Any, List, Optional
from utils import determine_mime_type, parse_update
from models import Message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class YoPhoneBot:
    """
    A Python wrapper for the YoPhone Bot API.
    """

    def __init__(
            self,
            api_key: str,
            base_url: str = "https://yoai.yophone.com/api/pub"
    ):
        """
        Initialize the YoPhone bot with the given API key and optional base URL.

        Args:
            api_key (str): The API key for your YoPhone bot.
            base_url (str, optional): The base URL of the YoPhone API.
                Defaults to "https://yoai.yophone.com/api/pub".
        """
        self.api_key = api_key
        self.base_url = base_url
        self.message_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self.command_handlers: Dict[str, Callable[[Message], None]] = {}
        self._session = requests.Session()
        self._session.headers.update({"X-YoAI-API-Key": self.api_key})

    def _make_request(
            self,
            method: str,
            endpoint: str,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[List[tuple]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Internal method to make HTTP requests to the YoPhone API.

        Args:
            method (str): The HTTP method (e.g., "POST", "GET").
            endpoint (str): The API endpoint to call.
            data (Optional[Dict[str, Any]], optional): The JSON payload for the request. Defaults to None.
            files (Optional[List[tuple]], optional): A list of tuples for file uploads. Defaults to None.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self._session.request(method, url, json=data, files=files)
            response.raise_for_status()
            if response.status_code == 200 and response.text.strip():
                return response.json()
            elif response.status_code == 204:
                return None
            else:
                logging.warning(
                    f"Empty or unexpected response for {method} {url}: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to make request to {url}: {e}")
            return None

    def message_handler(
            self,
            func: Callable[[Dict[str, Any]], None]
    ):
        """
        Register a function to handle general messages.

        Args:
            func (Callable[[Dict[str, Any]], None]): The function to call when a general message is received.
                This function should accept the raw update dictionary as an argument.

        Returns:
            Callable[[Dict[str, Any]], None]: The decorated function.
        """
        self.message_handlers.append(func)
        logging.info(f"Registered message handler: {func.__name__}")
        return func

    def command_handler(
            self,
            command: str
    ):
        """
        Register a function to handle specific commands.

        Args:
            command (str): The command to handle (e.g., "start"). Note that the leading '/' should not be included.

        Returns:
            Callable[[Message], None] -> Callable[[Message], None]: A decorator that registers the function.
                The decorated function should accept a `Message` object as an argument.
        """

        def decorator(func: Callable[[Message], None]):
            self.command_handlers[f"/{command}"] = func
            logging.info(f"Registered command handler for '/{command}': {func.__name__}")
            return func

        return decorator

    def get_updates(self) -> List[Dict[str, Any]]:
        """
        Fetch updates from the YoPhone API.

        Returns:
            List[Dict[str, Any]]: A list of update dictionaries.
        """
        response = self._make_request("POST", "getUpdates")
        if response and "data" in response:
            return response["data"]
        return []

    def process_updates(self):
        """
        Fetch and process incoming updates.
        """
        updates = self.get_updates()
        for update in updates:
            try:
                parsed_update = parse_update(update)
                message = Message.from_dict(parsed_update)

                # Check for commands
                if message.text and message.text.startswith("/"):
                    command = message.text.split()[0]
                    if command in self.command_handlers:
                        self.command_handlers[command](message)
                        continue

                # Process as a regular message
                for handler in self.message_handlers:
                    handler(parsed_update)
            except Exception as e:
                logging.error(f"Error processing update: {update}. Error: {e}", exc_info=True)

    def start_polling(
            self,
            interval: int = 2
    ):
        """
        Start an infinite polling loop to fetch and process updates.

        Args:
            interval (int, optional): The polling interval in seconds. Defaults to 2.
        """
        logging.info("Bot started polling... Press Ctrl+C to stop.")
        try:
            while True:
                self.process_updates()
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Polling stopped by user.")
        except Exception as e:
            logging.error(f"An error occurred during polling: {e}", exc_info=True)
            time.sleep(5)  # Wait before retrying in case of errors

    def send_message(
            self,
            chat_id: str,
            text: str
    ) -> Optional[Dict[str, Any]]:
        """
        Send a text message to a specific chat.

        Args:
            chat_id (str): The ID of the chat to send the message to.
            text (str): The text of the message to send.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        payload = {
            "to": chat_id,
            "text": text
        }
        return self._make_request("POST", "sendMessage", data=payload)

    def send_message_with_options(
            self,
            chat_id: str,
            text: str,
            options: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message with options (label-value pairs) to a specific chat.

        Args:
            chat_id (str): The ID of the chat to send the message to.
            text (str): The text of the message.
            options (List[Dict[str, str]]): A list of dictionaries, where each dictionary
                represents an option with "label" and "value" keys.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        payload = {
            "to": chat_id,
            "text": text,
            "options": options
        }
        return self._make_request("POST", "sendMessage", data=payload)

    def send_message_with_buttons(
            self,
            chat_id: str,
            text: str,
            grid: int = 1,
            options: Optional[List[Dict[str, str]]] = None,
            inline_buttons: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message with buttons to a specific chat.

        Args:
            chat_id (str): The ID of the chat to send the message to.
            text (str): The text of the message.
            grid (int, optional): The number of buttons per row. Defaults to 1.
            options (Optional[List[Dict[str, str]]], optional): A list of dictionaries
                for reply buttons, each with "label" and "value" keys. Defaults to None.
            inline_buttons (Optional[List[Dict[str, str]]], optional): A list of dictionaries
                for inline buttons, each with "label" and "url" or "callback_data" keys.
                Defaults to None.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        payload = {
            "to": chat_id,
            "text": text,
            "buttons": {
                "grid": grid,
                "options": options if options else [],
                "inline_buttons": inline_buttons if inline_buttons else []
            }
        }
        return self._make_request("POST", "sendMessage", data=payload)

    def send_message_with_file(
            self,
            chat_id: str,
            file_paths: List[str],
            caption: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send one or more files (photos, videos, documents) to a specific chat.

        Args:
            chat_id (str): The ID of the chat to send the file(s) to.
            file_paths (List[str]): A list of file paths to the files to send.
            caption (Optional[str], optional): An optional caption for the file(s). Defaults to None.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        payload = {"to": chat_id, "text": caption if caption else ""}
        files_data = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logging.error(f"File not found at {file_path}")
                return None
            if os.path.getsize(file_path) > 50 * 1024 * 1024:  # 50MB limit
                logging.error(f"File {file_path} exceeds 50MB limit.")
                return None

            try:
                with open(file_path, "rb") as f:
                    buffer = f.read()
                mime_type = determine_mime_type(file_path)
                files_data.append(("file", (os.path.basename(file_path), io.BytesIO(buffer), mime_type)))
            except Exception as e:
                logging.error(f"Error reading file {file_path}: {e}")
                return None

        return self._make_request("POST", "sendMessage", data=payload, files=files_data)

    def set_commands(
            self,
            commands: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Set a list of commands with their descriptions.

        Args:
            commands (List[Dict[str, str]]): A list of dictionaries, where each dictionary
                represents a command with "command" (without the leading '/') and "description" keys.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        payload = {"commands": commands}
        response = self._make_request("POST", "setCommands", data=payload)
        if response:
            logging.info(f"Successfully set commands: {response}")
        return response

    def set_webhook(
            self,
            webhook_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Configure the YoAI bot to receive updates via a webhook.
        The bot will send messages to the specified webhook URL.

        Args:
            webhook_url (str): The URL where the YoPhone API should send updates.
                Ensure this URL is publicly accessible and can handle POST requests.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        payload = {"webhookURL": webhook_url}
        response = self._make_request("POST", "setWebhook", data=payload)
        if response:
            logging.info(f"Successfully set webhook to: {webhook_url}")
        return response

    def get_webhook(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve information about the configured webhook URL.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API containing webhook information,
                or None if an error occurred.
        """
        return self._make_request("POST", "getWebhookInfo")

    def delete_webhook(self) -> Optional[Dict[str, Any]]:
        """
        Delete the configured webhook URL.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurred.
        """
        response = self._make_request("POST", "deleteWebhook")
        if response:
            logging.info("Successfully deleted webhook.")
        return response

    def get_me(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve information about the bot.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API containing bot information,
                or None if an error occurred.
        """
        return self._make_request("POST", "getMe")

    def get_channel_member(
            self,
            channel_id: str,
            user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve information about a user's membership status in a specific channel.

        Args:
            channel_id (str): The ID of the channel.
            user_id (str): The ID of the user.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API containing the channel member information,
                or None if an error occurred.
        """
        payload = {
            "channelId": channel_id,
            "userId": user_id
        }
        return self._make_request("POST", "getChannelMember", data=payload)
