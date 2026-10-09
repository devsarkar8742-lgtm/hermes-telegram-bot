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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "Hello! I am your Gemini AI bot.\n"
        "Send me a message to start chatting!"
    )


async def chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    message = update.message.text

    if not GEMINI_API_KEY:
        await update.message.reply_text(
            "Gemini API key is not configured."
        )
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

        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i + 4000])

    except requests.exceptions.HTTPError:
        logging.exception("Gemini API returned an HTTP error")
        await update.message.reply_text(
            "Gemini API request failed. Please check the API configuration."
        )

    except (KeyError, IndexError, TypeError):
        logging.exception("Unexpected Gemini API response")
        await update.message.reply_text(
            "Gemini returned an unexpected response. Please try again."
        )

    except requests.exceptions.RequestException:
        logging.exception("Gemini connection failed")
        await update.message.reply_text(
            "Could not connect to Gemini. Please try again."
        )

    except Exception:
        logging.exception("Unexpected bot error")
        await update.message.reply_text(
            "An unexpected error occurred. Please try again."
        )


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing from environment variables."
        )

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from environment variables."
        )

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    logging.info("Starting Telegram bot...")

    app.run_polling()


if __name__ == "__main__":
    main()
