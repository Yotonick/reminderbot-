from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import os
import logging

# Логирование для ошибок
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
TOKEN = os.getenv('TOKEN')

# Начальная команда /start
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Установить напоминание", callback_data='set_reminder')],
        [InlineKeyboardButton("Посмотреть напоминания", callback_data='view_reminders')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Я напоминальщик. Выберите опцию ниже:", reply_markup=reply_markup)

# Функция установки напоминания
async def set_reminder(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data='set_today')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("Для начала выберите дату:", reply_markup=reply_markup)

# Функция для выбора даты (например, сегодня)
async def set_today(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("Напоминаю... Напишите текст напоминания:", reply_markup=reply_markup)

# Функция для обработки текста напоминания
async def handle_message(update: Update, context):
    # Получаем текст сообщения и устанавливаем напоминание
    reminder_text = update.message.text
    job_time = datetime.now(pytz.timezone("Europe/Minsk")) + timedelta(minutes=1)  # Настроим на 1 минуту от текущего времени
    context.job_queue.run_once(send_reminder, (job_time - datetime.now()).total_seconds(), context=reminder_text)
    await update.message.reply_text(f"Напоминание установлено на {job_time.strftime('%H:%M')} с сообщением: {reminder_text}")

# Функция для отправки напоминания
async def send_reminder(context):
    reminder_text = context.job.context
    await context.bot.send_message(chat_id=context.job.context, text=f"🔔 Напоминание: {reminder_text}")

# Функция для возврата в меню
async def back(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Установить напоминание", callback_data='set_reminder')],
        [InlineKeyboardButton("Посмотреть напоминания", callback_data='view_reminders')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("Вы вернулись в главное меню", reply_markup=reply_markup)

# Основная функция для запуска бота
async def main():
    # Создаем приложение с токеном
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(set_reminder, pattern='^set_reminder$'))
    application.add_handler(CallbackQueryHandler(set_today, pattern='^set_today$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(back, pattern='^back$'))

    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
