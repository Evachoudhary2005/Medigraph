import urllib.request
pid = "4d47bedd-7f8f-46fe-88c0-c7d4bd638ffb"
url = f"http://127.0.0.1:8000/api/v1/summary/{pid}/pdf"
with urllib.request.urlopen(url, timeout=30) as r:
    data = r.read()
    print("status:", r.status)
    print("content-type:", r.headers.get("Content-Type"))
    print("content-length:", len(data), "bytes")
    print("first 8 bytes:", data[:8])
    with open("test_summary.pdf", "wb") as f:
        f.write(data)
    print("saved test_summary.pdf")
