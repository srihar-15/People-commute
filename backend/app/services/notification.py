import time
from typing import Dict, Any

class NotificationService:
    def send_whatsapp_template(self, phone: str, template_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Simulates sending a WhatsApp Template message via the native MCP tool integration / WABA API.
        """
        print(f"[WHATSAPP NOTIFICATION] In progress...")
        print(f"  Recipient Phone: {phone}")
        print(f"  Template Name: {template_name}")
        print(f"  Parameters: {parameters}")
        
        # In a real setup, this triggers the WhatsApp API or calls the WhatsApp MCP server tool.
        # For our MVP/Hackathon, we log this and make it queryable in the DB / log stream.
        time.sleep(0.5)
        print(f"[WHATSAPP NOTIFICATION] Sent successfully to {phone}!")
        return True

    def send_sms(self, phone: str, message: str) -> bool:
        """
        Sends standard SMS notifications.
        """
        print(f"[SMS NOTIFICATION] Sent to {phone}: '{message}'")
        return True

    def send_email(self, email: str, subject: str, body: str) -> bool:
        """
        Sends system emails (primarily for Officer alerts and reports).
        """
        print(f"[EMAIL NOTIFICATION] Sent to {email}:")
        print(f"  Subject: {subject}")
        print(f"  Body: {body[:100]}...")
        return True

notification_service = NotificationService()
