from plugins import Plugin
from managers import group_manager
from utils.permissions import is_user_admin

class GroupPlugin(Plugin):
    def register(self):
        self.message_handler(commands=['ثبت_گروه_بازیکن'])(self.register_group)
    
    def register_group(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # Only works in groups
        if message.chat.type not in ['group', 'supergroup']:
            self.bot.reply_to(message, "⛔ این دستور فقط در گروه قابل استفاده است.")
            return
        
        # Check if user is admin
        if not is_user_admin(self.bot, chat_id, user_id):
            self.bot.reply_to(message, "⛔ فقط ادمین‌ها می‌توانند این دستور را اجرا کنند.")
            return
        
        args = message.text.split()
        if len(args) != 2:
            self.bot.reply_to(message, "❌ فرمت درست:\n/ثبت_گروه_بازیکن user_id")
            return
        
        player_id = args[1]
        if group_manager.set_player_group(player_id, str(chat_id)):
            self.bot.reply_to(message, f"✅ گروه فعلی به عنوان گروه اختصاصی برای کاربر {player_id} ثبت شد.")
        else:
            self.bot.reply_to(message, f"❌ ثبت گروه برای کاربر {player_id} انجام نشد.")

def register(bot):
    plugin = GroupPlugin(bot)
    plugin.register()