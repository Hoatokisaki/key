import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import string
import time
from flask import Flask
from threading import Thread

# ================= CẤU HÌNH WEB SERVER =================
app = Flask('')

@app.route('/')
def home():
    return "I am alive"

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

# --- HÀM MỚI: DÙNG LITTERBOX (CỰC KỲ ỔN ĐỊNH) ---
def upload_to_litterbox(content_text):
    # Cách hoạt động: Tạo 1 file txt ảo và up lên server chứa file
    try:
        url = "https://litterbox.catbox.moe/resources/internals/api.php"
        # reqtype: fileupload, time: 12h (tồn tại 12 tiếng)
        data = {'reqtype': 'fileupload', 'time': '12h'} 
        # Tạo file ảo tên là key_vip.txt
        files = {'fileToUpload': ('key_vip.txt', content_text)}
        
        response = requests.post(url, data=data, files=files, timeout=15)
        
        # Kiểm tra kỹ xem kết quả có phải là Link không (bắt buộc phải có http)
        if response.status_code == 200 and response.text.startswith("http"):
            return response.text.strip()
            
    except Exception as e:
        print(f"Litterbox lỗi: {e}")

    # BACKUP: Nếu Litterbox lỗi, trả về None để xử lý sau (tránh crash bot)
    return None
# -----------------------------------------------

def shorten_with_nhapma(long_url):
    # Nếu không có link (None) hoặc link lỗi thì trả về None
    if not long_url or not long_url.startswith("http"):
        return None
        
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
            content = f"KEY CỦA BẠN LÀ:\n\n{key}\n\nKey VIP Free Fire PC - Hạn 12h."
            
            # 1. Upload lên Litterbox
            link_goc = upload_to_litterbox(content)
            
            # 2. Kiểm tra nếu có link thì mới rút gọn
            if link_goc:
                link_level_1 = shorten_with_nhapma(link_goc)
                input_lv2 = link_level_1 if link_level_1 else link_goc
                link_level_2 = shorten_with_nhapma(input_lv2)
                input_lv3 = link_level_2 if link_level_2 else input_lv2
                final_link = shorten_with_nhapma(input_lv3)
                
                # Nếu rút gọn lỗi, dùng link gốc
                if not final_link: final_link = link_goc

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
                # TRƯỜNG HỢP KHẨN CẤP: Nếu không up được link nào, gửi luôn Key cho khách đỡ chửi
                bot.edit_message_text(
                    chat_id=message.chat.id, 
                    message_id=msg.message_id, 
                    text=f"❌ Lỗi Server Link. Key tạm thời của bạn là: <code>{key}</code>",
                    parse_mode="HTML"
                )
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi kết nối Google Sheet.")
            
    except Exception as e:
        # In lỗi ra console server để mình biết đường sửa
        print(f"Lỗi Bot: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ Lỗi hệ thống, vui lòng thử lại sau.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào bạn! Hãy gõ 'key' hoặc 'getkey' để lấy Key nhé.")

# ================= CHẠY BOT =================
if __name__ == '__main__':
    keep_alive()
    print("Bot đang chạy...")
    bot.infinity_polling()
