from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
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
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Установить напоминание", callback_data='set_reminder')],
        [InlineKeyboardButton("Посмотреть напоминания", callback_data='view_reminders')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Привет! Я напоминальщик. Выберите опцию ниже:", reply_markup=reply_markup)

# Функция установки напоминания
def set_reminder(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data='set_today')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text("Для начала выберите дату:", reply_markup=reply_markup)

# Функция для выбора даты (например, сегодня)
def set_today(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text("Напоминаю... Напишите текст напоминания:", reply_markup=reply_markup)

# Функция для обработки текста напоминания
def handle_message(update: Update, context: CallbackContext):
    # Получаем текст сообщения и устанавливаем напоминание
    reminder_text = update.message.text
    job_time = datetime.now(pytz.timezone("Europe/Minsk")) + timedelta(minutes=1)  # Настроим на 1 минуту от текущего времени
    context.job_queue.run_once(send_reminder, (job_time - datetime.now()).total_seconds(), context=reminder_text)
    update.message.reply_text(f"Напоминание установлено на {job_time.strftime('%H:%M')} с сообщением: {reminder_text}")

# Функция для отправки напоминания
def send_reminder(context: CallbackContext):
    reminder_text = context.job.context
    context.bot.send_message(chat_id=context.job.context, text=f"🔔 Напоминание: {reminder_text}")

# Функция для возврата в меню
def back(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Установить напоминание", callback_data='set_reminder')],
        [InlineKeyboardButton("Посмотреть напоминания", callback_data='view_reminders')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.edit_text("Вы вернулись в главное меню", reply_markup=reply_markup)

# Основная функция для запуска бота
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(set_reminder, pattern='^set_reminder$'))
    dp.add_handler(CallbackQueryHandler(set_today, pattern='^set_today$'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(back, pattern='^back$'))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
