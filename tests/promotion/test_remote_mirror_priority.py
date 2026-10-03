import fcntl
import selectors
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCK_WORKER = """\
import fcntl, io, sys, threading
from pathlib import Path
from tools import run_remote_tests as runner
from tools.promotion import lane_execution as gate

role, path, bound = sys.argv[1:]
runner.LOCAL_MIRROR_LOCK_PATH = Path(path)
gate.REMOTE_MIRROR_LOCK_TIMEOUT = float(bound)
real_flock, real_lockf = fcntl.flock, fcntl.lockf
report_lock = threading.Lock()
mirror_worker = None
worker_started = threading.Event()

def report(message):
    with report_lock:
        print(message, flush=True)

def flock(descriptor, operation):
    global mirror_worker
    try:
        if operation == fcntl.LOCK_EX and role in ('gate', 'queue-gate', 'timeout-gate'):
            mirror_worker = threading.current_thread()
        if operation == fcntl.LOCK_EX and role in ('queue-gate', 'timeout-gate', 'old-runner'):
            report('queued-mirror')
        if operation == fcntl.LOCK_EX and role in ('gate', 'queue-gate', 'timeout-gate'):
            report('worker-started')
            worker_started.set()
        result = real_flock(descriptor, operation)
        if operation == fcntl.LOCK_EX and role in ('queue-gate', 'timeout-gate'):
            report('mirror-held')
        return result
    except BlockingIOError:
        report('waiting-mirror')
        raise

def lockf(descriptor, operation):
    try:
        return real_lockf(descriptor, operation)
    except BlockingIOError:
        if role == 'runner':
            report('waiting-turnstile')
        raise

fcntl.flock, fcntl.lockf = flock, lockf
if role in ('gate', 'queue-gate', 'timeout-gate'):
    if role == 'timeout-gate':
        now = 0.0
        gate.time.monotonic = lambda: now
    def poll(seconds):
        report('poll')
        command = sys.stdin.readline().strip()
        if command == 'expire' and role == 'timeout-gate':
            global now
            now = float(bound)
        elif command != 'retry':
            raise RuntimeError('gate retry was not authorized by the test')
        else:
            if not worker_started.wait(timeout=30):
                raise RuntimeError('gate worker did not start')
            mirror_worker.join(timeout=30)
            if mirror_worker.is_alive():
                raise RuntimeError('gate worker did not finish after releasing the mirror')
    gate.time.sleep = poll
    with gate._hold_remote_mirror(io.StringIO(), lambda: report('heartbeat')) as descriptor:
        report('acquired' if descriptor is not None else 'timed-out')
        sys.stdin.readline()
elif role == 'old-runner':
    with Path(path).open('a+') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        report('acquired')
        sys.stdin.readline()
else:
    with runner._hold_mirror_lock():
        report('acquired')
        sys.stdin.readline()
"""


class RemoteMirrorPriorityTest(unittest.TestCase):
    def start_worker(self, role, lock_path, bound=60):
        process = subprocess.Popen(
            (sys.executable, "-u", "-c", LOCK_WORKER, role, str(lock_path), str(bound)),
            cwd=PROJECT_ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, bufsize=0,
        )
        self.addCleanup(self.stop_worker, process)
        return process

    @staticmethod
    def stop_worker(process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=30)

    def read_event(self, process):
        with selectors.DefaultSelector() as ready:
            ready.register(process.stdout, selectors.EVENT_READ)
            self.assertTrue(ready.select(timeout=30), "lock worker did not report progress")
        message = process.stdout.readline().decode().strip()
        self.assertTrue(message, f"lock worker exited with {process.poll()}")
        return message

    @staticmethod
    def send(process, command):
        process.stdin.write((command + "\n").encode())
        process.stdin.flush()

    def test_gate_bound_also_covers_a_busy_turnstile(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "mirror.lock"
            with lock_path.with_suffix(".turnstile").open("a+") as admission:
                fcntl.lockf(admission.fileno(), fcntl.LOCK_EX)
                gate = self.start_worker("gate", lock_path, bound=0)
                self.assertEqual(self.read_event(gate), "timed-out")
                self.send(gate, "release")
                self.assertEqual(gate.wait(timeout=30), 0)

    def test_waiting_gate_stops_new_runners_at_the_turnstile(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "mirror.lock"
            with lock_path.open("a+") as current_runner:
                fcntl.flock(current_runner.fileno(), fcntl.LOCK_EX)
                gate = self.start_worker("gate", lock_path)
                self.waiting_gate(gate)
                runners = [self.start_worker("runner", lock_path) for _ in range(3)]
                for runner in runners:
                    self.assertEqual(self.read_event(runner), "waiting-turnstile")
                    with selectors.DefaultSelector() as ready:
                        ready.register(runner.stderr, selectors.EVENT_READ)
                        self.assertTrue(ready.select(timeout=30), "runner gave no turnstile notice")
                    notice = runner.stderr.readline().decode().strip()
                    self.assertIn("Remote mirror busy; waiting", notice)
                    self.assertIn(str(lock_path.with_suffix(".turnstile")), notice)
                fcntl.flock(current_runner.fileno(), fcntl.LOCK_UN)
                self.send(gate, "retry")
                self.assertEqual(self.read_event(gate), "acquired")

                self.send(gate, "release")
                self.assertEqual(gate.wait(timeout=30), 0)
                with selectors.DefaultSelector() as ready:
                    for runner in runners:
                        ready.register(runner.stdout, selectors.EVENT_READ, runner)
                    while ready.get_map():
                        events = ready.select(timeout=30)
                        self.assertTrue(events, "runner remained blocked after the gate finished")
                        for key, _ in events:
                            runner = key.data
                            message = runner.stdout.readline().decode().strip()
                            if message == "waiting-mirror":
                                continue
                            self.assertEqual(message, "acquired")
                            ready.unregister(runner.stdout)
                            self.send(runner, "release")
                            self.assertEqual(runner.wait(timeout=30), 0)

    def waiting_gate(self, gate):
        events = []
        while not {"poll", "worker-started"}.issubset(events):
            events.append(self.read_event(gate))
        self.assertIn("waiting-mirror", events)
        self.assertIn("heartbeat", events)
        return events

    def finish_runners(self, runners):
        with selectors.DefaultSelector() as ready:
            for runner in runners:
                if runner.poll() is None:
                    ready.register(runner.stdout, selectors.EVENT_READ, runner)
            while ready.get_map():
                readable = ready.select(timeout=30)
                self.assertTrue(readable, "runner remained blocked after the gate finished")
                for key, _ in readable:
                    runner = key.data
                    self.assertEqual(self.read_event(runner), "acquired")
                    ready.unregister(runner.stdout)
                    self.send(runner, "release")
                    self.assertEqual(runner.wait(timeout=30), 0)

    def test_old_runners_cannot_starve_a_waiting_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "mirror.lock"
            with lock_path.open("a+") as current_runner:
                fcntl.flock(current_runner.fileno(), fcntl.LOCK_EX)
                gate = self.start_worker("queue-gate", lock_path)
                events = self.waiting_gate(gate)
                runners = [self.start_worker("old-runner", lock_path) for _ in range(6)]
                for runner in runners:
                    self.assertEqual(self.read_event(runner), "queued-mirror")
                fcntl.flock(current_runner.fileno(), fcntl.LOCK_UN)

                holds_before_gate = 0
                with selectors.DefaultSelector() as ready:
                    ready.register(gate.stdout, selectors.EVENT_READ, gate)
                    for runner in runners:
                        ready.register(runner.stdout, selectors.EVENT_READ, runner)
                    while "mirror-held" not in events:
                        readable = ready.select(timeout=30)
                        self.assertTrue(readable, "no queued process acquired the mirror")
                        for key, _ in readable:
                            process = key.data
                            event = self.read_event(process)
                            if process is gate:
                                events.append(event)
                            else:
                                self.assertEqual(event, "acquired")
                                holds_before_gate += 1
                                # macOS handoff is assumed to serve the blocked gate within
                                # three of these six holds. The pipe marks the flock call
                                # boundary, not kernel enqueue order, which has no portable
                                # observer; this bound is a host scheduling assumption.
                                self.assertLessEqual(
                                    holds_before_gate, 3,
                                    "old runners starved the waiting gate beyond three holds",
                                )
                                ready.unregister(process.stdout)
                                self.send(process, "release")
                                self.assertEqual(process.wait(timeout=30), 0)
                self.send(gate, "retry")
                while True:
                    event = self.read_event(gate)
                    if event == "acquired":
                        break
                    if event == "poll":
                        self.send(gate, "retry")
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(current_runner.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.send(gate, "release")
                self.assertEqual(gate.wait(timeout=30), 0)
                self.finish_runners(runners)

    def test_timed_out_gate_releases_a_late_kernel_acquisition(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "mirror.lock"
            with lock_path.open("a+") as current_runner:
                fcntl.flock(current_runner.fileno(), fcntl.LOCK_EX)
                gate = self.start_worker("timeout-gate", lock_path, bound=3600)
                events = self.waiting_gate(gate)
                self.send(gate, "expire")
                while True:
                    event = self.read_event(gate)
                    events.append(event)
                    if event == "timed-out":
                        break
                self.assertIn("queued-mirror", events)
                fcntl.flock(current_runner.fileno(), fcntl.LOCK_UN)
                self.assertEqual(self.read_event(gate), "mirror-held")
                runner = self.start_worker("old-runner", lock_path)
                self.assertEqual(self.read_event(runner), "queued-mirror")
                self.assertEqual(self.read_event(runner), "acquired")
                self.send(runner, "release")
                self.assertEqual(runner.wait(timeout=30), 0)
                # Keep the gate process alive: process exit must not mask a leaked lock.
                self.assertIsNone(gate.poll())
                fcntl.flock(current_runner.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                with lock_path.with_suffix(".turnstile").open("a+") as admission:
                    fcntl.lockf(admission.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.send(gate, "release")
                self.assertEqual(gate.wait(timeout=30), 0)


if __name__ == "__main__":
    unittest.main()
