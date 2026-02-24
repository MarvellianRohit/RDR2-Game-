#ifndef MEM_TRACKER_H
#define MEM_TRACKER_H

#include <stddef.h>

void *game_malloc_internal(size_t size, const char *file, int line);
void game_free_internal(void *ptr, const char *file, int line);
void dump_memory_leaks();
size_t get_total_memory_usage();

#define game_malloc(size) game_malloc_internal(size, __FILE__, __LINE__)
#define game_free(ptr) game_free_internal(ptr, __FILE__, __LINE__)

#endif // MEM_TRACKER_H
