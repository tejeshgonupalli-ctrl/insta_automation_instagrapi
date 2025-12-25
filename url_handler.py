def detect_url_type(url):
    if "/reel/" in url:
        return "reel"
    if "/p/" in url:
        return "post"
    return "unknown"
