from plugins import Plugin
from database.db import get_conn
from managers import profile_manager
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

class ShopPlugin(Plugin):
    def register(self):
        self.message_handler(commands=['add_item_shop'])(self.add_item)
        self.message_handler(commands=['remove_item_shop'])(self.remove_item)
        self.message_handler(commands=['remove_all_items_shop'])(self.remove_all_items)
        self.message_handler(commands=['decrease_item_health'])(self.decrease_item_health)
        self.message_handler(commands=['buy_item'])(self.handle_buy_item_command)
        self.callback_query_handler(func=lambda call: call.data.startswith('shop:'))(self.handle_shop_callback)

    def add_item(self, message):
        args = message.text.split(maxsplit=5)
        if len(args) != 5:
            self.bot.reply_to(message, "❌ فرمت: /add_item_shop name quantity price coin_type")
            return

        name = args[1]
        try:
            quantity = int(args[2])
            price = int(args[3])
        except ValueError:
            self.bot.reply_to(message, "❌ تعداد و قیمت باید عدد باشند.")
            return
        coin_type = args[4]

        with get_conn() as conn:
            conn.execute("INSERT OR REPLACE INTO shop_items VALUES (?, ?, ?, ?, ?)", (name, quantity, price, coin_type, 100))
        self.bot.reply_to(message, f"✅ آیتم '{name}' اضافه شد.")

    def remove_item(self, message):
        args = message.text.split()
        if len(args) != 2:
            self.bot.reply_to(message, "❌ فرمت: /remove_item_shop name")
            return

        with get_conn() as conn:
            conn.execute("DELETE FROM shop_items WHERE name = ?", (args[1],))
        self.bot.reply_to(message, f"🗑 آیتم '{args[1]}' حذف شد.")

    def remove_all_items(self, message):
        with get_conn() as conn:
            conn.execute("DELETE FROM shop_items")
        self.bot.reply_to(message, "🧹 تمام آیتم‌های فروشگاه پاک شدند.")

    def decrease_item_health(self, message):
        args = message.text.split()
        if len(args) != 3:
            self.bot.reply_to(message, "❌ فرمت: /decrease_item_health item_name amount")
            return

        item_name, amount = args[1], int(args[2])
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM player_items WHERE item_name = ?", (item_name,))
            for row in c.fetchall():
                user_id = row[0]
                c.execute("UPDATE player_items SET health = health - ? WHERE user_id = ? AND item_name = ?", (amount, user_id, item_name))
                c.execute("SELECT health FROM player_items WHERE user_id = ? AND item_name = ?", (user_id, item_name))
                health = c.fetchone()[0]
                if health <= 0:
                    c.execute("DELETE FROM player_items WHERE user_id = ? AND item_name = ?", (user_id, item_name))
                    c.execute("UPDATE shop_items SET quantity = quantity + 1 WHERE name = ?", (item_name,))
        self.bot.reply_to(message, f"❤️ سلامت آیتم '{item_name}' کم شد.")

    def handle_shop_callback(self, call):
        user_id = str(call.from_user.id)
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT name, quantity, price, coin_type FROM shop_items WHERE quantity > 0")
            items = c.fetchall()
            if not items:
                self.bot.send_message(call.message.chat.id, "🛒 فروشگاه خالی است.")
                return

            markup = InlineKeyboardMarkup(row_width=1)
            for item in items:
                name, qty, price, coin = item
                btn_text = f"{name} ({qty} موجود | 💰 {price} {coin})"
                markup.add(InlineKeyboardButton(btn_text, callback_data=f"shop:buy:{name}"))

            self.bot.send_message(call.message.chat.id, "🛒 فروشگاه:", reply_markup=markup)

    def handle_buy(self, call, item_name):
        user_id = str(call.from_user.id)
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT quantity, price, coin_type FROM shop_items WHERE name = ?", (item_name,))
            result = c.fetchone()
            if not result:
                self.bot.answer_callback_query(call.id, "❌ آیتم موجود نیست.")
                return

            qty, price, coin_type = result
            player = profile_manager.get_player(user_id)
            if not player:
                self.bot.answer_callback_query(call.id, "❌ پروفایل پیدا نشد.")
                return

            # Check already owned
            c.execute("SELECT 1 FROM player_items WHERE user_id = ? AND item_name = ?", (user_id, item_name))
            if c.fetchone():
                self.bot.answer_callback_query(call.id, "❗️ شما قبلاً این آیتم را خریده‌اید.")
                return

            coin_map = {"طلا": "gold", "نقره": "silver", "برنز": "bronze"}
            col = coin_map.get(coin_type, coin_type)

            if player[f"{col}_coins"] < price:
                self.bot.answer_callback_query(call.id, "❌ سکه کافی موجود نمیباشد.")
                return

            # خرید انجام شود
            profile_manager.remove_coins(user_id, price, col)
            c.execute("UPDATE shop_items SET quantity = quantity - 1 WHERE name = ?", (item_name,))
            c.execute("INSERT INTO player_items (user_id, item_name, health) VALUES (?, ?, 100)", (user_id, item_name))
            self.bot.answer_callback_query(call.id, "✅ خرید انجام شد.")

    def handle_buy_item_command(self, message):
        args = message.text.split(maxsplit=2)
        if len(args) != 3:
            self.bot.reply_to(message, "❌ فرمت درست:\n/buy_item user_id item_name")
            return

        buyer_id = args[1].strip()
        item_name = args[2].strip()

        with get_conn() as conn:
            c = conn.cursor()

            # بررسی موجود بودن آیتم در فروشگاه
            c.execute("SELECT quantity, price, coin_type FROM shop_items WHERE name = ?", (item_name,))
            item = c.fetchone()

            if not item:
                self.bot.reply_to(message, f"❌ آیتم «{item_name}» در فروشگاه وجود ندارد.")
                return

            quantity, price, coin_type_fa = item

            if quantity <= 0:
                self.bot.reply_to(message, f"❌ آیتم «{item_name}» در حال حاضر موجود نیست.")
                return

            # بررسی داشتن آیتم توسط بازیکن
            c.execute("SELECT 1 FROM player_items WHERE user_id = ? AND item_name = ?", (buyer_id, item_name))
            if c.fetchone():
                self.bot.reply_to(message, "⚠️ شما قبلاً این آیتم را خریده‌اید. تا وقتی که آیتم خراب نشود نمی‌توانید دوباره بخرید.")
                return

            # گرفتن اطلاعات سکه بازیکن
            player = profile_manager.get_player(buyer_id)
            if not player:
                self.bot.reply_to(message, "⚠️ ابتدا بازیکن باید پروفایل بسازد.")
                return

            # تبدیل نوع سکه
            coin_map = {"طلا": "gold", "نقره": "silver", "برنز": "bronze"}
            coin_column = coin_map.get(coin_type_fa.strip(), None)

            if not coin_column:
                self.bot.reply_to(message, f"❌ نوع سکه برای آیتم «{item_name}» نامعتبر است.")
                return

            user_coin = player.get(f"{coin_column}_coins", 0)
            if user_coin < price:
                self.bot.reply_to(message, "❌ سکه کافی نمیباشد.")
                return

            # خرید انجام شود
            profile_manager.remove_coins(buyer_id, price, coin_column)
            c.execute("UPDATE shop_items SET quantity = quantity - 1 WHERE name = ?", (item_name,))
            c.execute("INSERT INTO player_items (user_id, item_name, health) VALUES (?, ?, 100)", (buyer_id, item_name))

            self.bot.reply_to(message, f"✅ آیتم «{item_name}» با موفقیت برای بازیکن {buyer_id} خریداری شد.")

            # اگر آیتم تمام شد → در فروشگاه غیرفعال شود (یا حذف موقت)
            c.execute("SELECT quantity FROM shop_items WHERE name = ?", (item_name,))
            remaining = c.fetchone()[0]
            if remaining == 0:
                self.bot.reply_to(message, f"❗️ آیتم «{item_name}» تمام شد و دیگر در فروشگاه موجود نیست.")



def register(bot):
    plugin = ShopPlugin(bot)
    plugin.register()
