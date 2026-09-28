"""Run the shipped injections in Qt's real DOM without an Anki profile."""

import importlib.util
import json
import unittest

HAS_AQT = importlib.util.find_spec("aqt") is not None
if HAS_AQT:
    from aqt.qt import QApplication, QEvent, QEventLoop, QTimer, QWebEngineView
    from PyQt6.QtTest import QSignalSpy

ICON = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aWQAAAABJRU5ErkJggg=="


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class DomTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["ankiscape-js-dom-tests"])

    def setUp(self):
        self.view = QWebEngineView()
        self.view.resize(640, 480)
        self.addCleanup(self.close_page)
        self.view.show()
        self.load_body("")

    def close_page(self):
        self.view.close()
        self.view.deleteLater()
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def load_body(self, body):
        loaded = QSignalSpy(self.view.loadFinished)
        self.view.setHtml(
            "<!doctype html><html><body>" + body
            + "<script>window.commands = []; window.pycmd = command => commands.push(command);</script>"
            + "</body></html>"
        )
        self.assertTrue(loaded.wait(5000), "DOM fixture did not load")
        self.assertTrue(loaded[0][0], "DOM fixture load failed")

    def js(self, source):
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        results = []

        def finished(value):
            results.append(value)
            loop.quit()

        wrapped = (
            "(() => { try { return JSON.stringify({value: eval("
            + json.dumps(source)
            + ")}); } catch (error) { return JSON.stringify({error: String(error)}); } })()"
        )
        timer.start(5000)
        self.view.page().runJavaScript(wrapped, finished)
        if not results:
            loop.exec()
        timer.stop()
        self.assertTrue(results, "JavaScript callback timed out")
        result = json.loads(results[0])
        self.assertNotIn("error", result, result)
        return result.get("value")

    def assert_menu_click(self):
        self.assertEqual(self.js("document.querySelectorAll('#ankiscape-btn').length"), 1)
        result = self.js("""
            (() => {
                commands.length = 0;
                const click = new MouseEvent('click', {bubbles: true, cancelable: true});
                document.getElementById('ankiscape-btn').dispatchEvent(click);
                return {prevented: click.defaultPrevented,
                        opened: commands.filter(command => command === 'ankiscape_open_menu')};
            })()
        """)
        self.assertEqual(result, {"prevented": True, "opened": ["ankiscape_open_menu"]})

    def assert_pointer_and_hover(self, source):
        self.load_body('<button id="study" style="position:fixed;inset:0">Study</button>')
        self.js(source)
        self.js(source)
        self.assertEqual(self.js("document.querySelectorAll('#ankiscape-float').length"), 1)
        result = self.js("""
            (() => {
                const wrap = document.getElementById('ankiscape-float');
                const btn = document.getElementById('ankiscape-btn');
                wrap.style.padding = '20px';
                const outer = wrap.getBoundingClientRect();
                const inner = btn.getBoundingClientRect();
                const gap = document.elementFromPoint(outer.left + 1, outer.top + 1);
                const target = document.elementFromPoint(inner.left + inner.width / 2,
                                                         inner.top + inner.height / 2);
                return [getComputedStyle(wrap).pointerEvents, getComputedStyle(btn).pointerEvents,
                        gap.id, target.closest('a').id];
            })()
        """)
        self.assertEqual(result, ["none", "auto", "study", "ankiscape-btn"])
        self.assert_menu_click()
        states = self.js("""
            (() => {
                const btn = document.getElementById('ankiscape-btn');
                const img = btn.querySelector('img');
                // Transitions affect timing, not the event handlers under test.
                btn.style.transition = img.style.transition = 'none';
                const snapshot = () => ({background: getComputedStyle(btn).backgroundColor,
                    shadow: getComputedStyle(btn).boxShadow, filter: getComputedStyle(img).filter,
                    scale: new DOMMatrix(getComputedStyle(img).transform).a});
                const before = snapshot();
                btn.dispatchEvent(new MouseEvent('mouseenter'));
                const entered = snapshot();
                btn.dispatchEvent(new MouseEvent('mouseleave'));
                return [before, entered, snapshot()];
            })()
        """)
        before, entered, left = states
        self.assertNotEqual(entered["background"], before["background"])
        self.assertNotEqual(entered["shadow"], before["shadow"])
        self.assertNotEqual(entered["filter"], before["filter"])
        self.assertGreater(entered["scale"], before["scale"])
        self.assertEqual(left, before)
