from apps.diffuino.python.display import MatrixDisplay


class FakeBridge:
    def __init__(self):
        self.calls = []

    def call(self, method, *parameters, timeout):
        self.calls.append((method, parameters, timeout))
        return 6 if method == "poll_digit" else None


def test_selector_rpc_methods_forward_values():
    display = MatrixDisplay.__new__(MatrixDisplay)
    display.timeout = 5.0
    display.ready_timeout = 20.0
    display.bridge = FakeBridge()

    display.selector_ready()
    assert display.poll_digit() == 6
    display.complete_request(True)

    assert display.bridge.calls == [
        ("selector_ready", (), 5.0),
        ("poll_digit", (), 5.0),
        ("complete_request", (True,), 5.0),
    ]
