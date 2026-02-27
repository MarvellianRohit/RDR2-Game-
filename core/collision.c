#include <stdio.h>

/**
 * High-speed AABB collision detection for Crimson Trails.
 */

typedef struct {
  float x;
  float y;
  float w;
  float h;
} AABB;

/**
 * Returns 1 if two AABBs intersect, 0 otherwise.
 * Optimized for decoupled hitboxes where x,y are base positions and w,h are
 * size.
 */
int check_collision_aabb(AABB a, AABB b) {
  return (a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h &&
          a.y + a.h > b.y);
}

/**
 * Enhanced collision check that accounts for entity offsets.
 */
int check_entity_collision(float x1, float y1, float w1, float h1, float ox1,
                           float oy1, float x2, float y2, float w2, float h2,
                           float ox2, float oy2) {
  float ax = x1 + ox1;
  float ay = y1 + oy1;
  float bx = x2 + ox2;
  float by = y2 + oy2;

  return (ax < bx + w2 && ax + w1 > bx && ay < by + h2 && ay + h1 > by);
}
