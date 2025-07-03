from plugins import Plugin
import importlib
from utils.permissions import *
class ReloadPlugin(Plugin):
    def register(self):
        self.message_handler(commands=['reload'])(self.handle_reload)
    
    def handle_reload(self, message):
        if not is_user_admin(self.bot, message.chat.id, message.from_user.id):
            self.bot.reply_to(message, "⛔ Only admins can reload plugins")
            return
        
        args = message.text.split()
        if len(args) < 2:
            self.bot.reply_to(message, "Usage: /reload <plugin_name> or /reload all")
            return
        
        target = args[1]
        if target == "all":
            # Reload all plugins
            for plugin_name in list(globals()["loaded_plugins"].keys()):
                self.reload_plugin(plugin_name)
            self.bot.reply_to(message, "♻️ All plugins reloaded")
        else:
            # Reload specific plugin
            if self.reload_plugin(target):
                self.bot.reply_to(message, f"♻️ Plugin {target} reloaded")
            else:
                self.bot.reply_to(message, f"❌ Failed to reload {target}")
    
    def reload_plugin(self, plugin_name):
        if plugin_name not in globals()["loaded_plugins"]:
            return False
        
        try:
            module = importlib.reload(globals()["loaded_plugins"][plugin_name])
            globals()["loaded_plugins"][plugin_name] = module
            
            # Re-register plugin
            if hasattr(module, "register"):
                # Unregister old handlers
                if hasattr(module, "registered_handlers"):
                    for handler in module.registered_handlers:
                        self.bot.remove_message_handler(handler)
                
                # Clear and re-register
                module.registered_handlers = []
                module.register(self.bot)
            
            return True
        except Exception as e:
            print(f"Reload error: {str(e)}")
            return False

def register(bot):
    plugin = ReloadPlugin(bot)
    plugin.register()