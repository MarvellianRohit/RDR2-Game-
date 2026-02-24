#include "mem_tracker.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct AllocationRecord {
  void *address;
  size_t size;
  const char *file;
  int line;
  struct AllocationRecord *next;
} AllocationRecord;

static AllocationRecord *head = NULL;
static size_t total_allocated = 0;

void *game_malloc_internal(size_t size, const char *file, int line) {
  void *ptr = malloc(size);
  if (!ptr)
    return NULL;

  AllocationRecord *record =
      (AllocationRecord *)malloc(sizeof(AllocationRecord));
  if (!record) {
    free(ptr);
    return NULL;
  }

  record->address = ptr;
  record->size = size;
  record->file = file;
  record->line = line;
  record->next = head;
  head = record;

  total_allocated += size;
  return ptr;
}

void game_free_internal(void *ptr, const char *file, int line) {
  if (!ptr)
    return;

  AllocationRecord **curr = &head;
  while (*curr) {
    if ((*curr)->address == ptr) {
      AllocationRecord *to_free = *curr;
      *curr = (*curr)->next;
      total_allocated -= to_free->size;
      free(to_free);
      free(ptr);
      return;
    }
    curr = &((*curr)->next);
  }

  fprintf(stderr,
          "[Mem Tracker] ERROR: Attempted to free untracked or double-freed "
          "address %p at %s:%d\n",
          ptr, file, line);
}

void dump_memory_leaks() {
  printf("\n--- Crimson Trails Memory Report ---\n");
  if (!head) {
    printf("No memory leaks detected. Clean exit.\n");
  } else {
    printf("LEAK DETECTED! Total Unfreed: %zu bytes\n", total_allocated);
    AllocationRecord *curr = head;
    while (curr) {
      printf("  Address: %p | Size: %zu bytes | Allocated at: %s:%d\n",
             curr->address, curr->size, curr->file, curr->line);
      curr = curr->next;
    }
  }
  printf("------------------------------------\n\n");
}

size_t get_total_memory_usage() { return total_allocated; }
