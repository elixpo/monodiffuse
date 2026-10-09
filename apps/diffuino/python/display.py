"""Bridge adapter for the STM32-owned UNO Q LED matrix."""

from __future__ import annotations

from arduino.router_bridge import Bridge


class MatrixDisplay:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.bridge = Bridge()

    def __enter__(self) -> "MatrixDisplay":
        if not self.bridge.connect(timeout=self.timeout):
            raise RuntimeError("Arduino Router did not become available")
        return self

    def draw(self, payload: bytes) -> None:
        self.bridge.call("draw", payload, timeout=self.timeout)

    def clear(self) -> None:
        self.draw(bytes(104))

    def __exit__(self, *_args) -> None:
        self.bridge.disconnect()
