import os
import shutil
from telethon import TelegramClient, events, Button
from config import api_id, api_hash, bot_token, admin_ids
from database import session, Payment, QRCode
import asyncio
import json
from datetime import datetime, timedelta

if not os.path.exists("receipts"):
    os.mkdir("receipts")
if not os.path.exists("qrcodes"):
    os.mkdir("qrcodes")

bot = TelegramClient("bot_session", api_id, api_hash).start(bot_token=bot_token)
user_states = {}


admin_states = {}

user_link_state = {}



def load_settings():
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(data):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

with open("settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

android_link = settings.get("android_link")
ios_link = settings.get("ios_link")


barcode_upload_count = 0 


card_buttons = [
    Button.inline("💳 کارت 1", b"copy_card1"),
    Button.inline("💳 کارت 2", b"copy_card2"),
]


main_inline_buttons = [
    [Button.inline("💳 خرید اشتراک", b"buy")],
    [Button.inline("📲 دانلود اپ", b"download_app")],
]


support_button = [Button.text("🛠 پشتیبان", resize=True)]


@bot.on(events.CallbackQuery(data=b"download_app"))
async def download_app(event):
    settings = load_settings()
    android_link = settings.get("android_link", "https://default_android_link")
    ios_link = settings.get("ios_link", "https://default_ios_link")

    download_buttons = [ 
        [
            Button.url("🤖 نسخه اندروید", android_link),
            Button.url("🍏 نسخه آیفون / آیپد", ios_link),
        ],
        [
            Button.inline("🔙 بازگشت", b"back_to_main"),
        ],
    ]

    await event.respond(
        "لطفا نسخه دانلود خودتان را انتخاب کنید:",
        buttons=download_buttons
    )
    await event.answer()


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id


    buttons = list(main_inline_buttons)


    if user_id in admin_ids:
        buttons.append([Button.inline("🛠 پنل مدیریت", b"open_admin_panel")])

    await event.respond(
        "سلام خوش آمدید🌟\n\nلطفا یکی از آیتم‌های زیر را انتخاب کنید 👇",
        buttons=buttons
    )

    await event.respond(
        "اگر نیاز به پشتیبان داری روی دکمه پایین بزن:",
        buttons=support_button
    )


@bot.on(events.CallbackQuery(data=b"buy"))
async def buy(event):
    user_states[event.sender_id] = "awaiting_info"
    await event.respond(
        "لطفاً فامیلی + ۴ رقم آخر موبایل را وارد کن (مثال: barari 8264)",
        buttons=[[Button.inline("🔙 بازگشت", b"back_to_main")]]
    )

    await event.answer()



@bot.on(events.CallbackQuery(data=b"back_to_main"))
async def back_to_main_callback(event):
    user_id = event.sender_id

    if user_support_state.get(user_id):
        del user_support_state[user_id]


    if support_reply_state.get(user_id):
        del support_reply_state[user_id]

    await event.edit(
        "به منوی اصلی برگشتید، لطفا یکی از آیتم های زیر را انتخاب کنید 👇",
        buttons=main_inline_buttons
    )
    await event.answer()

################################################################################ظ######
######################################################################################
######################################################################################


user_support_state = {}    
support_reply_state = {}       

@bot.on(events.NewMessage(pattern="🛠 پشتیبان"))
async def support_button_pressed(event):
    user_id = event.sender_id
    user_support_state[user_id] = True 

    await event.respond(
        "🧑‍💻 شما در حال ارسال پیام به پشتیبان هستید.\n"
        "لطفاً پیام متنی یا تصویری خود را وارد کنید.\n\n"
        "⚠️ فقط پیام‌های متنی و تصویری مجاز هستند.",
        buttons=[[Button.inline("🔙 بازگشت", b"back_to_main")]]
    )


@bot.on(events.NewMessage())
async def support_message_handler(event):
    user_id = event.sender_id

    if support_reply_state.get(user_id):
        target_user = support_reply_state.pop(user_id)
        try:
            if event.photo or event.document:
                caption = event.text or ""
                full_caption = f"📬 پاسخ پشتیبان:\n\n{caption}" if caption else "📬 پاسخ پشتیبان 🛠️"
                await bot.send_file(
                    target_user,
                    file=event.media,
                    caption=full_caption
                )
            elif event.text:
                await bot.send_message(
                    target_user,
                    f"📬 پاسخ پشتیبان:\n\n{event.text}"
                )
            await event.respond("✅ پاسخ شما برای کاربر ارسال شد.")
        except Exception as e:
            await event.respond("❌ خطا در ارسال پاسخ به کاربر.")
            print(f"❌ خطا در ارسال پیام به کاربر: {e}")
        return


    if user_support_state.get(user_id):

        if event.raw_text.strip() == "🛠 پشتیبان":
            return

        del user_support_state[user_id]

        await event.respond("✅ پیام شما برای پشتیبان ارسال شد.")

  
        for admin_id in admin_ids:
            if event.photo or event.document:
                caption = event.text or "بدون کپشن"
                await bot.send_file(
                    admin_id,
                    file=event.media,
                    caption=(
                        f"📩 پیام تصویری از کاربر:\n"
                        f"🆔 یوزرنیم: @{event.sender.username or 'ندارد'}\n"
                        f"🧾 آیدی عددی: {user_id}\n\n"
                        f"💬 کپشن:\n{caption}"
                    ),
                    buttons=[Button.inline("✉️ پاسخ به کاربر", data=f"reply_{user_id}")]
                )
            elif event.text:
                await bot.send_message(
                    admin_id,
                    f"📩 پیام متنی از کاربر:\n"
                    f"🆔 یوزرنیم: @{event.sender.username or 'ندارد'}\n"
                    f"🧾 آیدی عددی: {user_id}\n\n"
                    f"💬 پیام:\n{event.text}",
                    buttons=[Button.inline("✉️ پاسخ به کاربر", data=f"reply_{user_id}")]
                )
        else:
            await event.respond("❌ فقط پیام‌های متنی و تصویری پشتیبانی می‌شوند.")

@bot.on(events.CallbackQuery(pattern=b"reply_\d+"))
async def handle_support_reply_button(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔️ شما اجازه این عملیات را ندارید.", alert=True)
        return

    user_id = int(event.data.decode().split("_")[1])
    support_reply_state[event.sender_id] = user_id

    await event.respond("✍️ لطفاً پیام پاسخ را وارد کنید (متن یا عکس با کپشن):")



######################################################################################
######################################################################################
######################################################################################


@bot.on(events.NewMessage())
async def handle_input(event):
    user_id = event.sender_id

    if user_states.get(user_id) == "awaiting_info":
        user_states[user_id] = "awaiting_receipt"
        user_states[f"{user_id}_info"] = event.raw_text.strip()

        settings = load_settings()

        await event.respond(
            f"💳 مبلغ {settings['price']} ریال را به یکی از این شماره کارت‌ها واریز کن:\n\n"
            f"{settings['card1']}\n"
            f"{settings['card2']}\n"
            "(به نام میلاد مغربی)\n\n"
            "سپس رسید پرداخت را به صورت **عکس** ارسال کن 📸",
            parse_mode='markdown',
            buttons=[
                card_buttons,
                [Button.inline("🔙 بازگشت", b"back_to_main")]
            ]
        )


    elif user_states.get(user_id) == "awaiting_receipt" and event.photo:
        filename = f"receipts/{user_id}_{event.id}.jpg"
        await event.download_media(file=filename)
        info = user_states.get(f"{user_id}_info", "نامشخص")

        payment = Payment(
            user_id=user_id,
            username=event.sender.username or "Unknown",
            family_info=info,
            receipt_path=filename,
        )
        session.add(payment)
        session.commit()

        del user_states[user_id]

        await event.respond("✅ رسید ثبت شد و در حال بررسی است.")

        for admin_id in admin_ids:
            await bot.send_file(
                admin_id,
                file=filename,
                caption=f"🔔 رسید جدید از @{event.sender.username or 'کاربر'}\n{info}",
                buttons=[
                    Button.inline("✅ تأیید", f"confirm_{payment.id}"),
                    Button.inline("❌ رد", f"reject_{payment.id}")
                ]
            )

@bot.on(events.CallbackQuery(data=b"copy_card1"))
async def copy_card1(event):
    settings = load_settings()
    await bot.send_message(event.sender_id, f"📇 شماره کارت:\n{settings['card1']}")

    await event.answer()

@bot.on(events.CallbackQuery(data=b"copy_card2"))
async def copy_card2(event):
    settings = load_settings()
    await bot.send_message(event.sender_id, f"📇 شماره کارت:\n{settings['card2']}")

    await event.answer()

@bot.on(events.CallbackQuery(pattern=b"reject_"))
async def reject(event):
    if event.sender_id not in admin_ids:
        return

    payment_id = int(event.data.decode().split("_")[1])
    payment = session.get(Payment, payment_id)
    if not payment:
        await event.respond("❌ پرداخت یافت نشد.")
        return


    if payment.status == "accepted":
        await event.respond(f"⚠️ این رسید قبلاً توسط ادمین {payment.handled_by} تایید شده و قابل رد نیست.")
        return
    elif payment.status == "rejected":
        await event.respond(f"⚠️ این رسید قبلاً توسط ادمین {payment.handled_by} رد شده و نیازی به رد مجدد نیست.")
        return


    payment.status = "rejected"
    payment.handled_by = event.sender_id
    session.commit()

    await event.respond("❌ رسید رد شد.")

    try:
        await bot.send_message(
            payment.user_id,
            "❌ رسید شما توسط ادمین تایید نشد.\nلطفاً دوباره یک عکس واضح از رسید ارسال کنید.",
            buttons=[[Button.inline("🔙 بازگشت", b"back_to_main")]]
        )
    except Exception as e:
        print(f"خطا در ارسال پیام رد به کاربر: {e}")


@bot.on(events.CallbackQuery(pattern=b"confirm_"))
async def confirm(event):
    if event.sender_id not in admin_ids:
        return

    payment_id = int(event.data.decode().split("_")[1])
    payment = session.get(Payment, payment_id)

    if not payment:
        await event.respond("❌ پرداخت یافت نشد.")
        return


    if payment.status == "accepted":
        await event.respond(f"⚠️ این رسید قبلاً توسط ادمین {payment.handled_by} تایید شده و نیازی به تایید مجدد نیست.")
        return


    if payment.status == "rejected":
        await event.respond(f"🚫 این رسید قبلاً توسط ادمین {payment.handled_by} رد شده و قابل تایید نیست.")
        return


    payment.status = "accepted"
    payment.handled_by = event.sender_id
    session.commit()


    qrcode = session.query(QRCode).filter_by(is_used=False).order_by(QRCode.id).first()
    if not qrcode:
        await bot.send_message(
            payment.user_id,
            "❌ بارکدها تمام شدند. لطفاً بعداً دوباره تلاش کنید.",
            buttons=[[Button.inline("🔙 بازگشت", b"back_to_main")]]
        )

        for admin_id in admin_ids:
            await bot.send_message(admin_id, "🚨 بارکدها تمام شدند! لطفاً 20 بارکد جدید آپلود کنید.")
        return

    qrcode.is_used = True
    session.commit()

    await bot.send_file(
        payment.user_id,
        f"qrcodes/{qrcode.filename}",
        caption=(
            "🔒 اشتراک شما فعال شد.\n\n"
            "برای وارد کردن بارکد لطفاً مراحل زیر رو انجام بده:\n"
            "1. با گوشی دیگه از این بارکد عکس بگیر📸\n"
            "2. برنامه Wireguard رو باز کن\n"
            "3. بالا سمت راست روی + بزن ➕\n"
            "4. گزینه 'Scan from QR code' رو انتخاب کن ✅\n"
            "5. عکس رو انتخاب و اسکن کن\n"
            "6. هر اسمی خواستی بزن 📝\n"
            "7. تیک کنار اسم رو روشن کن 🔛\n\n"
        )
    )
    await event.respond("✅ پرداخت تایید و بارکد ارسال شد.")


    remaining = session.query(QRCode).filter_by(is_used=False).count()
    if remaining == 5:
        for admin_id in admin_ids:
            await bot.send_message(admin_id, "⚠️ فقط ۵ بارکد باقی مانده! لطفاً بارکد های جدید را آماده کنید.")

@bot.on(events.Album())
async def upload_album(event):
    global barcode_upload_count
    if event.sender_id not in admin_ids:
        return

    messages = event.messages
    count = len(messages)

    if count > 10:
        await event.respond(f"❌ حداکثر ۱۰ عکس در هر نوبت مجاز است (شما {count} ارسال کردید).")
        return

    start_index = barcode_upload_count + 1
    end_index = barcode_upload_count + count

    if end_index > 20:
        await event.respond("❌ بیشتر از ۲۰ بارکد نمی‌توانید آپلود کنید.")
        return

    if barcode_upload_count == 0:
        shutil.rmtree("qrcodes", ignore_errors=True)
        os.makedirs("qrcodes", exist_ok=True)
        session.query(QRCode).delete()
        session.commit()

    for i, msg in enumerate(messages, start=start_index):
        path = f"qrcodes/{i}.png"
        await msg.download_media(file=path)
        session.add(QRCode(id=i, filename=f"{i}.png", is_used=False))

    session.commit()
    barcode_upload_count = end_index

    if barcode_upload_count == 20:
        await event.respond("✅ ۲۰ بارکد با موفقیت آپلود شد.")

    else:
        remaining = 20 - barcode_upload_count
        await event.respond(f"✅ {count} بارکد ذخیره شد. باقی مانده: {remaining} عدد.")


######################################################################################
######################################################################################
######################################################################################


@bot.on(events.NewMessage(pattern="/admin"))
async def admin_panel(event):
    if event.sender_id not in admin_ids:
        await event.respond("⛔ شما ادمین نیستید.")
        return

    await event.respond(
        "🔧 به پنل مدیریت خوش آمدید",
        buttons=[
            [Button.inline("💲 تغییر قیمت", b"change_price")],
            [Button.inline("💳 تغییر شماره کارت‌ها", b"change_cards")],
            [Button.inline("📲 تغییر لینک دانلود اپ", b"change_download_links")] 
        ]
    )

@bot.on(events.CallbackQuery(data=b"open_admin_panel"))
async def open_admin_panel(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔ شما ادمین نیستید.", alert=True)
        return

    await event.respond(
        "🔧 به پنل مدیریت خوش آمدید",
        buttons=[
            [Button.inline("💲 تغییر قیمت", b"change_price")],
            [Button.inline("💳 تغییر شماره کارت‌ها", b"change_cards")],
            [Button.inline("🔗 تغییر لینک دانلود اپ", b"change_download_links")], 
        ]
    )

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode("utf-8")

    if data == "change_android_link":
        user_link_state[event.sender_id] = "android_link"
        await event.respond("لینک جدید نسخه اندروید را ارسال کنید:")
    elif data == "change_ios_link":
        user_link_state[event.sender_id] = "ios_link"
        await event.respond("لینک جدید نسخه iOS را ارسال کنید:")


@bot.on(events.CallbackQuery(data=b"change_price"))
async def change_price(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔ شما ادمین نیستید.", alert=True)
        return

    admin_states[event.sender_id] = "waiting_for_price"
    await event.respond("🔢 لطفاً قیمت جدید را به ریال و با کاما و با فونت فارسی ارسال کنید:")

@bot.on(events.CallbackQuery(data=b"change_cards"))
async def change_cards(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔ شما ادمین نیستید.", alert=True)
        return

    settings = load_settings()
    await event.respond(
        "کدام شماره کارت را می‌خواهید تغییر دهید؟",
        buttons=[
            [Button.inline(f"کارت 1: {settings['card1']}", b"edit_card1")],
            [Button.inline(f"کارت 2: {settings['card2']}", b"edit_card2")]
        ]
    )

@bot.on(events.CallbackQuery(pattern=b"edit_card\d"))
async def edit_card(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔ شما ادمین نیستید.", alert=True)
        return

    if event.data == b"edit_card1":
        admin_states[event.sender_id] = "waiting_for_card_1"
    elif event.data == b"edit_card2":
        admin_states[event.sender_id] = "waiting_for_card_2"

    await event.respond("🔢 لطفاً شماره کارت جدید را وارد کنید:")

@bot.on(events.CallbackQuery(data=b"change_download_links"))
async def choose_platform(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔ شما ادمین نیستید.", alert=True)
        return
    await event.respond(
        "لطفاً پلتفرم مورد نظر را انتخاب کنید:",
        buttons=[
            [Button.inline("🍏 آیفون / آیپد", b"change_link_ios")],
            [Button.inline("🤖 اندروید", b"change_link_android")],
        ]
    )


@bot.on(events.CallbackQuery(data=b"change_link_ios"))
async def change_ios_link(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔ شما ادمین نیستید.", alert=True)
        return
    admin_states[event.sender_id] = "ios_link"
    await event.respond("لطفا لینک جدید برای نسخه آیفون / آیپد را ارسال کنید:")


@bot.on(events.CallbackQuery(data=b"change_link_android"))
async def change_android_link(event):
    if event.sender_id not in admin_ids:
        await event.answer("⛔ شما ادمین نیستید.", alert=True)
        return
    admin_states[event.sender_id] = "android_link"
    await event.respond("لطفا لینک جدید برای نسخه اندروید را ارسال کنید:")

@bot.on(events.NewMessage())
async def handle_link_message(event):
    user_id = event.sender_id
    state = admin_states.get(user_id)

    if state == "waiting_for_android_link":
        settings = load_settings()
        settings["android_link"] = event.raw_text.strip()
        save_settings(settings)
        admin_states.pop(user_id, None)
        await event.reply("✅ لینک اندروید با موفقیت ذخیره شد.")

    elif state == "waiting_for_ios_link":
        settings = load_settings()
        settings["ios_link"] = event.raw_text.strip()
        save_settings(settings)
        admin_states.pop(user_id, None)
        await event.reply("✅ لینک iOS با موفقیت ذخیره شد.")


@bot.on(events.NewMessage())
async def admin_input_handler(event):
    user_id = event.sender_id
    if user_id not in admin_ids:
        return  

    if user_id in admin_states:
        state = admin_states.pop(user_id)  

        settings = load_settings()

        if state == "waiting_for_price":
            settings["price"] = event.raw_text.strip()
            save_settings(settings)
            await event.respond(f"✅ قیمت با موفقیت به {settings['price']} تغییر یافت.")

        elif state == "waiting_for_card_1":
            settings["card1"] = event.raw_text.strip()
            save_settings(settings)
            await event.respond(f"✅ شماره کارت 1 با موفقیت به {settings['card1']} تغییر یافت.")

        elif state == "waiting_for_card_2":
            settings["card2"] = event.raw_text.strip()
            save_settings(settings)
            await event.respond(f"✅ شماره کارت 2 با موفقیت به {settings['card2']} تغییر یافت.")

        elif state == "android_link" or state == "ios_link":
            settings[state] = event.raw_text.strip()
            save_settings(settings)
            await event.respond(f"✅ لینک {state.replace('_link','')} با موفقیت ذخیره شد.")

######################################################################################
######################################################################################
######################################################################################

async def check_expiring_subscriptions():
    now = datetime.utcnow()
    threshold = timedelta(days=28)

    expiring_users = session.query(Payment).filter(
        Payment.is_confirmed == False,
        Payment.created_at <= now - threshold,
        Payment.reminder_sent == False
    ).all()

    print(f"[LOG] Found {len(expiring_users)} payments to remind with is_confirmed=False")

    for payment in expiring_users:
        try:
            await bot.send_message(
                payment.user_id,
                "سلام 👋\n"
                "اشتراک شما تا ۲ روز دیگه به پایان می‌رسه.\n\n"
                "برای جلوگیری از قطع سرویس، همین حالا می‌تونی تمدیدش کنی✅\n\n"
                "📌 جهت تمدید اشتراک روی دکمه زیر کلیک کن👇",
                buttons=main_inline_buttons
            )
            payment.reminder_sent = True
            session.commit()
        except Exception as e:
            print(f"❌ خطا در ارسال پیام به {payment.user_id}: {e}")



async def schedule_daily_check():
    while True:
        await check_expiring_subscriptions()
        await asyncio.sleep(86400)  

loop = asyncio.get_event_loop()
loop.create_task(schedule_daily_check())





print("🤖 Bot is running...")
bot.run_until_disconnected()