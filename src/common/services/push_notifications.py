import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

EXPO_PUSH_API_URL = "https://exp.host/--/api/v2/push/send"

def send_expo_push_notifications(push_tokens: List[str], message: str, data: Optional[Dict[str, Any]] = None, title: Optional[str] = None):
    """
    Sends push notifications via Expo's Push API.
    
    Args:
        push_tokens: List of Expo push tokens.
        message: The body of the notification.
        data: Optional data payload.
        title: Optional title of the notification.
    """
    if not push_tokens:
        return

    # Expo suggests sending messages in chunks of up to 100
    chunk_size = 100
    for i in range(0, len(push_tokens), chunk_size):
        chunk = push_tokens[i : i + chunk_size]
        payload = []
        for token in chunk:
            if not token.startswith("ExponentPushToken"):
                logger.warning(f"Invalid Expo push token: {token}")
                continue
                
            notification = {
                "to": token,
                "body": message,
                "sound": "default",
            }
            if title:
                notification["title"] = title
            if data:
                notification["data"] = data
            payload.append(notification)

        if not payload:
            continue

        try:
            response = requests.post(
                EXPO_PUSH_API_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Accept-encoding": "gzip, deflate",
                },
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                # Handle individual errors in the response
                # Expo returns a list of receipts in the same order as the payload
                data_result = result.get("data", [])
                for idx, receipt in enumerate(data_result):
                    if receipt.get("status") == "error":
                        error_msg = receipt.get("message")
                        details = receipt.get("details", {})
                        error_code = details.get("error")
                        logger.error(f"Error sending to token {payload[idx]['to']}: {error_msg} (code: {error_code})")
                        # If the error is 'DeviceNotRegistered', the token is no longer valid
                        if error_code == "DeviceNotRegistered":
                            logger.info(f"Token {payload[idx]['to']} is no longer registered.")
            else:
                logger.error(f"Failed to send push notifications: {response.status_code} - {response.text}")
        except Exception as e:
            logger.exception(f"Exception while sending push notifications: {e}")
