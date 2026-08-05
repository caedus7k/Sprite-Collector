import urllib.request

url = "https://caedus7k.github.io/spritecollector/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        print("STATUS:" + str(r.getcode()))
        body = r.read(800).decode("utf-8", "ignore")
        print("BODY_PREVIEW:\n" + body)
except Exception as e:
    print("ERROR:" + repr(e))
    import traceback

    traceback.print_exc()

    # Target URL (use the repository Pages URL)
    url = "https://caedus7k.github.io/Sprite-Collector/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print("STATUS:" + str(r.getcode()))
            body = r.read(800).decode("utf-8", "ignore")
            print("BODY_PREVIEW:\n" + body)
    except Exception as e:
        print("ERROR:" + repr(e))
        traceback.print_exc()
