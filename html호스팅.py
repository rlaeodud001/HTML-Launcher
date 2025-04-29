# All right reserved daeyoung_ceo
from flask import Flask, send_from_directory, request, abort
import requests
import os
from datetime import datetime

app = Flask(__name__)

STATIC_DIR = 'static_files'
DISCORD_WEBHOOK_URL = '웹훅_URL'  # 수정 
BLOCKED_IPS = ['1.2.3.4', '5.6.7.8']  # 차단할 IP 목록

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    print(f"'{STATIC_DIR}' 폴더가 없어서 새로 만들었습니다.")

def lookup_ip(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        if response.status_code == 200:
            data = response.json()
            country = data.get('country', 'Unknown')
            city = data.get('city', 'Unknown')
            return country, city
    except Exception as e:
        print(f"IP 조회 실패: {e}")
    return 'Unknown', 'Unknown'

def send_discord_webhook(ip, path):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    country, city = lookup_ip(ip)

    content = (
        f"접속 알림\n"
        f"- IP: {ip}\n"
        f"- 위치: {country}, {city}\n"
        f"- 경로: {path}\n"
        f"- 시간: {now}"
    )
    data = {
        "content": content
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Discord Webhook 전송 실패: {e}")

def is_blocked(ip):
    return ip in BLOCKED_IPS

@app.before_request
def block_ips():
    ip = request.remote_addr
    if is_blocked(ip):
        abort(403)

@app.route('/')
def index():
    ip = request.remote_addr
    send_discord_webhook(ip, '/')

    index_file = os.path.join(STATIC_DIR, 'index.html')

    if os.path.isfile(index_file):
        return send_from_directory(STATIC_DIR, 'index.html')
    else:
        try:
            files = [f for f in os.listdir(STATIC_DIR) if f.endswith('.html')]
        except FileNotFoundError:
            files = []

        if not files:
            return '''
            <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                    </style>
                </head>
                <body>
                    <h1>📂 HTML 파일이 없습니다.</h1>
                    <p>static_files 폴더에 파일을 추가해주세요.</p>
                    <p>index.html 파일을 추가해주세요.</p>
                    <p>All right reserved daeyoung_ceo</p>
                </body>
            </html>
            '''

        file_list = ''.join(
            f'''
            <div class="card">
                <a href="/{file}">{file}</a>
            </div>
            ''' for file in files
        )

        return f'''
        <html>
        <head>
            <title>파일 리스트</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    text-align: center;
                    padding-top: 50px;
                }}
                .container {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 20px;
                    padding: 20px;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    width: 200px;
                    transition: 0.3s;
                }}
                .card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                }}
                a {{
                    text-decoration: none;
                    color: #333;
                    font-weight: bold;
                    font-size: 18px;
                }}
            </style>
        </head>
        <body>
            <h1>📄 HTML 파일 목록</h1>

            <div class="container">
                {file_list}
            </div>
            <p>All right reserved daeyoung_ceo</p>
        </body>
        </html>
        '''

@app.route('/<path:filepath>')
def serve_file(filepath):
    full_path = os.path.join(STATIC_DIR, filepath)

    if not os.path.isfile(full_path):
        abort(404)

    ip = request.remote_addr
    send_discord_webhook(ip, filepath)

    if filepath.endswith('.html'):
        return send_from_directory(STATIC_DIR, filepath)

    referer = request.headers.get('Referer')
    if referer and request.host in referer:
        return send_from_directory(STATIC_DIR, filepath)

    abort(403)

# 에러 핸들러 (디자인 적용)
@app.errorhandler(404)
def page_not_found(e):
    return '''
    <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding-top: 100px; background: #ffecec; }
                h1 { font-size: 50px; color: #ff4d4d; }
                p { font-size: 20px; }
                a { text-decoration: none; color: #007bff; }
            </style>
        </head>
        <body>
            <h1>404</h1>
            <p>요청하신 파일을 찾을 수 없습니다.</p>
            <a href="/">홈으로 돌아가기</a>
            <p>All right reserved daeyoung_ceo</p>
        </body>
    </html>
    ''', 404

@app.errorhandler(403)
def forbidden(e):
    return '''
    <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding-top: 100px; background: #fff3cd; }
                h1 { font-size: 50px; color: #ffc107; }
                p { font-size: 20px; }
                a { text-decoration: none; color: #007bff; }
            </style>
        </head>
        <body>
            <h1>403</h1>
            <p>접근이 차단되었습니다.</p>
            <a href="/">홈으로 돌아가기</a>
            <p>All right reserved daeyoung_ceo</p>
        </body>
    </html>
    ''', 403

@app.errorhandler(500)
def internal_error(e):
    return '''
    <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding-top: 100px; background: #f8d7da; }
                h1 { font-size: 50px; color: #dc3545; }
                p { font-size: 20px; }
                a { text-decoration: none; color: #007bff; }
            </style>
        </head>
        <body>
            <h1>500</h1>
            <p>서버 내부 오류가 발생했습니다.</p>
            <a href="/">홈으로 돌아가기</a>
            <p>All right reserved daeyoung_ceo</p>
        </body>
    </html>
    ''', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)