from plugins import Plugin

class LifecyclePlugin(Plugin):
    def on_startup(self):
        print("🔌 Lifecycle plugin started")
    
    def on_shutdown(self):
        print("🛑 Lifecycle plugin stopped")
    
    def register(self):
        pass  # No commands needed for lifecycle

def register(bot):
    plugin = LifecyclePlugin(bot)
    plugin.register()