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
 */
int check_collision_aabb(AABB a, AABB b) {
  return (a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h &&
          a.y + a.h > b.y);
}
