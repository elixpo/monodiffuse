"""Bridge adapter for the STM32-owned UNO Q LED matrix."""

from __future__ import annotations

import time

from arduino.router_bridge import Bridge


class MatrixDisplay:
    def __init__(self, timeout: float = 5.0, ready_timeout: float = 20.0):
        self.timeout = timeout
        self.ready_timeout = ready_timeout
        self.bridge = Bridge()

    def __enter__(self) -> "MatrixDisplay":
        if not self.bridge.connect(timeout=self.timeout):
            raise RuntimeError("Arduino Router did not become available")
        return self

    def draw(self, payload: bytes) -> None:
        deadline = time.monotonic() + self.ready_timeout
        while True:
            try:
                self.bridge.call("draw", payload, timeout=self.timeout)
                return
            except Exception as error:
                # The Linux router socket becomes available before a freshly
                # flashed sketch has necessarily registered its RPC methods.
                # Treat that short window as startup, not a fatal missing-
                # firmware error.
                if "method draw not available" not in str(error):
                    raise
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        "STM32 draw RPC did not become ready; verify the Diffuino sketch is running"
                    ) from error
                time.sleep(0.25)

    def clear(self) -> None:
        self.draw(bytes(104))

    def __exit__(self, *_args) -> None:
        self.bridge.disconnect()
