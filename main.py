# Костыль для обхода ошибки imghdr
import sys
import mimetypes
sys.modules['imghdr'] = mimetypes

import logging
import sqlite3
import json
import io
from PIL import Image, ImageDraw, ImageFont
import telegram
import os
from telegram import Update, InputFile, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройки логгирования
logging.basicConfig(
    format="▮■▮ TOKYO CORE [%(asctime)s] ■▮▮\n%(levelname)s: %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конф
TOKEN = ""
ADMIN_ID = 12345678
CONFIG_ID = 123
DB_NAME = "TokyoCore.db"

# Инициализация базы данных ГЛОБАЛЬНО
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users 
       (chatid INTEGER PRIMARY KEY, name TEXT, volts INTEGER, rank TEXT)"""
)
conn.commit()
RANKS = {
    # Ученики и новички
    "owner": "Создатель",
    
    # Базовые ранги
    "user": "Ученик",
    "friend": "Друзья",
    "tester": "Тестер",

    # Административные
    "admin": "Администратор",
    "legend": "Легенда"
    
}


# Вспомогательные функции
from telegram.error import BadRequest

def backup_data(context: CallbackContext):
    global CONFIG_ID, conn, cursor
    try:
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        json_data = json.dumps(data).encode()
        
        # Удаляем предыдущее сообщение только если CONFIG_ID существует
        try:
            context.bot.delete_message(ADMIN_ID, CONFIG_ID)
        except BadRequest:
            logger.warning("Сообщение для удаления не найдено. Пропуск.")
        
        file = InputFile(io.BytesIO(json_data), filename="backup.json")
        msg = context.bot.send_document(ADMIN_ID, document=file)
        CONFIG_ID = msg.message_id
    except Exception as e:
        logger.error(f"Ошибка резервного копирования: {e}")
        
        
def generate_volts_image(user_name: str, volts: int, rank: str) -> io.BytesIO:
    try:
        # Загрузка фонового изображения
        img = Image.open("core_bg.png").convert("RGBA")
        img = img.resize((1280, 720))
    except Exception as e:
        # Fallback на черный фон
        img = Image.new('RGBA', (1280, 720), (0, 0, 0, 255))
        logger.error(f"Ошибка загрузки фона: {e}")

    draw = ImageDraw.Draw(img)
    
    # Стили текста
    text_style = {
        "title": {"size": 72, "color": (0, 255, 255), "position": (180, 120)},
        "volts": {"size": 64, "color": (255, 50, 150), "position": (180, 280)},
        "rank": {"size": 68, "color": (150, 255, 50), "position": (180, 450)}
    }

    # Загрузка шрифта
    try:
        cyber_font = ImageFont.truetype("cyber.ttf", 72)
    except Exception as e:
        logger.error(f"Ошибка загрузки шрифта: {e}")
        cyber_font = ImageFont.load_default()

    # Глитч-эффект для заголовка

    # Основной текст
    texts = [
        f"OPERATOR: {user_name.upper()}",
        f"VOLTS: {volts:,}".replace(",", "'"),
        f"RANK: {rank.upper()}"
    ]

    for key, text in zip(text_style.keys(), texts):
        style = text_style[key]
        # Тень текста
        draw.text(
            (style["position"][0] + 3, style["position"][1] + 3),
            text,
            fill=(0, 0, 0),
            font=ImageFont.truetype("cyber.ttf", style["size"])
        )
        # Основной текст
        draw.text(
            style["position"],
            text,
            fill=style["color"],
            font=ImageFont.truetype("cyber.ttf", style["size"])
        )

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    return img_byte_arr
    
    
def start(update: Update, context: CallbackContext):
    global conn, cursor  # Явное объявление глобальных переменных
    try:
        user = update.effective_user
        cursor.execute(
            "INSERT OR IGNORE INTO users VALUES (?, ?, 0, 'user')",
            (user.id, user.first_name),
        )
        conn.commit()
        
        cursor.execute("SELECT volts, rank FROM users WHERE chatid = ?", (user.id,))
        result = cursor.fetchone()
        volts, rank = (result[0], result[1]) if result else (0, 'user')
        
        img_bytes = generate_volts_image(user.first_name, volts, RANKS[rank])
        update.message.reply_photo(
            photo=InputFile(img_bytes, filename="core_profile.png"),
            caption=f"▣ OPERATOR: {user.first_name}\n■ PROTOCOL: NEON-{RANKS[rank].upper()}",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("⚡ CHARGE CORE"), KeyboardButton("🎖️ CYBER RANKING")]], 
                resize_keyboard=True
            )
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")

def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    
    if user.id == ADMIN_ID and text == "admin":
        update.message.reply_text(f"ID админа: {ADMIN_ID}\nID конфига: {CONFIG_ID}")
        return
    
    if text == "⚡ CHARGE CORE":
        cursor.execute("SELECT volts FROM users WHERE chatid = ?", (user.id,))
        result = cursor.fetchone()
        volts = result[0] + 1 if result else 1
        
        cursor.execute(
            "UPDATE users SET volts = ? WHERE chatid = ?", 
            (volts, user.id)
        )
        conn.commit()
        update.message.reply_text(
            f"▣ CORE OVERDRIVE!\n"
            f"VOLTS: {volts} VT\n"
            f"STATUS: {['■'*i + '□'*(10 - i) for i in range(11)][min(volts // 100, 10)]}"
        )
        
    elif text == "🎖️ CYBER RANKING":  # <-- Исправлен отступ!
        try:
            cursor.execute("SELECT name, volts, rank FROM users ORDER BY volts DESC LIMIT 10")
            top = cursor.fetchall()
            
            if not top:
                update.message.reply_text("▣ CYBER RANKING SYSTEM\nНет данных для отображения.")
                return
            
            response = f"▣ CYBER RANKING SYSTEM\n{'-'*70}\n"
            for i, (name, vt, rank) in enumerate(top, 1):
                rank_display = RANKS.get(rank, "Неизвестный ранг")[:10]
                response += f"▌{i:02d}│ {name[:10]:<10} │ {vt:07d}VT │ {rank_display:<10}▌\n"
            
            update.message.reply_text(f"```\n{response}\n```", parse_mode="MarkdownV2")
        
        except Exception as e:
            logger.error(f"Ошибка в CYBER RANKING: {e}")
            update.message.reply_text("⚠️ Ошибка генерации рейтинга")
        
        
if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    # Запуск автосохранения
    jq = updater.job_queue
    jq.run_repeating(backup_data, interval=30, first=10)
    
    updater.start_polling()
    updater.idle()