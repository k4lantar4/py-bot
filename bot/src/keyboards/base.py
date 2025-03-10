"""
Base keyboard utilities for the bot.
"""

from typing import List, Union, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

def create_inline_keyboard(
    buttons: List[List[Union[str, InlineKeyboardButton]]],
    callback_prefix: Optional[str] = None
) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard from a list of button data.
    
    Args:
        buttons: List of button rows. Each button can be either a string or InlineKeyboardButton.
        callback_prefix: Optional prefix for callback data when buttons are strings.
        
    Returns:
        InlineKeyboardMarkup instance
    """
    keyboard = []
    
    for row in buttons:
        keyboard_row = []
        for button in row:
            if isinstance(button, str):
                # If button is a string, create a button with text=callback_data=button
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=button,
                        callback_data=f"{callback_prefix}:{button}" if callback_prefix else button
                    )
                )
            else:
                # If button is already an InlineKeyboardButton, use it as is
                keyboard_row.append(button)
        keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(keyboard)

def create_reply_keyboard(
    buttons: List[List[str]],
    resize_keyboard: bool = True,
    one_time_keyboard: bool = False
) -> ReplyKeyboardMarkup:
    """
    Create a reply keyboard from a list of button texts.
    
    Args:
        buttons: List of button rows, each containing button texts
        resize_keyboard: Whether to resize the keyboard
        one_time_keyboard: Whether to hide the keyboard after one use
        
    Returns:
        ReplyKeyboardMarkup instance
    """
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard
    ) 