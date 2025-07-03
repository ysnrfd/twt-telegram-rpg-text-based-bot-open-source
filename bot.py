import telebot
import importlib
import os
import sys
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database.db import init_db

# Configuration
BOT_TOKEN = ''

# Global state
bot = telebot.TeleBot(BOT_TOKEN)
loaded_plugins = {}
plugin_order = []

class PluginReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            filename = os.path.basename(event.src_path)
            module_name = filename[:-3]
            if module_name in loaded_plugins:
                reload_plugin(module_name)
                print(f"♻️ Reloaded plugin: {module_name}")

def load_plugin(module_name):
    try:
        module = importlib.import_module(f"plugins.{module_name}")
        if hasattr(module, "register"):
            module.register(bot)
            loaded_plugins[module_name] = module
            plugin_order.append(module_name)
            print(f"✅ Loaded plugin: {module_name}")
            return True
    except Exception as e:
        print(f"❌ Failed to load {module_name}: {str(e)}")
    return False

def reload_plugin(module_name):
    try:
        module = importlib.reload(loaded_plugins[module_name])
        if hasattr(module, "register"):
            # Unregister old handlers
            if hasattr(module, "registered_handlers"):
                for handler in module.registered_handlers:
                    bot.remove_message_handler(handler)
            
            # Clear and re-register
            module.registered_handlers = []
            module.register(bot)
            print(f"🔄 Reloaded plugin: {module_name}")
            return True
    except Exception as e:
        print(f"❌ Failed to reload {module_name}: {str(e)}")
    return False

def load_all_plugins():
    plugin_dir = "plugins"
    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            load_plugin(module_name)

def setup_reloader():
    event_handler = PluginReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path="plugins", recursive=False)
    observer.start()
    return observer

def graceful_shutdown(signum, frame):
    print("\n🛑 Shutting down bot gracefully...")
    if 'observer' in globals():
        observer.stop()
        observer.join()
    sys.exit(0)

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Load plugins
    load_all_plugins()
    
    # Setup hot reloading
    observer = setup_reloader()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    # Start bot
    print(f"🤖 Bot started with {len(loaded_plugins)} plugins")
    bot.polling(non_stop=True)