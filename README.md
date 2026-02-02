# Telegram Gmail Watcher 🤖📩

A real-time AI agent that monitors your Gmail inbox, summarizes incoming emails using Google Gemini, and sends instant alerts to your Telegram.

## ✨ Features
* **Real-Time Monitoring:** Checks for new unread emails every 60 seconds.
* **AI Summarization:** Uses Google's **Gemini 2.5 Flash** model to condense long emails into 1-2 sentence summaries.
* **Instant Alerts:** Pushes a notification to your Telegram with the sender, subject, and summary.
* **Smart Filtering:** Tracks email IDs to prevent duplicate notifications.
* **Network Robustness:** Includes a patch to force IPv4 connections, solving timeouts on unstable IPv6 networks.

## 🛠️ Prerequisites
* Python 3.10+
* A Google Cloud Project with the **Gmail API** enabled.
* A Telegram Account.

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/NedaaaNik/telegram-gmail-bot.git]
    cd telegram-gmail-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🔑 Configuration

This agent requires three secrets to work. You must create a file named `.env` in the project folder and add them there.

### 1. Create the `.env` file
Create a file named `.env`and paste the following:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
