# test_openalex.py - 测试 OpenAlex API 正确的 URL 格式
import urllib.request, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 方式1：用 doi 过滤
urls_to_test = [
    # 用 arxiv 过滤器
    "https://api.openalex.org/works?filter=locations.source.host_organization_lineage:I19714098,title.search:LLaMA&select=id,cited_by_count,ids&per-page=1&mailto=test@test.com",
    # 用 primary_location.source.id 过滤
    "https://api.openalex.org/works?filter=ids.arxiv:https://arxiv.org/abs/2303.08774v2&select=id,cited_by_count&per-page=1&mailto=test@test.com",
    # 最简单：直接搜索 arxiv ID
    "https://api.openalex.org/works/https://doi.org/10.48550/arxiv.2303.08774?select=id,cited_by_count&mailto=test@test.com",
]

for url in urls_to_test:
    print(f"\nTesting: {url[:80]}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "test/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read())
            print(f"  OK: {json.dumps(data)[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
