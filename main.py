            add_reminder(chat_id, reminder_time, message, context)
        except Exception as e:
            update.message.reply_text(f"⚠️ Ошибка: {e}. Используй формат DD.MM.YYYY HH:MM сообщение.")
    else:
        update.message.reply_text("Для начала нажмите кнопку 'Установить напоминание'.")

def add_reminder(chat_id, reminder_time, message, context):
    job_id = os.urandom(16).hex()

    def job_function():
        context.bot.send_message(chat_id, f"🔔 Напоминание: {message}")
        scheduler.remove_job(job_id)

    scheduler.add_job(job_function, trigger='date', run_date=reminder_time, id=job_id)
    context.bot.send_message(chat_id, f"✅ Напоминание установлено на {reminder_time.strftime('%d.%m.%Y %H:%M')}")

    user_state[chat_id] = None

def show_reminders(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("↩️ Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text("🔔 Функция просмотра напоминаний пока в разработке.", reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == "set_reminder":
        set_reminder_menu(update, context)
    elif data == "custom_date":
        handle_time_selection(update, context)
    elif data == "show_reminders":
        show_reminders(update, context)
    elif data == "main_menu":
        start(update, context)

def main():
    print("⚙️ Запуск main()")
    threading.Thread(target=ping_self, daemon=True).start()
    print("🌐 Пингер запущен")

    print(f"🔑 TOKEN: {'Найден' if TOKEN else 'ОТСУТСТВУЕТ'}")
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    print("🤖 Бот работает и будет жить вечно!")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
