from plugins import Plugin
from managers import skill_manager
from levels.level_table import level_table

class SkillsPlugin(Plugin):
    def register(self):
        self.message_handler(commands=['set_skill_level'])(self.handle_set_skill)
    
    def handle_set_skill(self, message):
        args = message.text.split()
        if len(args) != 4:
            self.bot.reply_to(message, "❌ فرمت درست:\n/set_skill_level user_id skill_name level\nمثال:\n/set_skill_level 123456789 شمشیرزنی F")
            return
        
        user_id, skill_name, level = args[1], args[2], args[3]
        valid_levels = [lvl for lvl, _, _ in level_table] + [to_lvl for _, to_lvl, _ in level_table]
        
        if level not in valid_levels:
            self.bot.reply_to(message, f"❌ سطح نامعتبر است. یکی از این‌ها باشه:\n{', '.join(valid_levels)}")
            return
        
        if skill_manager.set_skill_level(user_id, 'combat', skill_name, level):
            self.bot.reply_to(message, f"✅ مهارت رزمی {skill_name} با سطح {level} برای کاربر {user_id} ثبت شد.")
        else:
            self.bot.reply_to(message, f"❌ ثبت مهارت برای کاربر {user_id} انجام نشد.")

def register(bot):
    plugin = SkillsPlugin(bot)
    plugin.register()