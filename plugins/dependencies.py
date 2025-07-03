from plugins import Plugin

class DependencyPlugin(Plugin):
    def register(self):
        self.message_handler(commands=['plugins'])(self.list_plugins)
    
    def list_plugins(self, message):
        plugins = "\n".join([
            f"• {name} - {'✅' if name in globals()['loaded_plugins'] else '❌'}"
            for name in globals()['plugin_order']
        ])
        self.bot.reply_to(message, f"📦 Loaded Plugins:\n{plugins}")

def register(bot):
    plugin = DependencyPlugin(bot)
    plugin.register()