# Telegram Subscription Bot 📲

A Telegram bot for managing **subscription purchases**, **receipt uploads**, and **admin confirmation**.

## 📦 Features

- 🔐 Admin-only approval system for payments
- 🧾 Upload receipt images (saved in `/receipts`)
- ✅ Only confirmed payments trigger services
- ⏱️ Automatically sets expiration for services
- 📁 QR code generation support (stored in `/qrcodes`)
- 💬 Clean and interactive UI with buttons
- 🗃️ SQLAlchemy-powered database

## 📁 Project Structure

```
├── bot.py              # Main bot logic
├── config.py           # Configuration variables
├── database.py         # SQLAlchemy models & DB session
├── receipts/           # Folder to store uploaded receipts
├── qrcodes/            # Folder to store generated QR codes
└── README.md           # You're here!
```

## ⚙️ Requirements

- Python 3.10+
- PostgreSQL or SQLite (via SQLAlchemy)
- Telethon
- python-telegram-bot
- asyncio
- Pillow (if using image processing)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/matinebadi/VPN_store_bot.git
cd VPN_store_bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your settings

Edit the `config.py` file with your:

- `api_id` and `api_hash` from https://my.telegram.org
- `bot_token` from BotFather
- `admin_ids` list (user IDs of admins)
- database connection (if needed)

### 4. Run the bot

```bash
python bot.py
```

## 🛠 Example Usage

- User sends payment screenshot.
- Admin receives it with approve/reject buttons.
- On approval, bot marks `Payment.is_confirmed = True`.
- If not confirmed, nothing happens.

## 🙋 About the Developer

Made with ❤️ by [@matinebadi](https://github.com/matinebadi)  
If you like the project, give it a ⭐️ on GitHub!
