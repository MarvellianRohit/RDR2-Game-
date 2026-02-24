#include "mem_tracker.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * A* Pathfinding Implementation for Crimson Trails.
 * Optimized for 2D grids.
 */

typedef struct {
  int x, y;
} Point;

typedef struct Node {
  int x, y;
  int g_cost; // Distance from start node
  int h_cost; // Distance to end node (heuristic)
  int f_cost; // g_cost + h_cost
  struct Node *parent;
} Node;

// Manhattan distance heuristic
int get_distance(int x1, int y1, int x2, int y2) {
  return abs(x1 - x2) + abs(y1 - y2);
}

// Check if a point is within grid bounds and walkable
int is_walkable(const int *grid, int width, int height, int x, int y) {
  if (x < 0 || x >= width || y < 0 || y >= height)
    return 0;
  return grid[y * width + x] == 0;
}

/**
 * Find path using A* algorithm.
 * Returns the number of points in the path.
 */
int find_path(const int *grid, int width, int height, int start_x, int start_y,
              int target_x, int target_y, Point *path_out, int max_path_len) {
  if (start_x == target_x && start_y == target_y)
    return 0;
  if (!is_walkable(grid, width, height, target_x, target_y))
    return 0;

  int max_nodes = width * height;
  Node *open_list[max_nodes];
  int open_count = 0;

  int closed_list[max_nodes];
  for (int i = 0; i < max_nodes; i++)
    closed_list[i] = 0;

  size_t nodes_size = max_nodes * sizeof(Node);
  Node *nodes = (Node *)game_malloc(nodes_size);
  if (!nodes)
    return 0;
  memset(nodes, 0, nodes_size);

  Node *start_node = &nodes[start_y * width + start_x];
  start_node->x = start_x;
  start_node->y = start_y;
  start_node->g_cost = 0;
  start_node->h_cost = get_distance(start_x, start_y, target_x, target_y);
  start_node->f_cost = start_node->g_cost + start_node->h_cost;

  open_list[open_count++] = start_node;

  Node *current = NULL;
  int found = 0;

  while (open_count > 0) {
    // Find node with lowest f_cost
    int best_index = 0;
    for (int i = 1; i < open_count; i++) {
      if (open_list[i]->f_cost < open_list[best_index]->f_cost) {
        best_index = i;
      }
    }

    current = open_list[best_index];

    // Check if reached target
    if (current->x == target_x && current->y == target_y) {
      found = 1;
      break;
    }

    // Move to closed list
    open_list[best_index] = open_list[--open_count];
    closed_list[current->y * width + current->x] = 1;

    // Check neighbors (N, S, E, W)
    int dx[] = {0, 0, 1, -1};
    int dy[] = {1, -1, 0, 0};

    for (int i = 0; i < 4; i++) {
      int nx = current->x + dx[i];
      int ny = current->y + dy[i];

      if (!is_walkable(grid, width, height, nx, ny) ||
          closed_list[ny * width + nx])
        continue;

      Node *neighbor = &nodes[ny * width + nx];
      int new_g_cost = current->g_cost + 1;

      int in_open = 0;
      for (int j = 0; j < open_count; j++) {
        if (open_list[j] == neighbor) {
          in_open = 1;
          break;
        }
      }

      if (new_g_cost < neighbor->g_cost || !in_open) {
        neighbor->x = nx;
        neighbor->y = ny;
        neighbor->g_cost = new_g_cost;
        neighbor->h_cost = get_distance(nx, ny, target_x, target_y);
        neighbor->f_cost = neighbor->g_cost + neighbor->h_cost;
        neighbor->parent = current;

        if (!in_open) {
          open_list[open_count++] = neighbor;
        }
      }
    }
  }

  int path_len = 0;
  if (found) {
    // Backtrack path
    Node *temp = current;
    Point *temp_path = (Point *)game_malloc(max_nodes * sizeof(Point));
    int count = 0;
    while (temp != NULL && count < max_nodes) {
      temp_path[count].x = temp->x;
      temp_path[count].y = temp->y;
      temp = temp->parent;
      count++;
    }

    // Reverse path and skip start
    path_len = (count - 1 < max_path_len) ? count - 1 : max_path_len;
    for (int i = 0; i < path_len; i++) {
      path_out[i] = temp_path[count - 2 - i];
    }
    game_free(temp_path);
  }

  game_free(nodes);
  return path_len;
}
