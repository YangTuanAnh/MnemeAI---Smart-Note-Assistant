
from ._note_pages import NotePages

from client import TelegramClient

from bot.telegram.ui_templates import get_reminder_option_keyboard, create_preview_pages

from telegram_bot_pagination import InlineKeyboardPaginator

from telegram import CallbackQuery

import re

class ReminderPages(NotePages):
    def __init__(self, client: TelegramClient) -> None:
        super().__init__(client)

    def get_option_keyboard(self, note_idx: str) -> list:
        return get_reminder_option_keyboard(note_idx) 

    def init_preview_pages(self, page: int = 1) -> InlineKeyboardPaginator:
        return create_preview_pages(self.client.get_total_reminder_pages(), page, pattern='r#{page}')
    
    def check_match_pattern(self, query: CallbackQuery) -> bool:

        return re.match(r'r#(\d+)', query.data)
    
    def client_get_content(self, chat_id, note_idx) -> str:
        return self.client.get_reminder_content(chat_id, note_idx)
    
    def client_get_total_pages(self) -> int:
        return self.client.get_total_reminder_pages()
    