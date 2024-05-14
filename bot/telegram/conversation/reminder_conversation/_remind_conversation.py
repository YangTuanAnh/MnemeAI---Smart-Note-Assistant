from telegram import Message, Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from .._command_conversation import CommandConversation
from client import TelegramClient

class RemindConversation(CommandConversation):
    def __init__(self, REMIND_TEXT: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.REMIND_TEXT = REMIND_TEXT

        self._states = [MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_remind_text)]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if(context.args):
            remind_text = ' '.join(context.args)
            await self._handle_receive_remind_text(update, context, remind_text)
            return ConversationHandler.END
        await update.message.reply_text("Please send me the details of the reminder.")
        return self.REMIND_TEXT
    
    async def receive_remind_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        remind_text = update.message.text
        message = await update.message.reply_text("Got it! Please wait a moment.")
        await self._handle_receive_remind_text(update, context, remind_text, message)
        return ConversationHandler.END
    

    async def _handle_receive_remind_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, remind_text: str, message: Message) -> None:
        chat_id = update.message.chat_id
        response_text = await self.client.save_remind(chat_id, remind_text)
        
        await message.edit_text(response_text)