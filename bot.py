import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH WEB SERVER (ĐỂ CHẠY 24/24) =================
app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run():
    # Chạy trên port 8080 để tương thích tốt với Render/Replit
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= CẤU HÌNH BOT =================
API_TOKEN = '7833444319:AAHdrEdMtqM88zLpUlnyX7bWqoT8GVNnKm4'  # Token Bot
bot = telebot.TeleBot(API_TOKEN)

nhapma_token = "0975f449-c48b-46a0-bff0-c5cda2250fc7"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzgiR_3qqjjzv4QObfLjKjiAITk8Dlwyzbyv0S-aRJoeZVCQqnUGx_zegmx_0TzgP2Hzg/exec"
ADMIN_PASS = "admin_vip_proledinhkiet"

# ================= CÁC HÀM XỬ LÝ (GIỮ NGUYÊN) =================
def generate_ldk_key():
    prefix = "LDKNCH"
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
    return f"{prefix}{random_part}"

def add_key_to_server(key):
    try:
        params = {"type": "create", "pass": ADMIN_PASS, "key": key, "role": "VIP", "max_device": 1}
        requests.get(WEB_APP_URL, params=params, timeout=5)
        return True
    except:
        return False

def upload_to_notems(content_text):
    try:
        path_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        url = f"https://note.ms/{path_name}"
        payload = {"t": content_text}
        headers = {"User-Agent": "Mozilla/5.0"}
        requests.post(url, data=payload, headers=headers, timeout=5)
        return url
    except:
        return None

def shorten_with_nhapma(long_url):
    try:
        api_url = f"https://service.nhapma.com/api?token={nhapma_token}&url={long_url}"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl")
        return long_url
    except:
        return long_url

# ================= XỬ LÝ TIN NHẮN TRONG NHÓM =================

# Hàm kiểm tra xem tin nhắn có chứa từ khóa muốn bắt không
def check_keywords(message):
    if message.text is None: return False
    text = message.text.lower() # Chuyển về chữ thường để so sánh
    
    # Danh sách các từ khóa sẽ kích hoạt Bot
    keywords = ["key", "getkey", "lấy key", "xin key", "mua key", "bot ơi"]
    
    # Nếu tin nhắn chứa 1 trong các từ trên -> True
    for kw in keywords:
        if kw in text:
            return True
    return False

# Bắt tin nhắn dựa trên từ khóa (Không cần dấu /)
@bot.message_handler(func=check_keywords)
def handle_group_chat(message):
    # Trả lời lại đúng tin nhắn của người hỏi (Reply)
    msg = bot.reply_to(message, "⏳ <b>Đang khởi tạo Key VIP cho bạn...</b>", parse_mode="HTML")
    
    try:
        # 1. Tạo Key
        key = generate_ldk_key()
        
        # 2. Thêm vào Server
        if add_key_to_server(key):
            # 3. Up lên Note.ms
            content = f"KEY CỦA BẠN LÀ:\n\n{key}\n\nKey VIP Free Fire PC - Hạn 24h."
            link_goc = upload_to_notems(content)
            
            if link_goc:
                # 4. Chồng Link 3 tầng
                link_level_1 = shorten_with_nhapma(link_goc)
                input_lv2 = link_level_1 if link_level_1 else link_goc
                link_level_2 = shorten_with_nhapma(input_lv2)
                input_lv3 = link_level_2 if link_level_2 else input_lv2
                final_link = shorten_with_nhapma(input_lv3)
                
                # Tạo nút bấm
                markup = InlineKeyboardMarkup()
                btn_link = InlineKeyboardButton("👉 BẤM VÀO ĐÂY ĐỂ LẤY KEY 👈", url=final_link)
                markup.add(btn_link)

                response_text = (
                    f"✅ <b>ĐÃ TẠO KEY THÀNH CÔNG!</b>\n"
                    f"Chào {message.from_user.first_name}, link của bạn đây:\n\n"
                    f"⚠️ <i>Lưu ý: Link có quảng cáo để duy trì server.</i>"
                )
                
                bot.edit_message_text(
                    chat_id=message.chat.id, 
                    message_id=msg.message_id, 
                    text=response_text, 
                    parse_mode="HTML", 
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi tạo Note.")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi kết nối Server.")
            
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"❌ Lỗi: {str(e)}")

# Vẫn giữ lệnh /start cho ai chat riêng
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào bạn! Hãy gõ 'key' hoặc 'getkey' để lấy Key nhé.")

# ================= CHẠY BOT =================
if __name__ == '__main__':
    keep_alive()  # <--- Bắt đầu chạy Web Server ảo
    print("Bot đang chạy...")
    bot.infinity_polling() # <--- Bắt đầu chạy Bot Telegram
