from dataclasses import dataclass
import re

@dataclass
class LinkInfo:
    provider: str
    url: str

TERABOX_RE = re.compile(r"https?://(?:www\.)?(?:1024terabox|terabox|teraboxapp)\.[^/\s]+/\S+", re.I)
NOTY_RE = re.compile(r"https?://(?:www\.)?notydrive\.com/\S+", re.I)

def detect_link(text):
    for rx, name in ((TERABOX_RE, "terabox"), (NOTY_RE, "notydrive")):
        m = rx.search(text or "")
        if m:
            return LinkInfo(name, m.group(0).rstrip(").,]"))
    return None

async def fetch_permitted_download(url, provider):
    # Implement only through an official/permitted API or direct-download mechanism.
    # Do not bypass CAPTCHA, DRM, authentication or anti-bot protections.
    raise NotImplementedError(f"No permitted {provider} adapter configured.")
