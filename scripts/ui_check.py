#!/usr/bin/env python3
"""화면이 실제로 동작하는지 짧게 확인한다. 결과는 [OK]/[!!] 몇 줄만 출력한다 (토큰 절약).

사용:
  python3 scripts/ui_check.py http://0.0.0.0:3000/
  python3 scripts/ui_check.py http://0.0.0.0:8000/ --expect "svg" --expect "#result" --text "이상 설비"
  python3 scripts/ui_check.py http://0.0.0.0:8000/ --click "button#run" --wait "#result tr" --count "#result tr"

확인 항목:
  - HTTP 응답 코드, 페이지 제목
  - 콘솔 에러, 페이지 예외, 실패한 요청(4xx/5xx)
  - --expect CSS 선택자가 화면에 있는지, --text 문구가 보이는지
  - --click 후 --wait 선택자가 나타나는지, --count 선택자 개수
  - 기본 요약: svg·table 행·canvas 개수

Playwright(파이썬)와 Chromium이 없으면 HTTP 응답과 HTML 문자열 검사만 한다.
설치: pip install -q playwright && python3 -m playwright install chromium
종료 코드: 문제 없으면 0, 하나라도 [!!]이면 1.
"""
import argparse
import sys
import urllib.request

problems = 0


def ok(msg):
    print(f"  [OK] {msg}")


def ng(msg):
    global problems
    problems += 1
    print(f"  [!!] {msg}")


def fallback(a, reason):
    print(f"(브라우저 없이 HTTP만 확인: {reason})")
    try:
        with urllib.request.urlopen(a.url, timeout=a.timeout / 1000) as r:
            html = r.read().decode("utf-8", "replace")
            ok(f"HTTP {r.status}")
    except Exception as e:  # noqa: BLE001
        ng(f"접속 실패: {e}")
        return
    for t in a.text:
        (ok if t in html else ng)(f"HTML에 문구 '{t}'")
    if a.expect or a.click:
        print("  (선택자·클릭 확인은 브라우저가 필요해 건너뜀. 자바스크립트로 그리는 화면은 HTML에 없을 수 있음)")


def browser(a):
    from playwright.sync_api import sync_playwright

    errors, failed = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1280, "height": 800})
        page.on("console", lambda m: m.type == "error" and errors.append(m.text[:160]))
        page.on("pageerror", lambda e: errors.append(str(e)[:160]))
        page.on("response", lambda r: r.status >= 400 and failed.append(f"{r.status} {r.url[-80:]}"))
        resp = page.goto(a.url, wait_until="networkidle", timeout=a.timeout)
        code = resp.status if resp else 0
        (ok if code and code < 400 else ng)(f"HTTP {code} / 제목 '{page.title()[:60]}'")

        for sel in a.expect:
            n = page.locator(sel).count()
            (ok if n else ng)(f"선택자 {sel}: {n}개")
        for t in a.text:
            vis = page.get_by_text(t, exact=False).count()
            (ok if vis else ng)(f"문구 '{t}' 표시")

        if a.click:
            try:
                page.locator(a.click).first.click(timeout=a.timeout)
                ok(f"클릭 {a.click}")
            except Exception as e:  # noqa: BLE001
                ng(f"클릭 실패 {a.click}: {str(e).splitlines()[0][:120]}")
            if a.wait:
                try:
                    page.wait_for_selector(a.wait, timeout=a.timeout)
                    ok(f"클릭 후 {a.wait} 나타남")
                except Exception:  # noqa: BLE001
                    ng(f"클릭 후 {a.wait} 나타나지 않음 ({a.timeout}ms)")
            page.wait_for_load_state("networkidle")

        for sel in a.count:
            print(f"  [..] {sel}: {page.locator(sel).count()}개")
        summ = page.evaluate(
            "() => ({svg: document.querySelectorAll('svg').length,"
            " rows: document.querySelectorAll('tbody tr').length,"
            " canvas: document.querySelectorAll('canvas').length,"
            " empty: document.body.innerText.trim().length === 0})"
        )
        print(f"  [..] svg {summ['svg']} / 표 행 {summ['rows']} / canvas {summ['canvas']}")
        if summ["empty"]:
            ng("본문 텍스트가 비어 있음 (렌더링 실패 가능)")

        (ok if not errors else ng)(f"콘솔 에러 {len(errors)}개")
        for e in errors[:3]:
            print(f"       - {e}")
        (ok if not failed else ng)(f"실패한 요청 {len(failed)}개")
        for f in failed[:3]:
            print(f"       - {f}")
        if a.shot:
            page.screenshot(path=a.shot, full_page=True)
            print(f"  [..] 스크린샷 {a.shot} (필요할 때만 열어 볼 것)")
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--expect", action="append", default=[], help="있어야 하는 CSS 선택자 (여러 번 가능)")
    ap.add_argument("--text", action="append", default=[], help="보여야 하는 문구 (여러 번 가능)")
    ap.add_argument("--click", help="클릭할 CSS 선택자")
    ap.add_argument("--wait", help="클릭 후 나타나야 하는 CSS 선택자")
    ap.add_argument("--count", action="append", default=[], help="개수만 출력할 CSS 선택자")
    ap.add_argument("--shot", help="스크린샷 저장 경로 (선택)")
    ap.add_argument("--timeout", type=int, default=10000, help="ms")
    a = ap.parse_args()
    print(f"== UI 점검 {a.url}")
    try:
        import playwright  # noqa: F401
    except ImportError:
        fallback(a, "playwright 미설치")
    else:
        try:
            browser(a)
        except Exception as e:  # noqa: BLE001
            msg = str(e).splitlines()[0][:160]
            if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
                fallback(a, "Chromium 미설치")
            else:
                ng(f"브라우저 점검 실패: {msg}")
    print("결과:", "문제 없음" if problems == 0 else f"확인 필요 {problems}건")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
