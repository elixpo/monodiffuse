# Diffuino

Diffuino runs a class-conditioned MNIST diffusion model on the Arduino UNO Q.
The Qualcomm Linux processor performs ONNX inference and streams 8×13 grayscale
frames over Bridge RPC; the STM32 refreshes the onboard matrix. The reliable
interactive default is a separately trained FP32 generator. Binary-weight
checkpoints remain part
of the research workflow, but are deployed only after passing the same 10-class
matrix validation.

## Install the packaged Arduino App

Build a deterministic runtime-only archive on a workstation:

~~~bash
python -m apps.diffuino.package_app
scp dist/diffuino.zip arduino@<UNO-Q-IP>:/home/arduino/
~~~

Then import, flash, and start it from the UNO Q shell:

~~~bash
arduino-app-cli app import ~/diffuino.zip
arduino-app-cli app start user:diffuino
arduino-app-cli app logs user:diffuino --tail 200 --all
~~~

Make Diffuino the board's startup app after verifying one manual run:

~~~bash
arduino-app-cli properties set default user:diffuino
~~~

The UNO Q app supervisor will then launch both the STM32 sketch and Linux
inference container after every boot. A separate systemd unit is unnecessary and
would not manage the two processors as one application.

The archive includes only the runtime Python modules, pinned dependencies, the
two required ONNX models, the STM32 sketch, and MANIFEST.sha256. It deliberately
excludes PyTorch checkpoints, training utilities, seed-search tools, and tests.
If an older app with the same ID is already installed, remove or update that app
before importing the new archive.

## Install from a repository checkout

```bash
cd ~/monodiffuse
git pull --ff-only
source .venv/bin/activate
python -m pip install -r apps/diffuino/requirements.txt
```

Open `apps/diffuino` in Arduino App Lab and run it once to compile and flash
`sketch/sketch.ino`. Then generate a requested digit from the repository root:

App Lab discovers user applications under `~/ArduinoApps`. From the UNO Q shell,
install or update this repository checkout with:

```bash
mkdir -p ~/ArduinoApps/diffuino
rsync -a ~/monodiffuse/apps/diffuino/ ~/ArduinoApps/diffuino/
arduino-app-cli app list
arduino-app-cli app start user:diffuino
```

The matrix briefly displays a border when the STM32 sketch boots. Diffusion
frames begin after the Linux container and Bridge RPC are ready. To inspect a
run that exits before displaying frames:

```bash
arduino-app-cli app ps
arduino-app-cli app logs user:diffuino --tail 200 --all
```

```bash
python -m apps.diffuino.python.main --digit 7
```

The default conditional FP32 deployment accepts `--digit 0` through `--digit 9`
and automatically selects a visually audited initial-noise seed for that class.
Pass `--seed` explicitly to explore other outputs. Use `--no-matrix` to benchmark
inference without Bridge. The
final 28×28 image is saved under
`apps/diffuino/output/latest.png`. Each run creates exactly one sample and then
prints a held-out MNIST classifier prediction so the terminal result can be
matched against the matrix. The prediction is a diagnostic consistency check,
not a ground-truth label or a generative-quality metric.

The physical framebuffer is horizontal: 8 rows by 13 columns. Diffuino keeps
the digit square by centering an 8×8 image within those 13 columns.

The 8×8 digit conversion applies per-frame contrast stretching. Digits `2`,
`3`, and `8` use crisp nearest-neighbor downsampling so their holes and stroke
gaps survive; `0`, `1`, `4`, `5`, `6`, `7`, and `9` retain smoother bilinear
downsampling.

The visually audited default seeds are `0:15`, `1:16`, `2:50`, `3:22`, `4:0`,
`5:0`, `6:12`, `7:4`, `8:10`, and `9:18`.
All digits retain eight grayscale levels; no destructive binary threshold is
applied.

## Hardware BCD selector

When the packaged app starts without a digit argument, it enters appliance mode
and loads the ONNX model only once. After Linux inference and Bridge RPC are
ready, the matrix displays a centered D and RGB LED 4 turns green.

Connect the four BCD bits and trigger as follows:

| UNO Q pin | Function |
| --- | --- |
| D2 | bit 0, least significant bit |
| D3 | bit 1 |
| D4 | bit 2 |
| D5 | bit 3, most significant bit |
| D6 | active-high request button |

All five inputs use the STM32's internal pull-down. Drive them with
board-compatible 3.3 V logic and share ground with the selector circuit. Connect
the pushbutton between D6 and 3.3 V. Set D2--D5 before pressing D6.

The STM32 debounces D6 for 40 ms, samples D2--D5 once on the accepted rising
edge, and latches that value for the whole diffusion run. Changes on the BCD
pins and further D6 edges are ignored while busy. Values 0--9 start exactly one
generation. The external AND/OR/NOT validity logic prevents values 10--15 from
asserting a request; a software range check remains only as a wiring or logic
fault guard. After the final image has been held for 1.2 seconds, the selector
rearms only after D6 is released. The green ready LED and D then return.

The service log makes the hardware selection explicit:

~~~text
selector=ready bcd_pins=2,3,4,5 trigger_pin=6 bit_order=lsb_to_msb
bcd_selected=3
requested_digit=3 generated_digit=3 classifier_confidence=... match=yes
selector=rearming_after_release
~~~

During matrix inference, the four onboard RGB LEDs expose live system state:
LED 1 shows CPU load, LED 2 shows RAM load, LED 3 fades from blue to magenta as
diffusion progresses, and LED 4 is blue while running then green/red for a
classifier match/mismatch. Diffuino restores the Linux-managed LED 1/2 states
after inference. Pass `--no-status-leds` to disable this behavior.

Screen candidate seeds on a workstation before running them on the board:

```bash
python -m apps.diffuino.screen_seeds --start 0 --count 50
# Recheck a shortlist at higher visual density:
python -m apps.diffuino.screen_seeds --seeds 11,12,30 --columns 3
```

This writes labeled 28×28 and exact quantized 8×8 matrix contact sheets plus a
CSV under `apps/diffuino/output/`.
The automatic `KEEP` filter combines classifier confidence with foreground-ink
and contrast checks; the contact sheet remains the final visual check.

The sampler remains aligned with the paper's 1,000-step ancestral DDPM process,
but the reliable interactive checkpoint is an artifact-specific,
class-conditioned FP32 model. A reduced-step DDIM mode is available for profiling
and is not used for the exhibit.

## Training workstation

```bash
venv/bin/python -m apps.diffuino.export_onnx
```

The unconditional export uses the best verified native
uncentered/pre-activation seed-2 checkpoint from the paper. It materializes the
learned one-bit convolution weights into ordinary floating-point convolution
tensors because ONNX Runtime does not use a packed XNOR kernel. The trained
representation is binary-weight, but this deployment does not claim binary
arithmetic acceleration.
