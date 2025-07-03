from plugins import Plugin
from managers import profile_manager, group_manager
from utils.permissions import *
from utils.events import event_system, PLAYER_CREATED
from managers import skill_manager
import telebot


class PlayerPlugin(Plugin):
    def register(self):
        self.message_handler(commands=['start'])(self.handle_start)
        self.message_handler(commands=['create_player'])(self.handle_create_player)
        self.message_handler(commands=['set_age'])(self.handle_set_age)
        self.message_handler(commands=['add_coins'])(self.handle_add_coins)
        self.message_handler(commands=['set_player_level'])(self.handle_set_player_level)
        self.message_handler(commands=['show_profile'])(self.handle_show_profile)
        self.message_handler(commands=['add_coins'])(self.handle_add_coins)
        self.callback_query_handler(func=lambda call: call.data.startswith("view:"))(
    self.handle_view_section
)
        self.message_handler(commands=['add_coins'])(self.handle_add_coins)
        self.message_handler(commands=['remove_coins'])(self.handle_remove_coins)
        



    
    def handle_start(self, message):
        user_id = str(message.from_user.id)
        name = message.from_user.first_name
        
        # Create player if doesn't exist
        if not profile_manager.get_player(user_id):
            profile_manager.create_player(user_id, name)
            event_system.publish(PLAYER_CREATED, {
                "user_id": user_id,
                "name": name
            })
        
        # Get player group
        group_id = group_manager.get_player_group(user_id)
        
        if not group_id:
            self.bot.reply_to(message, "⚠️ هنوز گروه اختصاصی شما ثبت نشده است.")
            return
        
        player = profile_manager.get_player(user_id)
        # Get skills for profile
        skills_combat = skill_manager.get_skills(user_id, "combat")
        skills_common = skill_manager.get_skills(user_id, "common")
        skills_special = skill_manager.get_skills(user_id, "special")
        
        msg = self.bot.send_message(
            group_id, 
            profile_manager.format_profile(player, skills_combat, skills_common, skills_special),
            reply_markup=self.get_profile_buttons(user_id)
        )
        
        # Link message to user
        from utils.memory import link_message_to_user
        link_message_to_user(msg.message_id, user_id)
        
        self.bot.reply_to(message, "✅ پروفایل شما در گروه اختصاصی‌تان ارسال شد.")
    
    def handle_create_player(self, message):
        args = message.text.split(maxsplit=3)
        if len(args) != 4:
            self.bot.reply_to(message, "❌ فرمت درست:\n/create_player user_id name age")
            return
        
        user_id = args[1]
        name = args[2]
        
        try:
            age = int(args[3])
        except ValueError:
            self.bot.reply_to(message, "❌ مقدار سن باید عدد باشد.")
            return
        
        if profile_manager.create_player(user_id, name, age):
            event_system.publish(PLAYER_CREATED, {
                "user_id": user_id,
                "name": name,
                "age": age
            })
            self.bot.reply_to(message, f"✅ بازیکن با نام '{name}' برای آیدی {user_id} ساخته شد.")
        else:
            self.bot.reply_to(message, f"⚠️ بازیکن {user_id} از قبل وجود دارد.")
    
    def handle_set_age(self, message):
        args = message.text.split()
        if len(args) != 3:
            self.bot.reply_to(message, "❌ /set_age user_id age")
            return
        
        user_id, age = args[1], int(args[2])
        if profile_manager.set_age(user_id, age):
            self.bot.reply_to(message, f"👤 سن کاربر {user_id} به {age} تنظیم شد.")
        else:
            self.bot.reply_to(message, f"❌ تنظیم سن برای کاربر {user_id} انجام نشد.")
    
    def handle_add_coins(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        # بررسی ادمین بودن
        if not is_user_admin(self.bot, chat_id, user_id):
            self.bot.reply_to(message, "⛔ فقط ادمین‌ها یا سازنده گروه می‌توانند از این دستور استفاده کنند.")
            return

        args = message.text.split()
        if len(args) != 4:
            self.bot.reply_to(message, "❌ فرمت درست:\n/add_coins user_id amount type\nمثلاً:\n/add_coins 123 10 طلا")
            return

        target_id, amount, coin_type_fa = args[1], args[2], args[3]

        try:
            amount = int(amount)
        except ValueError:
            self.bot.reply_to(message, "❌ مقدار سکه باید عدد باشد.")
            return

        # نگاشت نوع سکه فارسی به نوع قابل ذخیره
        coin_map = {"طلا": "gold", "نقره": "silver", "برنز": "bronze"}
        coin_type = coin_map.get(coin_type_fa, None)

        if not coin_type:
            self.bot.reply_to(message, "❌ نوع سکه نامعتبر است. فقط 'طلا'، 'نقره'، 'برنز'.")
            return

        success = profile_manager.add_coins(target_id, amount, coin_type)
        if success:
            self.bot.reply_to(message, f"✅ {amount} سکه {coin_type_fa} به کاربر {target_id} اضافه شد.")
        else:
            self.bot.reply_to(message, f"❌ افزودن سکه برای کاربر {target_id} انجام نشد.")

    
    def handle_remove_coins(self, message):
        args = message.text.split()
        if len(args) != 4:
            self.bot.reply_to(message, "❌ /remove_coins user_id amount type\nمثلاً:\n/remove_coins 123 5 silver")
            return
    
        user_id, amount, coin_type = args[1], int(args[2]), args[3]
        if profile_manager.remove_coins(user_id, amount, coin_type):
            self.bot.reply_to(message, f"🪙 {amount} {coin_type} از کاربر {user_id} کم شد.")
        else:
            self.bot.reply_to(message, f"❌ حذف سکه برای کاربر {user_id} انجام نشد.")


    
    def handle_set_player_level(self, message):
        args = message.text.split()
        if len(args) != 3:
            self.bot.reply_to(message, "❌ /set_player_level user_id level")
            return
        
        user_id, level = args[1], args[2]
        try:
            if profile_manager.set_player_level(user_id, level):
                self.bot.reply_to(message, f"✅ سطح توانایی {level} برای کاربر {user_id} تنظیم شد.")
            else:
                self.bot.reply_to(message, f"❌ تنظیم سطح برای کاربر {user_id} انجام نشد.")
        except ValueError:
            self.bot.reply_to(message, "❌ سطح نامعتبر است.")
    
    def handle_show_profile(self, message):
        args = message.text.split()
        if len(args) != 2:
            self.bot.reply_to(message, "❌ /show_profile user_id")
            return
        
        user_id = args[1]
        group_id = group_manager.get_player_group(user_id)
        
        if not group_id:
            self.bot.reply_to(message, "❌ این بازیکن گروه اختصاصی ندارد.")
            return
        
        player = profile_manager.get_player(user_id)
        if not player:
            self.bot.reply_to(message, f"❌ بازیکن با آیدی {user_id} وجود ندارد.")
            return
        
        # Get skills for profile
        skills_combat = skill_manager.get_skills(user_id, "combat")
        skills_common = skill_manager.get_skills(user_id, "common")
        skills_special = skill_manager.get_skills(user_id, "special")
        
        msg = self.bot.send_message(
            group_id,
            profile_manager.format_profile(player, skills_combat, skills_common, skills_special),
            reply_markup=self.get_profile_buttons(user_id)
        )
        
        # Link message to user
        from utils.memory import link_message_to_user
        link_message_to_user(msg.message_id, user_id)
        
        self.bot.reply_to(message, f"📤 پروفایل برای گروه کاربر {user_id} ارسال شد.")
    
    # ADD THIS MISSING METHOD
    def get_profile_buttons(self, user_id):
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("🎒 تجهیزات", callback_data=f"view:equipment:{user_id}"),
            telebot.types.InlineKeyboardButton("🐾 پت‌ها", callback_data=f"view:pets:{user_id}"),
            telebot.types.InlineKeyboardButton("💰 سکه‌ها", callback_data=f"view:coins:{user_id}"),
            telebot.types.InlineKeyboardButton("🛒 فروشگاه", callback_data=f"shop:show")
        )
        return markup
    

    def get_back_to_profile_button(self, user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data=f"view:profile:{user_id}")
        )
        
        return markup
    
    def handle_view_section(self, call):
        parts = call.data.split(":")  # مثلا ['view', 'equipment', '123456']
        if len(parts) != 3:
            return  # اگر ساختار اشتباه بود، کاری نکن

        _, section, user_id = parts
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        # حالا بسته به اینکه کاربر چی خواسته، متن رو آماده می‌کنیم
        if section == "profile":
            player = profile_manager.get_player(user_id)
            skills_combat = skill_manager.get_skills(user_id, "combat")
            skills_common = skill_manager.get_skills(user_id, "common")
            skills_special = skill_manager.get_skills(user_id, "special")
            text = profile_manager.format_profile(player, skills_combat, skills_common, skills_special)
            reply_markup = self.get_profile_buttons(user_id)

        elif section == "equipment":
            from managers import equipment_manager
            equipment = equipment_manager.get_equipment(user_id)
            text = "🎒 تجهیزات:\n" + ("\n".join(f"➤ {e}" for e in equipment) if equipment else "⛔ بدون تجهیزات")
            reply_markup = self.get_back_to_profile_button(user_id)

        elif section == "pets":
            text = "🐾 سیستم پت‌ها به‌زودی فعال می‌شود."
            reply_markup = self.get_back_to_profile_button(user_id)

        elif section == "coins":
            player = profile_manager.get_player(user_id)
            coins = player['coins'] if player else 0
            text = f"💰 سکه‌های شما: {coins}"
            reply_markup = self.get_back_to_profile_button(user_id)

        elif section == "shop":
            from plugins.shop import ShopPlugin
            ShopPlugin(self.bot).handle_shop_callback(call)
            return


        else:
            return  # اگر بخش ناشناخته بود، بی‌خیال

        # حالا پیام قبلی رو ویرایش می‌کنیم
        try:
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"❌ Edit error: {e}")

    

    


def register(bot):
    plugin = PlayerPlugin(bot)
    plugin.register()