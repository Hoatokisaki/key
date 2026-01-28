import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
import base64  # <--- Thư viện để mã hóa Key vào Link
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH SERVER =================
app = Flask('')

# Địa chỉ Render của bạn
MY_DOMAIN = "https://key-klud.onrender.com"

@app.route('/')
def home():
    return "I am alive"

# --- TRANG WEB HIỂN THỊ KEY (GIẢI MÃ TỪ LINK) ---
@app.route('/view/<encoded_data>')
def view_key_page(encoded_data):
    try:
        # 1. Giải mã: Lấy chuỗi từ Link -> Dịch ngược ra Key gốc
        decoded_bytes = base64.urlsafe_b64decode(encoded_data)
        real_key = decoded_bytes.decode('utf-8')
        
        # 2. Nếu giải mã thành công, hiện giao diện đẹp
        return f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nhận Key VIP</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{ --primary: #00ff88; --bg: #0a0a0a; --card: #1a1a1a; }}
                body {{ font-family: 'Poppins', sans-serif; background-color: var(--bg); color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
                .card {{ background: var(--card); padding: 40px; border-radius: 20px; text-align: center; max-width: 90%; width: 420px; border: 1px solid #333; box-shadow: 0 0 20px rgba(0,255,136,0.2); }}
                h2 {{ color: var(--primary); margin-top: 0; }}
                .key-box {{ background: rgba(255,255,255,0.1); padding: 20px; border: 2px dashed var(--primary); color: var(--primary); font-family: monospace; font-size: 22px; margin: 20px 0; word-break: break-all; cursor: pointer; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>🎉 LẤY KEY THÀNH CÔNG!</h2>
                <p style="color: #aaa;">Key của bạn là:</p>
                <div class="key-box" onclick="navigator.clipboard.writeText(this.innerText); alert('Đã sao chép!')">{real_key}</div>
                <p style="font-size: 14px; color: #888;">(Chạm vào key để sao chép)</p>
                <div class="footer">Powered by Snowie Panel</div>
            </div>
        </body>
        </html>
        """
    except:
        # Nếu link bị lỗi hoặc người dùng sửa bậy link
        return "<h1>❌ Link không hợp lệ hoặc bị lỗi.</h1>"

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

# --- HÀM TẠO LINK "BẤT TỬ" (KHÔNG DÙNG DATABASE) ---
def create_stateless_link(key_content):
    try:
        # 1. Mã hóa Key thành Base64 (để giấu vào link)
        # Ví dụ: LDK123 -> TERLMTIz
        encoded_bytes = base64.urlsafe_b64encode(key_content.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        
        # 2. Tạo link chứa mã này
        return f"{MY_DOMAIN}/view/{encoded_str}"
    except Exception as e:
        print(f"Lỗi mã hóa: {e}")
        return None
# ---------------------------------------------------

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
        if kw in text: return True
    return False

@bot.message_handler(func=check_keywords)
def handle_group_chat(message):
    msg = bot.reply_to(message, "⏳ <b>Đang khởi tạo Key VIP cho bạn...</b>", parse_mode="HTML")
    
    try:
        key = generate_ldk_key()
        
        if add_key_to_server(key):
            # --- DÙNG HÀM MỚI ---
            link_goc = create_stateless_link(key)
            
            if link_goc:
                link_level_1 = shorten_with_nhapma(link_goc)
                input_lv2 = link_level_1 if link_level_1 else link_goc
                link_level_2 = shorten_with_nhapma(input_lv2)
                input_lv3 = link_level_2 if link_level_2 else input_lv2
                final_link = shorten_with_nhapma(input_lv3)
                
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
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi tạo link.")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi kết nối Server.")
            
    except Exception as e:
        print(f"Lỗi: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi hệ thống.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào bạn! Hãy gõ 'key' hoặc 'getkey' để lấy Key nhé.")

if __name__ == '__main__':
    keep_alive()
    print("Bot đang chạy...")
    bot.infinity_polling()
