#include <stdio.h>

typedef struct {
  float x;
  float y;
  float z;
} Vector3;

typedef struct {
  Vector3 start;
  Vector3 velocity;
} ProjectileInput;

/**
 * Calculates the landing coordinate (y=0) for a set of projectiles.
 * Factors in gravity and a basic wind resistance (drag) constant.
 *
 * Formula (simplified linear drag):
 * dv/dt = g - k*v
 */
void calculate_impacts(const ProjectileInput *inputs, Vector3 *outputs,
                       int count, float gravity, float drag) {
  for (int i = 0; i < count; i++) {
    Vector3 pos = inputs[i].start;
    Vector3 vel = inputs[i].velocity;

    float dt = 0.01f; // High precision step for simulation
    float total_time = 0.0f;

    // Simulation loop until it hits the ground (y <= 0)
    while (pos.y > 0.0f && total_time < 60.0f) { // 60s timeout safety
      // Acceleration with drag
      // a = g - k*v
      float ax = -drag * vel.x;
      float ay = -gravity - (drag * vel.y);
      float az = -drag * vel.z;

      // Update velocity
      vel.x += ax * dt;
      vel.y += ay * dt;
      vel.z += az * dt;

      // Update position
      pos.x += vel.x * dt;
      pos.y += vel.y * dt;
      pos.z += vel.z * dt;

      total_time += dt;
    }

    outputs[i] = pos;
  }
}
