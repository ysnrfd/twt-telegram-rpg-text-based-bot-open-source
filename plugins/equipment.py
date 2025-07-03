from plugins import Plugin
from managers import equipment_manager

class EquipmentPlugin(Plugin):
    def register(self):
        self.message_handler(commands=['add_equipment'])(self.handle_add)
        self.message_handler(commands=['remove_equipment'])(self.handle_remove)
        self.callback_query_handler(func=lambda call: call.data.startswith('equipment:'))(
            self.handle_callback
        )
    
    def handle_add(self, message):
        args = message.text.split(maxsplit=2)
        if len(args) != 3:
            self.bot.reply_to(message, "❌ /add_equipment user_id item_name")
            return
        
        user_id, item = args[1], args[2]
        if equipment_manager.add_equipment(user_id, item):
            self.bot.reply_to(message, f"🎒 تجهیز '{item}' برای کاربر {user_id} افزوده شد.")
        else:
            self.bot.reply_to(message, f"❌ افزودن تجهیز برای کاربر {user_id} انجام نشد.")
    
    def handle_remove(self, message):
        args = message.text.split(maxsplit=2)
        if len(args) != 3:
            self.bot.reply_to(message, "❌ /remove_equipment user_id item_name")
            return
        
        user_id, item = args[1], args[2]
        if equipment_manager.remove_equipment(user_id, item):
            self.bot.reply_to(message, f"🗑 تجهیز '{item}' از کاربر {user_id} حذف شد.")
        else:
            self.bot.reply_to(message, f"❌ حذف تجهیز برای کاربر {user_id} انجام نشد.")
    
    def handle_callback(self, call):
        _, user_id = call.data.split(':')
        equipment = equipment_manager.get_equipment(user_id)
        
        if equipment:
            text = "🎒 تجهیزات:\n" + "\n".join(f"➤ {item}" for item in equipment)
        else:
            text = "🎒 شما هیچ تجهیزاتی ندارید!"
        
        # Answer the callback and send message
        try:
            self.bot.answer_callback_query(call.id)
            self.bot.send_message(call.message.chat.id, text)
        except Exception as e:
            print(f"Error handling equipment callback: {e}")

def register(bot):
    plugin = EquipmentPlugin(bot)
    plugin.register()