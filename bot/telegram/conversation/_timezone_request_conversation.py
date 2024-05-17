from datetime import datetime
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, Message
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters
)
from timezonefinder import TimezoneFinder

from llm.models import UserData
from ._command_conversation import CommandConversation
from client import TelegramClient

import pytz

class TimezoneRequestConversation(CommandConversation):
    def __init__(self, TIMEZONE_REQ: int, client: TelegramClient, debug: bool = True) -> None:
        super().__init__(debug)
        self.client = client
        self.TIMEZONE_REQ = TIMEZONE_REQ

        self._states = [
            MessageHandler(filters.LOCATION, self.receive_user_location_from_button),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.client_receive_user_timezone_from_text)
            ]

    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_data = context.user_data.get('user_system_data', None)

        if not user_data:
            await update.message.reply_text("Please use /start command to start the bot.")
            return ConversationHandler.END


        await update.message.reply_text(
            "Please press the button to share your location or type your location.\n"\
            "For example: You are in <b>GMT+7</b>. Type <b>+7</b>.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Share Location", request_location=True)]], 
                one_time_keyboard=True),
                parse_mode='HTML'
                )
        return self.TIMEZONE_REQ



    async def client_receive_user_timezone_from_text(self, update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if 'user_system_data' not in context.user_data:
            await update.message.reply_text("Please use /start command to start the bot.")
            return
        
        location_text = update.message.text

        user_data = context.user_data['user_system_data']
        
        response =  await self.client.receive_user_timezone_from_text(user_data, location_text)

        context.user_data['user_system_data'] = user_data

        print(user_data.timezone)

        await update.message.reply_text(response)

        return ConversationHandler.END


    
    async def receive_user_location_from_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_location = update.message.location
        if user_location:
            message = await update.message.reply_text("Got it! Please wait a moment.")
            await self._handle_receive_data(update, context, user_location, message)
        else:
            await update.message.reply_text("Could not get your location. Please try again.")
        
        return ConversationHandler.END
        
    async def _handle_receive_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE, location: dict, message: Message) -> None:
        context.user_data['location'] = location
        user_data: UserData = context.user_data.get('user_system_data', None)

        if not user_data:
            await message.edit_text("Please use /start command to start the bot.")
            return

        context.user_data['location'] = location

        tf = TimezoneFinder()
        
        timezone = pytz.timezone(tf.timezone_at(lng=location['longitude'], lat=location['latitude']))

        user_data.timezone = timezone

        context.user_data['timezone'] = timezone
        current_time = datetime.now(timezone).strftime("%H:%M")

        await message.edit_text(f"Your timezone is {timezone} and the current time is {current_time}")
            

        