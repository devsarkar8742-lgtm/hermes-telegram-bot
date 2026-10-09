import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am your Gemini AI bot. Send me a message!"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    if not GEMINI_API_KEY:
        await update.message.reply_text("Gemini API key is not configured.")
        return

    try:
        response = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": message}
                        ]
                    }
                ]
            },
            timeout=40,
        )

        response.raise_for_status()
        data = response.json()

        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        await update.message.reply_text(answer[:4000])

    except Exception:
        logging.exception("Gemini request failed")
        await update.message.reply_text(
            "Sorry, an error occurred. Please try again."
        )


def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise RuntimeError("Required environment
