# Global message to user mapping
msg_user_map = {}

def link_message_to_user(message_id, user_id):
    msg_user_map[str(message_id)] = str(user_id)

def get_user_by_message(message_id):
    return msg_user_map.get(str(message_id))