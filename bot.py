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
key_database = {}

# Địa chỉ Render của bạn
MY_DOMAIN = "https://key-klud.onrender.com"

@app.route('/')
def home():
    return "I am alive"

# --- TRANG WEB HIỂN THỊ KEY (GIAO DIỆN MỚI ĐẸP HƠN) ---
@app.route('/view/<key_id>')
def view_key_page(key_id):
    content = key_database.get(key_id)
    if content:
        # HTML & CSS đã được nâng cấp
        return f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nhận Key VIP</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary-color: #00ff88;
                    --secondary-color: #00b8ff;
                    --bg-color: #0a0a0a;
                    --card-bg: #1a1a1a;
                    --text-color: #e0e0e0;
                }}
                body {{
                    font-family: 'Poppins', sans-serif;
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background-image: radial-gradient(circle at top right, rgba(0, 255, 136, 0.1), transparent),
                                      radial-gradient(circle at bottom left, rgba(0, 184, 255, 0.1), transparent);
                }}
                .container {{
                    perspective: 1000px;
                }}
                .card {{
                    background: var(--card-bg);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 15px 35px rgba(0,0,0,0.5), 0 0 20px rgba(0, 255, 136, 0.2);
                    text-align: center;
                    max-width: 90%;
                    width: 420px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    transform-style: preserve-3d;
                    animation: cardEntrance 0.8s ease-out;
                }}
                @keyframes cardEntrance {{
                    from {{ opacity: 0; transform: translateY(50px) rotateX(-10deg); }}
                    to {{ opacity: 1; transform: translateY(0) rotateX(0); }}
                }}
                h2 {{
                    font-weight: 700;
                    margin-top: 0;
                    background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 28px;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    color: #aaa;
                    font-size: 15px;
                    margin-bottom: 25px;
                }}
                .key-container {{
                    position: relative;
                    margin: 30px 0;
                }}
                .key-box {{
                    background: rgba(255, 255, 255, 0.05);
                    padding: 20px;
                    border-radius: 12px;
                    border: 2px dashed var(--primary-color);
                    font-family: 'Courier New', monospace;
                    font-size: 22px;
                    font-weight: 600;
                    color: var(--primary-color);
                    word-break: break-all;
                    letter-spacing: 2px;
                    text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .key-box:hover {{
                    background: rgba(0, 255, 136, 0.1);
                    transform: scale(1.02);
                }}
                .copy-hint {{
                    position: absolute;
                    bottom: -25px;
                    left: 50%;
                    transform: translateX(-50%);
                    font-size: 12px;
                    color: var(--secondary-color);
                    opacity: 0.8;
                }}
                .info-text {{
                    color: #888;
                    font-size: 14px;
                    margin-top: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }}
                .footer {{
                    margin-top: 35px;
                    font-size: 13px;
                    color: #666;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    padding-top: 15px;
                }}
                /* Hiệu ứng khi click để copy */
                .copied {{
                    animation: pulse 0.5s;
                    border-color: var(--secondary-color) !important;
                    color: var(--secondary-color) !important;
                }}
                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                    100% {{ transform: scale(1); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h2>🎉 LẤY KEY THÀNH CÔNG!</h2>
                    <p class="subtitle">Cảm ơn bạn đã vượt qua quảng cáo.</p>
                    
                    <div class="key-container">
                        <div class="key-box" id="keyContent" onclick="copyKey()">{content}</div>
                        <div class="copy-hint" id="copyHint">(Chạm để sao chép)</div>
                    </div>
                    
                    <div class="info-text">
                        ⏳ Key có hạn sử dụng 24 giờ.
                    </div>
                    
                    <div class="footer">
                        Developed with ❤️ by Snowie Panel
                    </div>
                </div>
            </div>

            <script>
                function copyKey() {{
                    const keyText = document.getElementById('keyContent').innerText;
                    navigator.clipboard.writeText(keyText).then(() => {{
                        const keyBox = document.getElementById('keyContent');
                        const copyHint = document.getElementById('copyHint');
                        
                        keyBox.classList.add('copied');
                        copyHint.innerText = "✅ Đã sao chép!";
                        copyHint.style.color = "#00ff88";
                        
                        setTimeout(() => {{
                            keyBox.classList.remove('copied');
                            copyHint.innerText = "(Chạm để sao chép)";
                            copyHint.style.color = "#00b8ff";
                        }}, 2000);
                    }}).catch(err => {{
                        console.error('Không thể sao chép: ', err);
                    }});
                }}
            </script>
        </body>
        </html>
        """
    else:
        # Giao diện lỗi cũng được làm đẹp
        return """
        <html>
        <head>
            <title>Lỗi</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet">
            <style>
                body { background-color: #0a0a0a; color: #ff4757; font-family: 'Poppins', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
                h1 { font-size: 24px; }
                p { color: #aaa; margin-top: 10px; }
            </style>
        </head>
        <body>
            <div>
                <h1>❌ 404 - KEY KHÔNG TỒN TẠI</h1>
                <p>Có thể link đã hết hạn hoặc bot đã khởi động lại.</p>
            </div>
        </body>
        </html>
        """

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
        link_id = str(uuid.uuid4())[:8]
        key_database[link_id] = key_content
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
            link_goc = create_self_hosted_link(key)
            
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
