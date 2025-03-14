from .auth import auth_handlers
from .chat import chat_handlers

handlers = [
    *auth_handlers,
    *chat_handlers,
] 