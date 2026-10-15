"""Element / image recognition.

The teammate's `random_explore_webpage()` clicks RANDOM screen coordinates.
That is the biggest weakness: it is not human (people click things they can
see), it can hit ads / nav / the close button / trigger downloads, and it
produces junk telemetry. This module finds REAL clickable targets and returns
their center points, which you feed into cursor.human_move_and_click(x, y).

Three strategies, best first. Each returns a list of Target(name, cx, cy, kind)
or a single (cx, cy). Use whichever is available on the VM:

  1. UI Automation (uiautomation)  -> finds real hyperlinks/buttons in Chrome
     via the accessibility tree. Most reliable; gives true element rects.
  2. Template matching (OpenCV via pyautogui.locateCenterOnScreen) -> for a
     button you have a screenshot of (e.g. a specific "Accept"/"Next").
  3. OCR (pytesseract) -> find clickable-looking text when 1 and 2 don't apply.

Install on the VM as needed:
    py -m pip install uiautomation            # strategy 1
    py -m pip install opencv-python           # strategy 2 (pyautogui confidence=)
    py -m pip install pytesseract             # strategy 3 (+ Tesseract OCR exe)

For Chrome's a11y tree to be populated, launch Chrome with
    chrome.exe --force-renderer-accessibility
(or it turns on automatically once a UIA client queries it). The teammate's
Win-search launch is fine for the parent process; just add that flag, or let
the first query enable it.
"""
from __future__ import annotations

import random
from collections import namedtuple

Target = namedtuple("Target", "name cx cy kind")
_rng = random.Random()


# =========================================================================
# Strategy 1: UI Automation — find real links / buttons in the browser
# =========================================================================
def find_browser_elements(max_items: int = 80, kinds=("Hyperlink", "Button")):
    """Return visible clickable Targets from the foreground Chrome window.

    Uses the accessibility tree, so these are the page's actual links/buttons
    with their real on-screen rectangles — no guessing at coordinates.
    """
    try:
        import uiautomation as auto  # type: ignore
    except Exception:
        return []

    results = []
    try:
        # Foreground Chrome top-level window.
        win = auto.GetForegroundControl()
        # climb to the Chrome_WidgetWin top window if needed
        top = win
        for _ in range(6):
            if top and "Chrome_WidgetWin" in (top.ClassName or ""):
                break
            top = top.GetParentControl() if top else None
        root = top or win
        if root is None:
            return []

        wanted = set(kinds)

        # Walk the subtree breadth-first, bounded, collecting link/button nodes.
        queue = [(root, 0)]
        seen = 0
        while queue and len(results) < max_items and seen < 4000:
            node, depth = queue.pop(0)
            seen += 1
            if depth > 25:
                continue
            try:
                ctype = node.ControlTypeName or ""   # e.g. 'HyperlinkControl'
                for w in wanted:
                    if w in ctype:
                        r = node.BoundingRectangle
                        if r and r.width() > 4 and r.height() > 4:
                            cx = (r.left + r.right) // 2
                            cy = (r.top + r.bottom) // 2
                            name = (node.Name or "").strip()[:60]
                            results.append(Target(name, cx, cy, w.lower()))
                        break
                for child in node.GetChildren():
                    queue.append((child, depth + 1))
            except Exception:
                continue
    except Exception:
        return results
    return results


def pick_visible_link(viewport=None):
    """Pick one real hyperlink inside the viewport, biased to the content area.

    viewport: optional (left, top, right, bottom) to keep clicks away from the
    browser chrome (tabs/address bar) and the very bottom. If None, uses the
    middle 60% of the screen height.
    """
    try:
        import pyautogui  # type: ignore
        sw, sh = pyautogui.size()
    except Exception:
        sw = sh = 1000
    if viewport is None:
        viewport = (int(sw * 0.05), int(sh * 0.18), int(sw * 0.95), int(sh * 0.90))
    l, t, r, b = viewport

    links = [e for e in find_browser_elements(kinds=("Hyperlink",))
             if l <= e.cx <= r and t <= e.cy <= b and e.name]
    if not links:
        return None
    # prefer links with real text; a little randomness so it's not always #1
    links.sort(key=lambda e: (-len(e.name)))
    top_slice = links[: max(3, len(links) // 3)]
    return _rng.choice(top_slice)


# =========================================================================
# Strategy 2: template matching (needs opencv-python for confidence=)
# =========================================================================
def find_image(template_path: str, confidence: float = 0.8):
    """Return (cx, cy) of a UI element matching a template screenshot, else None."""
    try:
        import pyautogui  # type: ignore
        box = pyautogui.locateCenterOnScreen(template_path, confidence=confidence)
        if box:
            return int(box.x), int(box.y)
    except Exception:
        return None
    return None


# =========================================================================
# Strategy 3: OCR — find clickable-looking text
# =========================================================================
def find_text(substring: str, region=None):
    """Return (cx, cy) of on-screen text containing `substring` (case-insensitive)."""
    try:
        import pyautogui  # type: ignore
        import pytesseract  # type: ignore
        from PIL import Image  # noqa: F401  (pyautogui.screenshot returns PIL)
    except Exception:
        return None
    try:
        shot = pyautogui.screenshot(region=region)
        data = pytesseract.image_to_data(shot, output_type=pytesseract.Output.DICT)
        sub = substring.lower()
        for i, word in enumerate(data["text"]):
            if word and sub in word.lower():
                x = data["left"][i] + data["width"][i] // 2
                y = data["top"][i] + data["height"][i] // 2
                if region:
                    x += region[0]
                    y += region[1]
                return int(x), int(y)
    except Exception:
        return None
    return None


# =========================================================================
# Convenience: a smart replacement for `random_explore_webpage`'s blind click
# =========================================================================
def smart_click_link(move_and_click):
    """Find a real link and click it with the given cursor function.

    Returns True if a real element was clicked, False if none was found (so the
    caller can decide to fall back to the old random behaviour or just scroll).

    `move_and_click` is cursor.human_move_and_click (passed in to avoid a hard
    dependency / circular import).
    """
    target = pick_visible_link()
    if target is None:
        return False
    move_and_click(target.cx, target.cy)
    return True
