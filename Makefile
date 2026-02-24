# Makefile for Crimson Trails Engine
# Optimized for macOS ARM64 (Apple Silicon)

CC = clang
CFLAGS = -O3 -Wall -Wextra -ffast-math -flto -arch arm64
LDFLAGS = -dynamiclib -arch arm64

TARGET = libengine.dylib
SRCS = core/engine.c core/ballistics.c core/entity_manager.c core/pathfinding.c core/collision.c core/quadtree.c core/particles.c core/mem_tracker.c
OBJS = $(SRCS:.c=.o)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
