import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from aiohttp import web

# Obtén los tokens de los bots desde las variables de entorno
BOT1_TOKEN = os.getenv("BOT1_TOKEN")
BOT2_TOKEN = os.getenv("BOT2_TOKEN")

# Configura la URL base para los webhooks (Render te dará esta URL)
WEBHOOK_URL_BASE = os.getenv("WEBHOOK_URL_BASE", "https://<TU_RENDER_DOMINIO>.onrender.com")

# Configura el primer bot
def setup_bot1():
    async def start(update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("Pulsa aquí", url="https://t.me/Uniquejerseyghr_menu_bot?start=start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="\U0001F447 Pulsa aquí para acceder al menú de la tienda \U0001F447",
            reply_markup=reply_markup
        )

    async def handle_message(update: Update, context: CallbackContext) -> None:
        if update.message and update.message.text:
            await start(update, context)

    application = Application.builder().token(BOT1_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, handle_message))

    return application

# Configura el segundo bot
def setup_bot2():
    async def start(update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("HACER PEDIDO", url='https://t.me/alh_1997')],
            [InlineKeyboardButton("VER ESTADO DEL PEDIDO", callback_data='ver_estado_del_pedido')],
            [InlineKeyboardButton("VER CATALOGO", callback_data='ver_catalogo')],
            [InlineKeyboardButton("GUIA DE TALLAS", callback_data='guia_de_tallas')],
            [InlineKeyboardButton("PRECIOS", callback_data='precios')],
            [InlineKeyboardButton("PROMOS", callback_data='promos')],
            [InlineKeyboardButton("REDES SOCIALES", callback_data='redes_sociales')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hola, aquí tienes el menú de la tienda Uniquejerseyghr. Elige lo que necesites:",
            reply_markup=reply_markup
        )

    async def handle_callback(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()
        back_to_main_menu_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al menú principal", callback_data='main_menu')]])

        if query.data == 'ver_estado_del_pedido':
            await query.edit_message_text(
                "Aquí puedes ver el estado de tu pedido: http://123.207.20.21:8082/en/trackIndex.htm",
                reply_markup=back_to_main_menu_keyboard
            )
        elif query.data == 'ver_catalogo':
            keyboard = [
                [InlineKeyboardButton("CAMISETAS DE FÚTBOL", callback_data='catalogo_futbol')],
                [InlineKeyboardButton("⬅️ Volver al menú principal", callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "Elige una categoría del catálogo:",
                reply_markup=reply_markup
            )
        elif query.data == 'catalogo_futbol':
            await query.edit_message_text(
                "Has seleccionado CAMISETAS DE FÚTBOL https://drive.google.com/drive/folders/1lxyq6EjtylR8RlLGzB25OBBWEWt2wn6P.",
                reply_markup=back_to_main_menu_keyboard
            )
        # Agrega más opciones aquí según tu lógica...

    async def handle_message(update: Update, context: CallbackContext) -> None:
        if update.message.chat.type == "private":
            await start(update, context)

    application = Application.builder().token(BOT2_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_message))

    return application

# Inicializa ambos bots
bot1 = setup_bot1()
bot2 = setup_bot2()

# Configura los webhooks para ambos bots
async def set_webhook(application, token, path):
    url = f"{WEBHOOK_URL_BASE}{path}"
    await application.bot.set_webhook(url=url)

async def setup_webhooks():
    await set_webhook(bot1, BOT1_TOKEN, "/bot1")
    await set_webhook(bot2, BOT2_TOKEN, "/bot2")

# Crea la aplicación web para manejar los webhooks
app = web.Application()
app.add_routes([
    web.post("/bot1", bot1.webhook_handler),
    web.post("/bot2", bot2.webhook_handler),
])

# Inicia el servidor web
if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_webhooks())
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8443)))
