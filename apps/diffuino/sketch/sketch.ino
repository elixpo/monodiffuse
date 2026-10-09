// Diffuino STM32 matrix receiver for Arduino UNO Q.

#include <Arduino_LED_Matrix.h>
#include <Arduino_RouterBridge.h>
#include <vector>
#include <zephyr/kernel.h>

Arduino_LED_Matrix matrix;
K_MUTEX_DEFINE(frame_mutex);

constexpr size_t FRAME_ROWS = 8;
constexpr size_t FRAME_COLS = 13;
constexpr size_t FRAME_SIZE = FRAME_ROWS * FRAME_COLS;

uint8_t frame[FRAME_SIZE] = {0};
bool frame_dirty = false;

void draw(std::vector<uint8_t> next_frame) {
  if (next_frame.size() != FRAME_SIZE) {
    return;
  }
  k_mutex_lock(&frame_mutex, K_FOREVER);
  memcpy(frame, next_frame.data(), FRAME_SIZE);
  frame_dirty = true;
  k_mutex_unlock(&frame_mutex);
}

void setup() {
  matrix.begin();
  matrix.setGrayscaleBits(3);

  // A short border confirms that the STM32 sketch booted independently of
  // Linux inference and Bridge RPC readiness.
  uint8_t boot_frame[FRAME_SIZE] = {0};
  for (size_t column = 0; column < FRAME_COLS; ++column) {
    boot_frame[column] = 2;
    boot_frame[(FRAME_ROWS - 1) * FRAME_COLS + column] = 2;
  }
  for (size_t row = 0; row < FRAME_ROWS; ++row) {
    boot_frame[row * FRAME_COLS] = 2;
    boot_frame[row * FRAME_COLS + FRAME_COLS - 1] = 2;
  }
  matrix.draw(boot_frame);
  delay(500);
  matrix.clear();
  Bridge.begin();
  Bridge.provide("draw", draw);
}

void loop() {
  k_mutex_lock(&frame_mutex, K_FOREVER);
  if (frame_dirty) {
    matrix.draw(frame);
    frame_dirty = false;
  }
  k_mutex_unlock(&frame_mutex);
  delay(5);
}
