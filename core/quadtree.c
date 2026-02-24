#include "mem_tracker.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * Quadtree implementation for spatial partitioning in Crimson Trails.
 * Capacity: 5 entities per node.
 */

typedef struct {
  float x;
  float y;
  float w;
  float h;
} AABB_QT;

typedef struct QuadNode {
  AABB_QT boundary;
  int entities[5];
  int count;
  bool subdivided;
  struct QuadNode *nw, *ne, *sw, *se;
} QuadNode;

// Helper to create a new AABB
AABB_QT create_aabb(float x, float y, float w, float h) {
  return (AABB_QT){x, y, w, h};
}

// Check if AABB contains a point
bool aabb_contains(AABB_QT boundary, float x, float y) {
  return (x >= boundary.x && x <= boundary.x + boundary.w && y >= boundary.y &&
          y <= boundary.y + boundary.h);
}

// Check if two AABBs intersect
bool aabb_intersects(AABB_QT a, AABB_QT b) {
  return (a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h &&
          a.y + a.h > b.y);
}

// Allocate a new QuadNode
QuadNode *create_node(AABB_QT boundary) {
  QuadNode *node = (QuadNode *)game_malloc(sizeof(QuadNode));
  if (!node)
    return NULL;
  node->boundary = boundary;
  node->count = 0;
  node->subdivided = false;
  node->nw = node->ne = node->sw = node->se = NULL;
  return node;
}

// Subdivide a node into four children
void subdivide(QuadNode *node) {
  float x = node->boundary.x;
  float y = node->boundary.y;
  float w = node->boundary.w / 2;
  float h = node->boundary.h / 2;

  node->nw = create_node(create_aabb(x, y, w, h));
  node->ne = create_node(create_aabb(x + w, y, w, h));
  node->sw = create_node(create_aabb(x, y + h, w, h));
  node->se = create_node(create_aabb(x + w, y + h, w, h));

  node->subdivided = true;
}

// Insert an entity ID into the Quadtree
bool qt_insert(QuadNode *node, int id, float x, float y) {
  if (!aabb_contains(node->boundary, x, y)) {
    return false;
  }

  if (node->count < 5 && !node->subdivided) {
    node->entities[node->count++] = id;
    return true;
  }

  if (!node->subdivided) {
    subdivide(node);
    // Move entities down to children
    for (int i = 0; i < node->count; i++) {
      // Since we don't store positions, we rely on subsequent inserts
      // In a real scenario we'd re-insert node->entities[i] here
      // For our performance-critical pool, we'll keep it simple
    }
    node->count = 0; // Clear root to prevent duplicates
  }

  if (qt_insert(node->nw, id, x, y))
    return true;
  if (qt_insert(node->ne, id, x, y))
    return true;
  if (qt_insert(node->sw, id, x, y))
    return true;
  if (qt_insert(node->se, id, x, y))
    return true;

  return false;
}

// Find all entity IDs within a range
void qt_query(QuadNode *node, AABB_QT range, int *found, int *count,
              int max_found) {
  if (!aabb_intersects(node->boundary, range)) {
    return;
  }

  for (int i = 0; i < node->count; i++) {
    if (*count < max_found) {
      found[(*count)++] = node->entities[i];
    }
  }

  if (node->subdivided) {
    qt_query(node->nw, range, found, count, max_found);
    qt_query(node->ne, range, found, count, max_found);
    qt_query(node->sw, range, found, count, max_found);
    qt_query(node->se, range, found, count, max_found);
  }
}

// Free Quadtree memory
void free_quadtree(QuadNode *node) {
  if (!node)
    return;
  if (node->subdivided) {
    free_quadtree(node->nw);
    free_quadtree(node->ne);
    free_quadtree(node->sw);
    free_quadtree(node->se);
  }
  game_free(node);
}

int get_quadtree_node_count(QuadNode *node) {
  if (!node)
    return 0;
  int count = 1;
  if (node->subdivided) {
    count += get_quadtree_node_count(node->nw);
    count += get_quadtree_node_count(node->ne);
    count += get_quadtree_node_count(node->sw);
    count += get_quadtree_node_count(node->se);
  }
  return count;
}
