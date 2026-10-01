import os
import base64
from datetime import datetime, timedelta
from flask import Flask, Response, request, render_template_string

app = Flask(__name__)

# ================= НАСТРОЙКИ =================
TARGET_VLESS = "vless://f3478441-7d7b-4ad3-9482-47b02a369ad3@195.72.61.72:443?encryption=none&type=xhttp&path=%2Froach_path%2F&mode=auto&security=tls&sni=meet.m64a.ru&fp=chrome&alpn=h3#%F0%9F%87%B8%F0%9F%87%AA%20Sweden%2C%20Stockholm"
LIMIT_GB = 100.0
LIMIT_DAYS = 30
# =============================================

TRAFFIC_FILE = "traffic_usage.txt"
START_DATE_FILE = "start_date.txt"

def get_used_traffic():
    if os.path.exists(TRAFFIC_FILE):
        with open(TRAFFIC_FILE, "r") as f:
            try: return float(f.read().strip())
            except: return 0.0
    return 0.0

def get_start_date():
    if os.path.exists(START_DATE_FILE):
        with open(START_DATE_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    now = datetime.now()
    with open(START_DATE_FILE, "w") as f:
        f.write(now.isoformat())
    return now

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAPP CORE // MONITOR</title>
    <style>
        @import url('https://googleapis.com');
        body { background-color: #050508; color: #c3c7db; font-family: 'Rajdhani', sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-image: radial-gradient(circle at 50% 50%, #141026 0%, #050508 100%); }
        .cyber-container { background: rgba(13, 12, 22, 0.85); padding: 35px; border-radius: 12px; box-shadow: 0 0 40px rgba(138, 92, 255, 0.15); width: 100%; max-width: 460px; text-align: center; border: 1px solid #2f2654; position: relative; backdrop-filter: blur(10px); }
        .cyber-container::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, #ff0055, #8a5cff, #00f0ff); border-radius: 12px 12px 0 0; }
        h1 { font-family: 'Orbitron', sans-serif; font-size: 26px; font-weight: 900; letter-spacing: 2px; margin-bottom: 5px; color: #fff; text-shadow: 0 0 10px rgba(138,92,255,0.6); }
        .subtitle { font-size: 13px; color: #61627a; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 25px; }
        .status-badge { display: inline-block; padding: 6px 16px; border-radius: 4px; font-size: 13px; font-weight: 700; font-family: 'Orbitron', sans-serif; margin-bottom: 25px; letter-spacing: 1px; }
        .active { background: rgba(0, 240, 255, 0.1); color: #00f0ff; border: 1px solid rgba(0,240,255,0.3); box-shadow: 0 0 15px rgba(0,240,255,0.1); }
        .expired { background: rgba(255, 0, 85, 0.1); color: #ff0055; border: 1px solid rgba(255,0,85,0.3); }
        .panel-grid { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .panel-box { background: #0b0a12; padding: 15px; border-radius: 6px; width: 44%; border: 1px solid #1c1a2e; text-align: left; position: relative; }
        .val-num { font-family: 'Orbitron', sans-serif; font-size: 24px; font-weight: 700; color: #fff; margin-top: 5px; }
        .lbl-txt { font-size: 12px; color: #8284a1; text-transform: uppercase; letter-spacing: 1px; }
        .bar-wrapper { background: #11101a; border-radius: 4px; height: 12px; width: 100%; overflow: hidden; margin-bottom: 8px; border: 1px solid #1f1d33; }
        .bar-fill { background: linear-gradient(90deg, #8a5cff 0%, #00f0ff 100%); height: 100%; width: {{ percent_used }}%; box-shadow: 0 0 10px rgba(0,240,255,0.4); }
        .time-box { background: #0b0a12; padding: 15px; border-radius: 6px; border: 1px solid #1c1a2e; margin-top: 20px; display: flex; justify-content: space-between; align-items: center; text-align: left; }
        .link-section { background: #07060a; padding: 15px; border-radius: 6px; border: 1px solid #151322; margin-top: 25px; text-align: left; }
        .link-lbl { font-size: 11px; color: #51536b; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; letter-spacing: 1px; }
        code { font-family: 'Orbitron', sans-serif; font-size: 11px; color: #00f0ff; display: block; word-break: break-all; background: #020204; padding: 10px; border-radius: 4px; border: 1px solid #12111c; }
    </style>
</head>
<body>
    <div class="cyber-container">
        <h1>HAPP NODE HUB</h1>
        <div class="subtitle">Traffic Shaper Systems</div>
        {% if is_active %}
        <div class="status-badge active">SYSTEM ONLINE</div>
        {% else %}
        <div class="status-badge expired">LIMIT EXCEEDED</div>
        {% endif %}
        <div class="panel-grid">
            <div class="panel-box">
                <div class="lbl-txt">Использовано</div>
                <div class="val-num" style="color: #00f0ff;">{{ "%.2f"|format(used) }}</div>
                <div class="lbl-txt" style="font-size:10px; text-align:right; margin-top:2px;">GIGABYTES</div>
            </div>
            <div class="panel-box">
                <div class="lbl-txt">Общий лимит</div>
                <div class="val-num">{{ limit_gb }}</div>
                <div class="lbl-txt" style="font-size:10px; text-align:right; margin-top:2px;">GIGABYTES</div>
            </div>
        </div>
        <div class="bar-wrapper"><div class="bar-fill"></div></div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #61627a; font-family:'Orbitron';">
            <span>LEFT: {{ "%.2f"|format(rem_gb) }} GB</span>
            <span>{{ "%.1f"|format(percent_used) }}% USED</span>
        </div>
        <div class="time-box">
            <div>
                <div class="lbl-txt">Осталось времени</div>
                <div class="val-num" style="color: #8a5cff; font-size: 22px;">{{ days_left }} Дней</div>
            </div>
            <div style="text-align: right;">
                <div class="lbl-txt" style="font-size:10px;">ДАТА ОТКЛЮЧЕНИЯ</div>
                <div style="font-size: 13px; color:#fff; font-family:'Orbitron'; margin-top:5px;">{{ end_date }}</div>
            </div>
        </div>
        <div class="link-section">
            <div class="link-lbl">🌐 Ссылка на подписку для друга в Happ:</div>
            <code>https://{{ host }}/sub</code>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def dashboard():
    used = get_used_traffic()
    start_date = get_start_date()
    end_date = start_date + timedelta(days=LIMIT_DAYS)
    days_left = (end_date - datetime.now()).days
    if days_left < 0: days_left = 0
    rem_gb = LIMIT_GB - used
    if rem_gb < 0: rem_gb = 0
    percent_used = (used / LIMIT_GB) * 100
    if percent_used > 100: percent_used = 100
    is_active = (used < LIMIT_GB) and (datetime.now() < end_date)
    return render_template_string(HTML_TEMPLATE, used=used, limit_gb=LIMIT_GB, rem_gb=rem_gb, percent_used=percent_used, days_left=days_left, end_date=end_date.strftime("%d.%m.%Y"), is_active=is_active, host=request.host)

@app.route("/sub")
def sub_endpoint():
    used = get_used_traffic()
    start_date = get_start_date()
    if (used >= LIMIT_GB) or (datetime.now() > start_date + timedelta(days=LIMIT_DAYS)):
        return Response(base64.b64encode(b"").decode('utf-8'), mimetype="text/plain")
    raw_sub_data = TARGET_VLESS.encode('utf-8')
    base64_sub = base64.b64encode(raw_sub_data).decode('utf-8')
    return Response(base64_sub, mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 14886))
    app.run(host="0.0.0.0", port=port)
