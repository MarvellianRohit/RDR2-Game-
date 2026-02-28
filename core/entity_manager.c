#include "mem_tracker.h"
#include <stdio.h>
#include <stdlib.h>

/**
 * Doubly Linked List for high-performance entity tracking.
 * Optimized for frequent insertions and deletions.
 */

typedef struct Entity {
  int id;
  float x;
  float y;
  float vx;
  float vy;
  int sprite_type; // 0=None, 1=Bullet, 2=Enemy, etc.
  float health;
  int state; // 0=ALIVE, 1=DEAD
  float hitbox_width;
  float hitbox_height;
  float hitbox_offset_x;
  float hitbox_offset_y;
  int active;
  struct Entity *prev;
  struct Entity *next;
} Entity;

static Entity *head = NULL;
static int next_id = 0;

// Add a new entity to the list
Entity *add_entity(float x, float y, int sprite_type) {
  Entity *new_entity = (Entity *)game_malloc(sizeof(Entity));
  if (!new_entity)
    return NULL;

  new_entity->id = next_id++;
  new_entity->x = x;
  new_entity->y = y;
  new_entity->vx = 0.0f;
  new_entity->vy = 0.0f;
  new_entity->sprite_type = sprite_type;
  new_entity->health = 100.0f;
  new_entity->state = 0;
  new_entity->hitbox_width = 32.0f;  // Default
  new_entity->hitbox_height = 32.0f; // Default
  new_entity->hitbox_offset_x = 0.0f;
  new_entity->hitbox_offset_y = 0.0f;
  new_entity->active = 1;
  new_entity->prev = NULL;
  new_entity->next = head;

  if (head) {
    head->prev = new_entity;
  }
  head = new_entity;

  printf("[C-Entity] Spawned ID: %d at (%.2f, %.2f)\n", new_entity->id, x, y);
  return new_entity;
}

// Batch update positions (using per-entity velocity)
void update_entities(float dt) {
  Entity *current = head;
  while (current) {
    if (current->active) {
      current->x += current->vx * dt;
      current->y += current->vy * dt;
    }
    current = current->next;
  }
}

// Remove inactive entities and free memory
void remove_inactive_entities() {
  Entity *current = head;
  while (current) {
    Entity *next = current->next;
    if (!current->active) {
      // Unlink node
      if (current->prev) {
        current->prev->next = current->next;
      } else {
        head = current->next; // Update head
      }
      if (current->next) {
        current->next->prev = current->prev;
      }

      printf("[C-Entity] Freed ID: %d\n", current->id);
      game_free(current);
    }
    current = next;
  }
}

// Return the head of the entity list for external traversal
Entity *get_entity_head() { return head; }

// Shutdown: Clear all entities
void clear_entities() {
  Entity *current = head;
  while (current) {
    Entity *next = current->next;
    game_free(current);
    current = next;
  }
  head = NULL;
  printf("[C-Entity] System cleared.\n");
}

int get_entity_count() {
  int count = 0;
  Entity *current = head;
  while (current) {
    if (current->active)
      count++;
    current = current->next;
  }
  return count;
}
