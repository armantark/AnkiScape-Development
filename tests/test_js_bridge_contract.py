import os
import io
import importlib

from injectors import build_reviewer_js, build_overview_js, build_deck_browser_js


def test_injected_js_contains_open_menu_command():
    icon = "data:image/png;base64,xxx"
    for js in (
        build_reviewer_js("left", icon),
        build_overview_js("right", icon),
        build_deck_browser_js(True, "right", icon),
    ):
        assert "ankiscape_open_menu" in js


def test_python_side_has_js_message_handler_present():
    # Contract: we must have a webview js message hook that mentions ankiscape_open_menu
    here = os.path.dirname(__file__)
    root = os.path.abspath(os.path.join(here, os.pardir))
    init_path = os.path.join(root, "__init__.py")
    with io.open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "webview_did_receive_js_message" in content
    assert "ankiscape_open_menu" in content
