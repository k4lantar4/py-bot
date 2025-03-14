from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler
)
from django.utils.translation import gettext as _
from django.db.models import Q

from ...models.chat import ChatSession, ChatAgent, ChatMessage
from ...services.chat import ChatManager
from ..decorators import authenticated_user
from ..utils import get_user_data


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chat command"""
    if not update.message:
        return

    user_data = await get_user_data(update.effective_user.id)
    if not user_data:
        await update.message.reply_text(
            _('Please login first using /login command')
        )
        return

    # Check if user has active chat
    active_chat = ChatSession.objects.filter(
        user=user_data['user'],
        status__in=['WAITING', 'ACTIVE']
    ).first()

    if active_chat:
        await update.message.reply_text(
            _('You already have an active chat. Please close it first.')
        )
        return

    # Ask for chat subject
    await update.message.reply_text(
        _('Please enter the subject of your chat:')
    )
    context.user_data['chat_state'] = 'WAITING_SUBJECT'


async def chat_subject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle chat subject input"""
    if not update.message or 'chat_state' not in context.user_data:
        return

    user_data = await get_user_data(update.effective_user.id)
    if not user_data:
        return

    subject = update.message.text

    # Create chat session
    session = ChatManager.start_chat(
        user=user_data['user'],
        subject=subject,
        category='SUPPORT'  # Default category
    )

    # Send confirmation
    keyboard = [
        [
            InlineKeyboardButton(
                _('Close Chat'),
                callback_data=f'close_chat:{session.id}'
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        _('Chat started! Our support team will join shortly.\n'
          'You can start typing your messages now.'),
        reply_markup=reply_markup
    )

    # Clear chat state
    context.user_data.pop('chat_state', None)


async def chat_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle chat messages"""
    if not update.message:
        return

    user_data = await get_user_data(update.effective_user.id)
    if not user_data:
        return

    # Check if user has active chat
    active_chat = ChatSession.objects.filter(
        user=user_data['user'],
        status__in=['WAITING', 'ACTIVE']
    ).first()

    if not active_chat:
        await update.message.reply_text(
            _('No active chat found. Use /chat to start a new chat.')
        )
        return

    # Handle different message types
    if update.message.text:
        content = update.message.text
        message_type = 'TEXT'
        file_data = {}
    elif update.message.document:
        content = update.message.caption or ''
        message_type = 'DOCUMENT'
        file_data = {
            'file_url': update.message.document.file_id,
            'file_name': update.message.document.file_name,
            'file_size': update.message.document.file_size
        }
    elif update.message.photo:
        content = update.message.caption or ''
        message_type = 'PHOTO'
        photo = update.message.photo[-1]  # Get largest photo
        file_data = {
            'file_url': photo.file_id,
            'file_name': 'photo.jpg',
            'file_size': None
        }
    else:
        await update.message.reply_text(
            _('This message type is not supported.')
        )
        return

    # Send message
    ChatManager.send_message(
        session=active_chat,
        sender=user_data['user'],
        content=content,
        message_type=message_type,
        **file_data
    )


async def close_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle close chat button callback"""
    if not update.callback_query:
        return

    query = update.callback_query
    chat_id = query.data.split(':')[1]

    user_data = await get_user_data(update.effective_user.id)
    if not user_data:
        await query.answer(_('Please login first'))
        return

    try:
        session = ChatSession.objects.get(
            id=chat_id,
            user=user_data['user']
        )
    except ChatSession.DoesNotExist:
        await query.answer(_('Chat not found'))
        return

    if session.status not in ['WAITING', 'ACTIVE']:
        await query.answer(_('Chat is already closed'))
        return

    # Close chat
    ChatManager.close_chat(session=session)

    # Ask for rating
    keyboard = [
        [
            InlineKeyboardButton(
                f"⭐ {i}",
                callback_data=f'rate_chat:{session.id}:{i}'
            ) for i in range(1, 6)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        _('Chat closed. How would you rate this chat?'),
        reply_markup=reply_markup
    )
    await query.answer()


async def rate_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle chat rating callback"""
    if not update.callback_query:
        return

    query = update.callback_query
    _, chat_id, rating = query.data.split(':')
    rating = int(rating)

    user_data = await get_user_data(update.effective_user.id)
    if not user_data:
        await query.answer(_('Please login first'))
        return

    try:
        session = ChatSession.objects.get(
            id=chat_id,
            user=user_data['user']
        )
    except ChatSession.DoesNotExist:
        await query.answer(_('Chat not found'))
        return

    # Update rating
    ChatManager.close_chat(
        session=session,
        rating=rating
    )

    await query.message.edit_text(
        _('Thank you for your feedback! 🙏\n'
          'You can start a new chat anytime using /chat command.')
    )
    await query.answer()


# Register handlers
chat_handlers = [
    CommandHandler('chat', chat_command),
    MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE &
        filters.StateFilter('WAITING_SUBJECT'),
        chat_subject_handler
    ),
    MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.Document.ALL) &
        filters.ChatType.PRIVATE,
        chat_message_handler
    ),
    CallbackQueryHandler(close_chat_callback, pattern=r'^close_chat:\d+$'),
    CallbackQueryHandler(rate_chat_callback, pattern=r'^rate_chat:\d+:\d$')
] 