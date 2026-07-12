"""Tests for AtomicParsley temp-file path helpers and interrupt cleanup."""

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

# Ensure package root is importable when running as `python3 -m unittest`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ap_wrapper.main import (  # noqa: E402
    atomicparsley_temp_pattern,
    find_atomicparsley_temps,
    remove_atomicparsley_temps,
    run_atomicparsley,
)


class TestAtomicParsleyTempPattern(unittest.TestCase):
    """atomicparsley_temp_pattern naming conventions."""

    def test_simple_mp4(self) -> None:
        pattern = atomicparsley_temp_pattern("/media/show.mp4")
        self.assertEqual(pattern, "/media/show-temp-*.mp4")

    def test_episode_style_name(self) -> None:
        pattern = atomicparsley_temp_pattern(
            "/data/go_for_it_nakamura-s01e05.mp4"
        )
        self.assertEqual(
            pattern, "/data/go_for_it_nakamura-s01e05-temp-*.mp4"
        )

    def test_m4v_extension(self) -> None:
        pattern = atomicparsley_temp_pattern("ep.m4v")
        self.assertTrue(pattern.endswith("ep-temp-*.m4v"))

    def test_relative_resolves_directory(self) -> None:
        pattern = atomicparsley_temp_pattern("clip.mp4")
        self.assertTrue(os.path.isabs(pattern))
        self.assertTrue(pattern.endswith("clip-temp-*.mp4"))


class TestRemoveAtomicParsleyTemps(unittest.TestCase):
    """remove_atomicparsley_temps filesystem behavior."""

    def test_removes_existing_temps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            media = os.path.join(tmp, "video.mp4")
            with open(media, "wb") as fh:
                fh.write(b"x")
            # AtomicParsley uses a random integer, not PID.
            temps = [
                os.path.join(tmp, "video-temp-42.mp4"),
                os.path.join(tmp, "video-temp-99887.mp4"),
            ]
            for path in temps:
                with open(path, "wb") as fh:
                    fh.write(b"leftover")
            # Unrelated file must not be removed.
            other = os.path.join(tmp, "other-temp-1.mp4")
            with open(other, "wb") as fh:
                fh.write(b"keep")

            removed = remove_atomicparsley_temps(media)
            self.assertEqual(sorted(removed), sorted(temps))
            for path in temps:
                self.assertFalse(os.path.exists(path))
            self.assertTrue(os.path.exists(media))
            self.assertTrue(os.path.exists(other))

    def test_missing_temp_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            media = os.path.join(tmp, "video.mp4")
            with open(media, "wb") as fh:
                fh.write(b"x")
            self.assertEqual(remove_atomicparsley_temps(media), [])

    def test_find_lists_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            media = os.path.join(tmp, "show.mp4")
            with open(media, "wb") as fh:
                fh.write(b"x")
            temp_path = os.path.join(tmp, "show-temp-123.mp4")
            with open(temp_path, "wb") as fh:
                fh.write(b"t")
            self.assertEqual(find_atomicparsley_temps(media), [temp_path])


class TestRunAtomicParsleyInterrupt(unittest.TestCase):
    """run_atomicparsley cleans temp and exits 130 on KeyboardInterrupt."""

    def test_keyboard_interrupt_cleans_temp_and_exits_130(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            media = os.path.join(tmp, "episode.mp4")
            with open(media, "wb") as fh:
                fh.write(b"media")
            temp_path = os.path.join(tmp, "episode-temp-14863.mp4")

            class FakeProc:
                pid = 99999
                returncode = None

                def __init__(self) -> None:
                    self._communicate_calls = 0
                    with open(temp_path, "wb") as fh:
                        fh.write(b"partial")

                def communicate(self, timeout=None):
                    self._communicate_calls += 1
                    if self._communicate_calls == 1:
                        raise KeyboardInterrupt
                    if self.returncode is None:
                        self.returncode = -2
                    return (None, None)

                def poll(self):
                    return self.returncode

                def send_signal(self, sig):
                    self.returncode = -int(sig) if sig else -1

                def kill(self):
                    self.returncode = -9

                def wait(self, timeout=None):
                    if self.returncode is None:
                        self.returncode = -2
                    return self.returncode

            with mock.patch(
                "ap_wrapper.main.subprocess.Popen", return_value=FakeProc()
            ):
                with self.assertRaises(SystemExit) as ctx:
                    run_atomicparsley(
                        ["AtomicParsley", media, "--title", "T", "--overWrite"],
                        media_file=media,
                    )
            self.assertEqual(ctx.exception.code, 130)
            self.assertFalse(
                os.path.exists(temp_path),
                "temp file should be removed after interrupt",
            )
            self.assertTrue(os.path.exists(media))

    def test_successful_overwrite_does_not_require_temp(self) -> None:
        """When no leftover temp exists, run completes normally."""

        class FakeProc:
            pid = 1
            returncode = 0

            def communicate(self, timeout=None):
                return (None, None)

            def poll(self):
                return 0

        with mock.patch(
            "ap_wrapper.main.subprocess.Popen", return_value=FakeProc()
        ):
            result = run_atomicparsley(
                ["AtomicParsley", "/tmp/x.mp4", "--overWrite"],
                media_file="/tmp/x.mp4",
            )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
