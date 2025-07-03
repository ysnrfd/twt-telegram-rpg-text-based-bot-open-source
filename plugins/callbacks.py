from plugins import Plugin
from utils.memory import get_user_by_message


class CallbacksPlugin(Plugin):
    def register(self):
        # Only handle callbacks not handled by other plugins
        self.callback_query_handler(func=lambda call: call.data.startswith('pets:'))(
            self.handle_pets_callback
        )
    
    def handle_pets_callback(self, call):
        self.bot.answer_callback_query(call.id, "🐾 سیستم پت‌ها به زودی اضافه خواهد شد!")

def register(bot):
    plugin = CallbacksPlugin(bot)
    plugin.register()