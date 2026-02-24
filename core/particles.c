#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PARTICLES 10000

typedef struct {
  float x, y;
  float vx, vy;
  float life;
  float max_life;
  uint32_t color;
  int active;
} Particle;

static Particle pool[MAX_PARTICLES];
static int next_available = 0;

void particles_init() {
  memset(pool, 0, sizeof(pool));
  next_available = 0;
}

void emit(float x, float y, float vx, float vy, float life, uint32_t color) {
  // Find next available slot using a simple ring-buffer style search
  int start = next_available;
  do {
    if (!pool[next_available].active) {
      Particle *p = &pool[next_available];
      p->x = x;
      p->y = y;
      p->vx = vx;
      p->vy = vy;
      p->life = life;
      p->max_life = life;
      p->color = color;
      p->active = 1;

      next_available = (next_available + 1) % MAX_PARTICLES;
      return;
    }
    next_available = (next_available + 1) % MAX_PARTICLES;
  } while (next_available != start);

  // If we reach here, the pool is full; oldest particle will be recycled
  // eventually
}

void update_particles(float dt) {
  for (int i = 0; i < MAX_PARTICLES; i++) {
    if (pool[i].active) {
      // Apply velocity
      pool[i].x += pool[i].vx * dt;
      pool[i].y += pool[i].vy * dt;

      // Apply simple gravity (down is +y in screen-ish coords, but we're in
      // cartesian)
      pool[i].vy += 0.5f * dt;

      // Aging
      pool[i].life -= dt;
      if (pool[i].life <= 0) {
        pool[i].active = 0;
      }
    }
  }
}

Particle *get_particle_pool() { return pool; }

int get_max_particles() { return MAX_PARTICLES; }
