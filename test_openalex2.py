# test_openalex2.py - 用正确 DOI 格式测试 OpenAlex
import urllib.request, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "test/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        return json.loads(resp.read())

# arXiv DOI 格式：10.48550/arXiv.2303.08774
# OpenAlex 用 filter=doi: 查询
test_cases = [
    # 方式A：DOI 路径（arXiv 论文有固定 DOI）
    "https://api.openalex.org/works/doi:10.48550/arXiv.2303.08774?select=id,cited_by_count&mailto=test@example.com",
    # 方式B：直接 OpenAlex ID by DOI filter
    "https://api.openalex.org/works?filter=doi:10.48550%2FarXiv.2303.08774&select=id,cited_by_count&mailto=test@example.com",
]

for url in test_cases:
    print(f"\nURL: {url[:90]}...")
    try:
        data = get(url)
        print(f"  cited_by_count: {data.get('cited_by_count', data.get('results', [{}])[0].get('cited_by_count', 'N/A'))}")
    except Exception as e:
        print(f"  Error: {e}")
