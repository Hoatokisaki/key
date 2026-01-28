import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
import uuid
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH SERVER TỰ LƯU TRỮ (SELF-HOST) =================
app = Flask('')

# --- KHO CHỨA KEY (Lưu trong RAM) ---
# Dạng: {'id_ngau_nhien': 'nội dung key'}
key_database = {} 

# Địa chỉ Render của bạn (Lấy từ ảnh bạn gửi)
MY_DOMAIN = "https://key-klud.onrender.com"

@app.route('/')
def home():
    return "I am alive"

# --- TRANG WEB HIỂN THỊ KEY ---
@app.route('/view/<key_id>')
def view_key_page(key_id):
    # Tìm key trong kho
    content = key_database.get(key_id)
    
    if content:
        # Giao diện hiển thị Key đẹp mắt
        return f"""
        <html>
        <head>
            <title>Nhận Key VIP</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ background-color: #121212; color: white; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .card {{ background: #1e1e1e; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); text-align: center; max-width: 90%; width: 400px; }}
                h2 {{ color: #00ff88; margin-top: 0; }}
                .key-box {{ background: #333; padding: 15px; margin: 20px 0; border-radius: 8px; border: 1px dashed #555; font-family: monospace; font-size: 18px; word-break: break-all; color: #ffeb3b; }}
                p {{ color: #aaa; font-size: 14px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>✅ LẤY KEY THÀNH CÔNG</h2>
                <p>Sao chép đoạn mã dưới đây:</p>
                <div class="key-box">{content}</div>
                <p>Key có hạn sử dụng 24h.</p>
                <div class="footer">Powered by Snowie Panel</div>
            </div>
        </body>
        </html>
        """
    else:
        return "<h1>❌ Key không tồn tại hoặc bot đã khởi động lại.</h1>"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= CẤU HÌNH BOT =================
API_TOKEN = '7833444319:AAHdrEdMtqM88zLpUlnyX7bWqoT8GVNnKm4'
bot = telebot.TeleBot(API_TOKEN)

nhapma_token = "0975f449-c48b-46a0-bff0-c5cda2250fc7"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzgiR_3qqjjzv4QObfLjKjiAITk8Dlwyzbyv0S-aRJoeZVCQqnUGx_zegmx_0TzgP2Hzg/exec"
ADMIN_PASS = "admin_vip_proledinhkiet"

# ================= CÁC HÀM XỬ LÝ =================
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

# --- HÀM MỚI: TỰ TẠO LINK TRÊN SERVER CỦA MÌNH ---
def create_self_hosted_link(key_content):
    try:
        # 1. Tạo ID ngẫu nhiên cho link
        link_id = str(uuid.uuid4())[:8] # Lấy 8 ký tự đầu cho ngắn
        
        # 2. Lưu nội dung vào RAM
        key_database[link_id] = key_content
        
        # 3. Trả về link của chính mình
        return f"{MY_DOMAIN}/view/{link_id}"
    except Exception as e:
        print(f"Lỗi tạo link nội bộ: {e}")
        return None
# -----------------------------------------------

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

# ================= XỬ LÝ TIN NHẮN =================

def check_keywords(message):
    if message.text is None: return False
    text = message.text.lower()
    keywords = ["key", "getkey", "lấy key", "xin key", "mua key", "bot ơi"]
    for kw in keywords:
        if kw in text:
            return True
    return False

@bot.message_handler(func=check_keywords)
def handle_group_chat(message):
    msg = bot.reply_to(message, "⏳ <b>Đang khởi tạo Key VIP cho bạn...</b>", parse_mode="HTML")
    
    try:
        key = generate_ldk_key()
        
        if add_key_to_server(key):
            # --- DÙNG PHƯƠNG PHÁP TỰ LƯU TRỮ ---
            # Link này sẽ là: https://key-klud.onrender.com/view/xxxx
            link_goc = create_self_hosted_link(key)
            
            if link_goc:
                # Rút gọn link
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
                # --- ĐÃ XÓA PHẦN HIỆN KEY THẲNG ---
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi hệ thống: Không thể tạo link. Vui lòng thử lại sau.")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi kết nối Google Sheet.")
            
    except Exception as e:
        print(f"Lỗi: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi Bot. Vui lòng báo Admin.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào bạn! Hãy gõ 'key' hoặc 'getkey' để lấy Key nhé.")

# ================= CHẠY BOT =================
if __name__ == '__main__':
    keep_alive()
    print("Bot đang chạy...")
    bot.infinity_polling()
