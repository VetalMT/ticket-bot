from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
)
from fpdf import FPDF

# Етапи розмови
STATION_FROM, STATION_TO, DATE, TIME, NAME = range(5)

# Старт
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("🚏 Введіть станцію відправлення:")
    return STATION_FROM

# Крок 1
def station_from(update: Update, context: CallbackContext) -> int:
    context.user_data['station_from'] = update.message.text
    update.message.reply_text("🛤 Введіть станцію прибуття:")
    return STATION_TO

# Крок 2
def station_to(update: Update, context: CallbackContext) -> int:
    context.user_data['station_to'] = update.message.text
    update.message.reply_text("📅 Введіть дату відправлення (напр. 22.05.2025):")
    return DATE

# Крок 3
def date(update: Update, context: CallbackContext) -> int:
    context.user_data['date'] = update.message.text
    update.message.reply_text("⏰ Введіть час відправлення (напр. 14:30):")
    return TIME

# Крок 4
def time(update: Update, context: CallbackContext) -> int:
    context.user_data['time'] = update.message.text
    update.message.reply_text("👤 Введіть ПІБ пасажира:")
    return NAME

# Крок 5 – завершення
def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text

    # Створення PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Автобусний квиток", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"З: {context.user_data['station_from']}", ln=True)
    pdf.cell(200, 10, txt=f"До: {context.user_data['station_to']}", ln=True)
    pdf.cell(200, 10, txt=f"Дата: {context.user_data['date']}", ln=True)
    pdf.cell(200, 10, txt=f"Час: {context.user_data['time']}", ln=True)
    pdf.cell(200, 10, txt=f"Пасажир: {context.user_data['name']}", ln=True)

    pdf.output("ticket.pdf")

    # Надсилання PDF
    update.message.reply_document(open("ticket.pdf", "rb"))

    # Кнопка «Створити наступний квиток»
    keyboard = [['🎫 Створити наступний квиток']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("✅ Ваш квиток готовий! Створити ще один?", reply_markup=reply_markup)

    return ConversationHandler.END

# Обробка кнопки «Створити наступний квиток»
def handle_next_ticket(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    return start(update, context)

# Скасування
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("❌ Операцію скасовано.")
    return ConversationHandler.END

# Запуск бота
def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATION_FROM: [MessageHandler(Filters.text & ~Filters.command, station_from)],
            STATION_TO: [MessageHandler(Filters.text & ~Filters.command, station_to)],
            DATE: [MessageHandler(Filters.text & ~Filters.command, date)],
            TIME: [MessageHandler(Filters.text & ~Filters.command, time)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Обробник кнопки
    dispatcher.add_handler(MessageHandler(Filters.text("🎫 Створити наступний квиток"), handle_next_ticket))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
