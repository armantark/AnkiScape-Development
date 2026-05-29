# injectors.py - JS injection and deck browser wiring for AnkiScape
from __future__ import annotations
import os
import datetime
from typing import Optional

try:
    from aqt import mw  # type: ignore
    from aqt import gui_hooks as _hooks  # type: ignore
    HAS_ANKI = True
except Exception:
    mw = None  # type: ignore
    _hooks = None  # type: ignore
    HAS_ANKI = False

# Central debug logger (no cycle; support both package and flat import in tests)
try:
    from .debug import debug_log as _debug_log  # type: ignore
except Exception:
    try:
        from debug import debug_log as _debug_log  # type: ignore
    except Exception:
        def _debug_log(msg: str) -> None:  # fallback no-op
            pass


# --- Pure JS builders (testable) ---

def should_force_pass_through(message: object) -> bool:
    """Return True if a JS bridge message must never be marked handled.

    Pure helper so unit tests can validate the allowlist contract.
    """
    try:
        if not isinstance(message, str):
            return False
        low = message.lower()
    except Exception:
        return False
    # Always allow native navigation and study actions through
    if low.startswith("open:"):
        return True
    if low in ("decks", "add", "browse", "stats", "sync"):
        return True
    if low in ("study", "review", "start"):
        return True
    if low.startswith("study") or low.startswith("review") or low.startswith("start"):
        return True
    # Common actions in Browser/Editor
    if low in ("preview", "previewer", "card-info", "addcards"):
        return True
    return False

def build_reviewer_js(position: str, icon_data_uri: str) -> str:
    pos = position if position in ("left", "right") else "right"
    js = r"""
        (function(){
            try{
                var wrap = document.getElementById('ankiscape-float');
                if (!wrap) {
                    wrap = document.createElement('div');
                    wrap.id = 'ankiscape-float';
                    wrap.style.position = 'fixed';
                    wrap.style.bottom = '16px';
                    // Ensure only the button receives events
                    wrap.style.pointerEvents = 'none';
                    wrap.style.zIndex = '9999';
                    document.body.appendChild(wrap);
                }
                wrap.style.left = '';
                wrap.style.right = '';
                if ('__POS__' === 'left') { wrap.style.left = '16px'; } else { wrap.style.right = '16px'; }

                var btn = document.getElementById('ankiscape-btn');
                if (!btn) {
                    btn = document.createElement('a');
                    btn.id = 'ankiscape-btn';
                }
                btn.href = '#';
                // Re-enable pointer events on the actual button
                btn.style.pointerEvents = 'auto';
                btn.style.padding = '10px';
                btn.style.border = 'none';
                btn.style.borderRadius = '20px';
                btn.style.background = 'transparent';
                btn.style.boxShadow = 'none';
                btn.style.textDecoration = 'none';
                btn.style.outline = 'none';
                btn.style.webkitTapHighlightColor = 'transparent';
                btn.style.cursor = 'pointer';
                btn.style.transition = 'background 150ms ease, box-shadow 150ms ease';
        btn.style.display = 'inline-flex';
        btn.style.alignItems = 'center';
        btn.style.justifyContent = 'center';
        btn.style.lineHeight = '0';
        btn.style.boxSizing = 'border-box';
        btn.style.overflow = 'hidden';
                btn.title = 'AnkiScape';
                var img = btn.querySelector('img');
                if (!img) { btn.textContent = ''; img = document.createElement('img'); btn.appendChild(img); }
                img.alt = 'AnkiScape';
                img.style.width = '24px';
                img.style.height = '24px';
                img.style.display = 'block';
                img.style.filter = 'drop-shadow(0 1px 1px rgba(0,0,0,0.25))';
                img.style.transition = 'transform 150ms ease';
        img.style.transformOrigin = '50% 50%';
        img.style.willChange = 'transform';
                img.src = '__ICON_DATA_URI__';
                if (!btn.dataset.ankiscapeHoverBound) {
                    btn.addEventListener('mouseenter', function(){
            try { img.style.transform = 'scale(1.15)'; img.style.filter = 'none'; } catch(_){}
                        btn.style.background = 'rgba(76, 175, 80, 0.15)';
                        btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
                        try { pycmd('ankiscape_log:hover_enter_reviewer'); } catch(e){}
                    });
                    btn.addEventListener('mouseleave', function(){
            try { img.style.transform = 'scale(1)'; img.style.filter = 'drop-shadow(0 1px 1px rgba(0,0,0,0.25))'; } catch(_){}
                        btn.style.background = 'transparent';
                        btn.style.boxShadow = 'none';
                        try { pycmd('ankiscape_log:hover_leave_reviewer'); } catch(e){}
                    });
                    btn.dataset.ankiscapeHoverBound = '1';
                }
        if (!btn.dataset.ankiscapeBound) {
                    btn.addEventListener('click', function(ev){
                        ev.preventDefault();
            try { pycmd('ankiscape_log:click_reviewer'); } catch(e){}
                        try { pycmd('ankiscape_open_menu'); } catch(e){}
                        return false;
                    });
                    btn.dataset.ankiscapeBound = '1';
                }
                if (btn.parentElement !== wrap) { wrap.appendChild(btn); }
                try { pycmd('ankiscape_log:review_floating_inserted'); } catch(e){}
            } catch(e) { try { pycmd('ankiscape_log:review_js_error'); } catch(_){} }
        })();
    """
    return js.replace("__POS__", pos).replace("__ICON_DATA_URI__", icon_data_uri or '')


def build_overview_js(position: str, icon_data_uri: str) -> str:
    pos = position if position in ("left", "right") else "right"
    js = r"""
        (function(){
            try{
                var wrap = document.getElementById('ankiscape-float');
                if (!wrap) {
                    wrap = document.createElement('div');
                    wrap.id = 'ankiscape-float';
                    wrap.style.position = 'fixed';
                    wrap.style.bottom = '16px';
                    // Ensure only the button receives events
                    wrap.style.pointerEvents = 'none';
                    wrap.style.zIndex = '9999';
                    document.body.appendChild(wrap);
                }
                wrap.style.left = '';
                wrap.style.right = '';
                if ('__POS__' === 'left') { wrap.style.left = '16px'; } else { wrap.style.right = '16px'; }

                var btn = document.getElementById('ankiscape-btn');
                if (!btn) { btn = document.createElement('a'); btn.id = 'ankiscape-btn'; }
                btn.href = '#';
                // Re-enable pointer events on the actual button
                btn.style.pointerEvents = 'auto';
                btn.style.padding = '10px';
                btn.style.border = 'none';
                btn.style.borderRadius = '20px';
                btn.style.background = 'transparent';
                btn.style.boxShadow = 'none';
                btn.style.textDecoration = 'none';
                btn.style.outline = 'none';
                btn.style.webkitTapHighlightColor = 'transparent';
                btn.style.cursor = 'pointer';
                btn.style.transition = 'background 150ms ease, box-shadow 150ms ease';
        btn.style.display = 'inline-flex';
        btn.style.alignItems = 'center';
        btn.style.justifyContent = 'center';
        btn.style.lineHeight = '0';
        btn.style.boxSizing = 'border-box';
        btn.style.overflow = 'hidden';
                btn.title = 'AnkiScape';
                var img = btn.querySelector('img');
                if (!img) { btn.textContent=''; img = document.createElement('img'); btn.appendChild(img); }
                img.alt = 'AnkiScape';
                img.style.width = '24px';
                img.style.height = '24px';
                img.style.display = 'block';
                img.style.filter = 'drop-shadow(0 1px 1px rgba(0,0,0,0.25))';
                img.style.transition = 'transform 150ms ease';
        img.style.transformOrigin = '50% 50%';
        img.style.willChange = 'transform';
                img.src = '__ICON_DATA_URI__';
                if (!btn.dataset.ankiscapeHoverBound) {
                    btn.addEventListener('mouseenter', function(){
            try { img.style.transform = 'scale(1.15)'; img.style.filter = 'none'; } catch(_){}
                        btn.style.background = 'rgba(76, 175, 80, 0.15)';
                        btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
                        try { pycmd('ankiscape_log:hover_enter_overview'); } catch(e){}
                    });
                    btn.addEventListener('mouseleave', function(){
            try { img.style.transform = 'scale(1)'; img.style.filter = 'drop-shadow(0 1px 1px rgba(0,0,0,0.25))'; } catch(_){}
                        btn.style.background = 'transparent';
                        btn.style.boxShadow = 'none';
                        try { pycmd('ankiscape_log:hover_leave_overview'); } catch(e){}
                    });
                    btn.dataset.ankiscapeHoverBound = '1';
                }
        if (!btn.dataset.ankiscapeBound) {
                    btn.addEventListener('click', function(ev){
                        ev.preventDefault();
            try { pycmd('ankiscape_log:click_overview'); } catch(e){}
                        try { pycmd('ankiscape_open_menu'); } catch(e){}
                        return false;
                    });
                    btn.dataset.ankiscapeBound = '1';
                }
                if (btn.parentElement !== wrap) { wrap.appendChild(btn); }
                try { pycmd('ankiscape_log:overview_floating_inserted'); } catch(e){}
            } catch(e) { try { pycmd('ankiscape_log:overview_js_error'); } catch(_){} }
        })();
    """
    return js.replace("__POS__", pos).replace("__ICON_DATA_URI__", icon_data_uri or '')


def build_deck_browser_js(enable_floating: bool, position: str, icon_data_uri: str) -> str:
    pos = position if position in ("left", "right") else "right"
    js = r"""
            (function(){
                try {
            function attachHover(a){
                        try {
                            if (!a || a.dataset.ankiscapeHoverBound) return;
                            var img = a.querySelector('img');
                a.style.display = 'inline-flex';
                a.style.alignItems = 'center';
                a.style.justifyContent = 'center';
                            a.style.cursor = 'pointer';
                            a.style.transition = 'background 150ms ease, box-shadow 150ms ease';
                a.style.lineHeight = '0';
                a.style.boxSizing = 'border-box';
                a.style.overflow = 'hidden';
                            if (img) { img.style.transition = 'transform 150ms ease'; }
                if (img) { img.style.transformOrigin = '50% 50%'; img.style.willChange = 'transform'; }
                            a.addEventListener('mouseenter', function(){
                try { if (img) { img.style.transform = 'scale(1.15)'; img.style.filter = 'none'; } } catch(_){ }
                                a.style.background = 'rgba(76, 175, 80, 0.15)';
                                a.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
                                try { pycmd('ankiscape_log:hover_enter_deckbrowser'); } catch(e){}
                            });
                            a.addEventListener('mouseleave', function(){
                try { if (img) { img.style.transform = 'scale(1)'; img.style.filter = 'drop-shadow(0 1px 1px rgba(0,0,0,0.25))'; } } catch(_){ }
                                a.style.background = 'transparent';
                                a.style.boxShadow = 'none';
                                try { pycmd('ankiscape_log:hover_leave_deckbrowser'); } catch(e){}
                            });
                            a.dataset.ankiscapeHoverBound = '1';
                        } catch(_){}
                    }
                    function makeBtn(){
                        var a = document.createElement('a');
                        a.id = 'ankiscape-btn';
                        a.href = '#';
                        // Ensure this specific button is the only interactive element if wrapped
                        a.style.pointerEvents = 'auto';
                        a.style.marginLeft = '8px';
                        a.style.padding = '6px';
                        a.style.border = 'none';
                        a.style.borderRadius = '8px';
                        a.style.textDecoration = 'none';
                        a.style.background = 'transparent';
            a.style.display = 'inline-flex';
            a.style.alignItems = 'center';
            a.style.justifyContent = 'center';
            a.style.lineHeight = '0';
            a.style.boxSizing = 'border-box';
            a.style.overflow = 'hidden';
                        a.title = 'AnkiScape';
                        var img = document.createElement('img');
                        img.alt = 'AnkiScape';
                        img.style.width = '24px';
                        img.style.height = '24px';
                        img.style.display = 'block';
                        img.style.filter = 'drop-shadow(0 1px 1px rgba(0,0,0,0.25))';
                        img.style.transition = 'transform 150ms ease';
            img.style.transformOrigin = '50% 50%';
            img.style.willChange = 'transform';
                        img.src = '__ICON_DATA_URI__';
                        a.appendChild(img);
                        if (!a.dataset.ankiscapeBound) {
                            a.addEventListener('click', function(ev){
                                ev.preventDefault();
                                try { pycmd('ankiscape_log:click_deckbrowser'); } catch(e){}
                                try { pycmd('ankiscape_open_menu'); } catch(e){}
                                return false;
                            });
                            a.dataset.ankiscapeBound = '1';
                        }
                        attachHover(a);
                        return a;
                    }

                    var elems = Array.from(document.querySelectorAll('a,button'));
                    var actions = elems.filter(function(e){
                        var t = (e.textContent || '').trim();
                        return /(Get Shared|Create Deck|Import)/i.test(t);
                    });
                    if (actions.length) {
                        var last = actions[actions.length - 1];
                        var btn = document.getElementById('ankiscape-btn') || makeBtn();
                        if (!btn.querySelector('img')) {
                            btn.textContent = '';
                            var img1 = document.createElement('img');
                            img1.alt = 'AnkiScape'; img1.style.width='24px'; img1.style.height='24px'; img1.style.display='block'; img1.style.filter='drop-shadow(0 1px 1px rgba(0,0,0,0.25))';
                            img1.style.transition='transform 150ms ease';
                            img1.src='__ICON_DATA_URI__'; btn.appendChild(img1);
                        }
                        attachHover(btn);
                        if (last.parentElement) {
                            if (last.nextSibling) { last.parentElement.insertBefore(btn, last.nextSibling); }
                            else { last.parentElement.appendChild(btn); }
                            try { pycmd('ankiscape_log:after_last_action(' + actions.length + ')'); } catch(e){}
                            return;
                        }
                    }

                    var topAnchors = elems.filter(function(e){
                        var t = (e.textContent || '').trim();
                        return /(Decks|Add|Browse|Stats|Sync)/i.test(t);
                    });
                    if (topAnchors.length) {
                        var rightmost = topAnchors[topAnchors.length - 1];
                        var btn2 = document.getElementById('ankiscape-btn') || makeBtn();
                        if (!btn2.querySelector('img')) {
                            btn2.textContent = '';
                            var img2 = document.createElement('img');
                            img2.alt='AnkiScape'; img2.style.width='24px'; img2.style.height='24px'; img2.style.display='block'; img2.style.filter='drop-shadow(0 1px 1px rgba(0,0,0,0.25))';
                            img2.style.transition='transform 150ms ease';
                            img2.src='__ICON_DATA_URI__'; btn2.appendChild(img2);
                        }
                        attachHover(btn2);
                        if (rightmost.parentElement) {
                            if (rightmost.nextSibling) { rightmost.parentElement.insertBefore(btn2, rightmost.nextSibling); }
                            else { rightmost.parentElement.appendChild(btn2); }
                            try { pycmd('ankiscape_log:inserted_topnav(' + topAnchors.length + ')'); } catch(e){}
                            return;
                        }
                    }

                    var footer = document.querySelector('.links') || document.querySelector('#links') || null;
                    if (footer) {
                        var btn3 = document.getElementById('ankiscape-btn') || makeBtn();
                        if (!btn3.querySelector('img')) {
                            btn3.textContent = '';
                            var img3 = document.createElement('img');
                            img3.alt='AnkiScape'; img3.style.width='24px'; img3.style.height='24px'; img3.style.display='block'; img3.style.filter='drop-shadow(0 1px 1px rgba(0,0,0,0.25))';
                            img3.style.transition='transform 150ms ease';
                            img3.src='__ICON_DATA_URI__'; btn3.appendChild(img3);
                        }
                        attachHover(btn3);
                        footer.appendChild(btn3);
                        try { pycmd('ankiscape_log:inserted_selector'); } catch(e){}
                        return;
                    }

                    if (__ENABLE_FLOATING__) {
                        var wrap = document.getElementById('ankiscape-float');
                        if (!wrap) {
                            wrap = document.createElement('div');
                            wrap.id = 'ankiscape-float';
                            wrap.style.position = 'fixed';
                            wrap.style.bottom = '16px';
                            // Ensure only the button receives events
                            wrap.style.pointerEvents = 'none';
                            wrap.style.zIndex = '9999';
                            document.body.appendChild(wrap);
                        }
                        wrap.style.left = '';
                        wrap.style.right = '';
                        if ('__POS__' === 'left') { wrap.style.left = '16px'; } else { wrap.style.right = '16px'; }
                        var btn = document.getElementById('ankiscape-btn');
                        if (!btn) { btn = makeBtn(); }
                        if (!btn.querySelector('img')) {
                            btn.textContent = '';
                            var img4 = document.createElement('img');
                            img4.alt='AnkiScape'; img4.style.width='24px'; img4.style.height='24px'; img4.style.display='block'; img4.style.filter='drop-shadow(0 1px 1px rgba(0,0,0,0.25))';
                            img4.style.transition='transform 150ms ease';
                            img4.src='__ICON_DATA_URI__'; btn.appendChild(img4);
                        }
                        attachHover(btn);
                        if (btn.parentElement !== wrap) { wrap.appendChild(btn); } else if (!document.getElementById('ankiscape-btn')) { wrap.appendChild(btn); }
                        try { pycmd('ankiscape_log:inserted_floating'); } catch(e){}
                    }
                } catch (e) {
                    try { pycmd('ankiscape_log:js_error'); } catch(_){ }
                }
            })();
    """
    js = js.replace("__ENABLE_FLOATING__", "true" if enable_floating else "false")
    js = js.replace("__POS__", pos)
    js = js.replace("__ICON_DATA_URI__", icon_data_uri or '')
    return js


# --- Runtime functions ---

def inject_reviewer_floating_button(_=None) -> None:
    if not HAS_ANKI:
        return
    try:
        enabled = True
        pos = "right"
        try:
            enabled = bool(mw.col.get_config("ankiscape_floating_enabled", True))
            pos = mw.col.get_config("ankiscape_floating_position", "right")
            if pos not in ("left", "right"):
                pos = "right"
        except Exception:
            pass
        if not enabled:
            js_remove = r"""
            (function(){ var el = document.getElementById('ankiscape-float'); if (el && el.parentElement){ el.parentElement.removeChild(el);} })();
            """
            mw.reviewer.web.eval(js_remove)
            _debug_log("inject_reviewer_floating_button: disabled; removed")
            return
        try:
            from .deck_injection_pure import _get_icon_data_uri  # type: ignore
            icon_uri = _get_icon_data_uri() or ''
        except Exception:
            icon_uri = ''
        js = build_reviewer_js(pos, icon_uri)
        _debug_log("inject_reviewer_floating_button: eval")
        mw.reviewer.web.eval(js)
    except Exception:
        _debug_log("inject_reviewer_floating_button: failed")


def inject_overview_floating_button(overview=None, content=None) -> None:
    if not HAS_ANKI:
        return
    try:
        web = None
        try:
            web = overview.web
        except Exception:
            web = getattr(getattr(mw, 'overview', None), 'web', None)
        if not web:
            _debug_log("inject_overview_floating_button: no web")
            return
        enabled = True
        pos = "right"
        try:
            enabled = bool(mw.col.get_config("ankiscape_floating_enabled", True))
            pos = mw.col.get_config("ankiscape_floating_position", "right")
            if pos not in ("left", "right"):
                pos = "right"
        except Exception:
            pass
        if not enabled:
            js_remove = r"""
            (function(){ var el = document.getElementById('ankiscape-float'); if (el && el.parentElement){ el.parentElement.removeChild(el);} })();
            """
            web.eval(js_remove)
            _debug_log("inject_overview_floating_button: disabled; removed")
            return
        try:
            from .deck_injection_pure import _get_icon_data_uri  # type: ignore
            icon_uri = _get_icon_data_uri() or ''
        except Exception:
            icon_uri = ''
        js = build_overview_js(pos, icon_uri)
        _debug_log("inject_overview_floating_button: eval")
        web.eval(js)
    except Exception:
        _debug_log("inject_overview_floating_button: failed")


def register_deck_browser_button() -> None:
    if not HAS_ANKI:
        return
    try:
        from .deck_injection_pure import DeckBrowserContent as _DBC, inject_into_deck_browser_content  # type: ignore
    except Exception:
        return

    def _add_button(deck_browser, content):  # type: ignore[no-redef]
        _debug_log("_add_button: called")
        try:
            db_content = _DBC(
                links=getattr(content, "links", None),
                stats=getattr(content, "stats", None),
                tree=getattr(content, "tree", None),
            )
            before_links, before_stats, before_tree = db_content.links, db_content.stats, db_content.tree
            db_content = inject_into_deck_browser_content(db_content)
            if db_content.links != before_links:
                if hasattr(content, "links"):
                    content.links = db_content.links
                _debug_log("_add_button: injected into links")
            elif db_content.stats != before_stats or db_content.tree != before_tree:
                _debug_log("_add_button: no injection (stats/tree avoided)")
            else:
                _debug_log("_add_button: already present; no injection")
        except Exception as e:
            _debug_log(f"_add_button: error {e}")

    def _on_js_message(handled, message, context):  # type: ignore[no-redef]
        _debug_log(f"_on_js_message: {message}")
        try:
            if isinstance(message, str):
                if message == "ankiscape_open_menu":
                    # Handle directly here to avoid relying on separate registration order.
                    try:
                        from .ui import is_main_menu_open, focus_main_menu_if_open  # type: ignore
                        if is_main_menu_open():
                            _debug_log("injectors.bridge: menu open; focusing")
                            try:
                                focus_main_menu_if_open()
                            except Exception:
                                pass
                        else:
                            # Resolve the package module reliably and call its _on_main_menu on the UI thread.
                            _debug_log("injectors.bridge: opening via package._on_main_menu")
                            try:
                                import sys
                                from aqt.qt import QTimer  # type: ignore
                            except Exception:
                                QTimer = None  # type: ignore

                            pkg = None
                            try:
                                pkg = sys.modules.get(__package__)
                            except Exception:
                                pkg = None
                            if pkg is None:
                                _debug_log("injectors.bridge: package module not found in sys.modules")
                            else:
                                open_cb = getattr(pkg, "_on_main_menu", None)
                                if callable(open_cb):
                                    def _do_open():
                                        try:
                                            open_cb()  # type: ignore[misc]
                                        except Exception as e:
                                            _debug_log(f"injectors.bridge: _on_main_menu raised: {e}")

                                    try:
                                        if QTimer is not None:
                                            QTimer.singleShot(0, _do_open)
                                            _debug_log("injectors.bridge: scheduled _on_main_menu with QTimer")
                                        else:
                                            _do_open()
                                            _debug_log("injectors.bridge: called _on_main_menu directly (no QTimer)")
                                    except Exception as e:
                                        _debug_log(f"injectors.bridge: failed to dispatch open: {e}")
                                else:
                                    _debug_log("injectors.bridge: _on_main_menu not found on package module")
                        # We handled this custom message; signal handled
                        return (True, message)
                    except Exception as e:
                        _debug_log(f"injectors.bridge: error handling open_menu: {e}")
                        return (handled, message)
                if message.startswith("ankiscape_log:"):
                    _debug_log(f"js: {message[len('ankiscape_log:'):]}")
                    # Not handled; allow default processing to continue
                    return (handled, message)
                # Hardening: ensure native navigation/study messages pass through unhandled
                if should_force_pass_through(message):
                    return (False, message)
        except Exception as e:
            _debug_log(f"injectors.bridge: handler exception: {e}")
        # Default: do not intercept messages we don't recognize
        try:
            if isinstance(message, str):
                return (False, message)
        except Exception:
            pass
        return (handled, message)

    def _did_render(deck_browser):  # type: ignore[no-redef]
        try:
            try:
                from .ui import hide_review_hud  # lazy import to avoid cycles
                hide_review_hud()
            except Exception:
                pass
            enable_floating = True
            float_pos = 'right'
            try:
                enable_floating = bool(mw.col.get_config('ankiscape_floating_enabled', True))
                p = mw.col.get_config('ankiscape_floating_position', 'right')
                float_pos = p if p in ('left','right') else 'right'
            except Exception:
                pass
            try:
                from .deck_injection_pure import _get_icon_data_uri  # type: ignore
                _icon_uri = _get_icon_data_uri() or ''
            except Exception:
                _icon_uri = ''
            js = build_deck_browser_js(enable_floating, float_pos, _icon_uri)
            deck_browser.web.eval(js)
            _debug_log("_did_render: eval injected fallback button if absent")
        except Exception:
            _debug_log("_did_render: eval failed")

    try:
        try:
            _hooks.deck_browser_will_render_content.remove(_add_button)
        except Exception:
            pass
        _hooks.deck_browser_will_render_content.append(_add_button)
        _debug_log("registered: deck_browser_will_render_content")
    except Exception as e:
        _debug_log(f"register failed: deck_browser_will_render_content: {e}")
    try:
        try:
            _hooks.deck_browser_did_render.remove(_did_render)
        except Exception:
            pass
        _hooks.deck_browser_did_render.append(_did_render)
        _debug_log("registered: deck_browser_did_render")
    except Exception as e:
        _debug_log(f"register failed: deck_browser_did_render: {e}")
    try:
        try:
            _hooks.webview_did_receive_js_message.remove(_on_js_message)
        except Exception:
            pass
        _hooks.webview_did_receive_js_message.append(_on_js_message)
        _debug_log("registered: webview_did_receive_js_message")
    except Exception as e:
        _debug_log(f"register failed: webview_did_receive_js_message: {e}")


def force_deck_browser_refresh() -> None:
    if not HAS_ANKI:
        return
    try:
        db = getattr(mw, "deckBrowser", None)
        if db is None:
            _debug_log("force_refresh: no deckBrowser present")
            return
        if hasattr(db, "refresh"):
            _debug_log("force_refresh: calling deckBrowser.refresh()")
            db.refresh()
        elif hasattr(db, "renderPage"):
            _debug_log("force_refresh: calling deckBrowser.renderPage()")
            db.renderPage()
    except Exception:
        _debug_log("force_refresh: failed to refresh")
        pass
