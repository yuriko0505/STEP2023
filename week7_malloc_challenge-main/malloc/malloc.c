//
// >>>> malloc challenge! <<<<
//
// Your task is to improve utilization and speed of the following malloc
// implementation.
// Initial implementation is the same as the one implemented in simple_malloc.c.
// For the detailed explanation, please refer to simple_malloc.c.

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE_INDEX 12
#define NUM_OF_BIN 12

//
// Interfaces to get memory pages from OS
//

void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

//
// Struct definitions
//

typedef struct my_metadata_t {
	size_t size;
	struct my_metadata_t *next;
} my_metadata_t;

typedef struct my_heap_t {
	my_metadata_t *free_head;
	my_metadata_t dummy;
} my_heap_t;

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap[NUM_OF_BIN];

//
// Helper functions (feel free to add/remove/edit!)
//

int get_free_list_index(size_t size) {
	if (size < 2) {
		return 0;
	} else if (size < 4){
		return 1;
	} else if (size < 8) {
		return 2;
	} else if (size < 16) {
		return 3;
	} else if (size < 32) {
		return 4;
	} else if (size < 64) {
		return 5;
	} else if (size < 128){
		return 6;
	} else if (size < 256){
		return 7;
	} else if (size < 512){
		return 8;
	} else if (size < 1024){
		return 9;
	} else if (size < 2048){
		return 10;
	} else {
		return 11;
	}
}

void my_add_to_free_list(my_metadata_t *metadata, int index) {
	assert(!metadata->next);
	metadata->next = my_heap[index].free_head;
	my_heap[index].free_head = metadata;
}

void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev, int index) {
	if (prev) {
		prev->next = metadata->next;
	} else {
		my_heap[index].free_head = metadata->next;
	}
	metadata->next = NULL;
}

//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

// This is called at the beginning of each challenge.
void my_initialize() {
	for (int i=0; i<NUM_OF_BIN; i++){
		my_heap[i].free_head = &my_heap[i].dummy;
		my_heap[i].dummy.size = 0;
		my_heap[i].dummy.next = NULL;
	}
}

// my_malloc() is called every time an object is allocated.
// |size| is guaranteed to be a multiple of 8 bytes and meets 8 <= |size| <= 4000.
// You are not allowed to use any library functions other than
// mmap_from_system() / munmap_to_system().
void *my_malloc(size_t size) {
	my_metadata_t *metadata;
	my_metadata_t *prev = NULL;

	// TODO: Update this logic to Best-fit!
	my_metadata_t *best_metadata = NULL;
	my_metadata_t *prev_best = NULL;
	size_t best_size = 1 << MAX_SIZE_INDEX;
	int index = get_free_list_index(size);
	for(; index < NUM_OF_BIN; index++){
		metadata = my_heap[index].free_head;
		prev = NULL;
		while(metadata){
			if (metadata->size >= size && metadata->size < best_size){
				best_size = metadata->size;
				best_metadata = metadata;
				prev_best = prev;
			}
			prev = metadata;
			metadata = metadata->next;
		}
		if(best_metadata){
			break;
		}
	}
	prev = prev_best;
	metadata = best_metadata;
	// First-fit: Find the first free slot the object fits.
	// while (metadata && metadata->size < size) {
	//   prev = metadata;
	//   metadata = metadata->next;
	// }
	// now, metadata points to the first free slot
	// and prev is the previous entry.

	if (!metadata) {
		// There was no free slot available. We need to request a new memory region
		// from the system by calling mmap_from_system().
		//
		//     | metadata | free slot |
		//     ^
		//     metadata
		//     <---------------------->
		//            buffer_size
		size_t buffer_size = 4096;
		my_metadata_t *metadata = (my_metadata_t *)mmap_from_system(buffer_size);
		metadata->size = buffer_size - sizeof(my_metadata_t);
		metadata->next = NULL;
		// Add the memory region to the free list.
		int index = get_free_list_index(metadata->size);
		my_add_to_free_list(metadata, index);
		// Now, try my_malloc() again. This should succeed.
		return my_malloc(size);
	}

	// |ptr| is the beginning of the allocated object.
	//
	// ... | metadata | object | ...
	//     ^          ^
	//     metadata   ptr
	void *ptr = metadata + 1;
	size_t remaining_size = metadata->size - size;
	// Remove the free slot from the free list.
	my_remove_from_free_list(metadata, prev, index);

	if (remaining_size > sizeof(my_metadata_t)) {
		metadata->size = size;
		// Create a new metadata for the remaining free slot.
		//
		// ... | metadata | object | metadata | free slot | ...
		//     ^          ^        ^
		//     metadata   ptr      new_metadata
		//                 <------><---------------------->
		//                   size       remaining size
		my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size);
		new_metadata->size = remaining_size - sizeof(my_metadata_t);
		new_metadata->next = NULL;
		// Add the remaining free slot to the free list.
		int new_index = get_free_list_index(new_metadata->size);
		my_add_to_free_list(new_metadata, new_index);
	}
	return ptr;
}

// This is called every time an object is freed.  You are not allowed to
// use any library functions other than mmap_from_system / munmap_to_system.
void my_free(void *ptr) {
	// Look up the metadata. The metadata is placed just prior to the object.
	//
	// ... | metadata | object | ...
	//     ^          ^
	//     metadata   ptr
	my_metadata_t *metadata = (my_metadata_t *)ptr - 1;
	// Add the free slot to the free list.
	int index = get_free_list_index(metadata->size);
	my_add_to_free_list(metadata, index);
}

// This is called at the end of each challenge.
void my_finalize() {
  // Nothing is here for now.
  // feel free to add something if you want!
}

void test() {
  // Implement here!
  assert(1 == 1); /* 1 is 1. That's always true! (You can remove this.) */
}
