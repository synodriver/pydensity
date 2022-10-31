import os
import sys

from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef(
    """
typedef uint8_t density_byte;
typedef bool density_bool;

typedef enum {
    DENSITY_ALGORITHM_CHAMELEON = 1,
    DENSITY_ALGORITHM_CHEETAH = 2,
    DENSITY_ALGORITHM_LION = 3,
} DENSITY_ALGORITHM;

typedef enum {
    DENSITY_STATE_OK = 0,                                        // Everything went alright
    DENSITY_STATE_ERROR_INPUT_BUFFER_TOO_SMALL,                  // Input buffer size is too small
    DENSITY_STATE_ERROR_OUTPUT_BUFFER_TOO_SMALL,                 // Output buffer size is too small
    DENSITY_STATE_ERROR_DURING_PROCESSING,                       // Error during processing
    DENSITY_STATE_ERROR_INVALID_CONTEXT,                         // Invalid context
    DENSITY_STATE_ERROR_INVALID_ALGORITHM,                       // Invalid algorithm
} DENSITY_STATE;

typedef struct {
    DENSITY_ALGORITHM algorithm;
    bool dictionary_type;
    size_t dictionary_size;
    void* dictionary;
} density_context;

typedef struct {
    DENSITY_STATE state;
    uint_fast64_t bytesRead;
    uint_fast64_t bytesWritten;
    density_context* context;
} density_processing_result;



/***********************************************************************************************************************
 *                                                                                                                     *
 * Density version information                                                                                         *
 *                                                                                                                     *
 ***********************************************************************************************************************/

/*
 * Returns the major density version
 */
 uint8_t density_version_major(void);

/*
 * Returns the minor density version
 */
 uint8_t density_version_minor(void);

/*
 * Returns the density revision
 */
 uint8_t density_version_revision(void);



/***********************************************************************************************************************
 *                                                                                                                     *
 * Density API functions                                                                                               *
 *                                                                                                                     *
 ***********************************************************************************************************************/

/*
 * Return the required size of an algorithm's dictionary
 *
 * @param algorithm the algorithm to use this dictionary for
 */
 size_t density_get_dictionary_size(DENSITY_ALGORITHM algorithm);

/*
 * Return an output buffer byte size which guarantees enough space for encoding input_size bytes
 *
 * @param input_size the size of the input data which is about to be compressed
 */
 uint_fast64_t density_compress_safe_size(const uint_fast64_t input_size);

/*
 * Return an output buffer byte size which, if expected_decompressed_output_size is correct, will enable density to decompress properly
 *
 * @param expected_decompressed_output_size the expected (original) size of the decompressed data
 */
 uint_fast64_t density_decompress_safe_size(const uint_fast64_t expected_decompressed_output_size);

/*
 * Releases a context from memory.
 *
 * @param context the context to free
 * @param mem_free the memory freeing function. If set to NULL, free() is used
 */
 void density_free_context(density_context *const context, void (*mem_free)(void *));

/*
 * Allocate a context in memory using the provided function and optional dictionary
 *
 * @param algorithm the required algorithm
 * @param custom_dictionary use an eventual custom dictionary ? If set to true the context's dictionary will have to be allocated
 * @param mem_alloc the memory allocation function. If set to NULL, malloc() is used
 */
 density_processing_result density_compress_prepare_context(const DENSITY_ALGORITHM algorithm, const bool custom_dictionary, void *(*mem_alloc)(size_t));

/*
 * Compress an input_buffer of input_size bytes and store the result in output_buffer, using the provided context.
 * Important note   * this function could be unsafe memory-wise if not used properly.
 *
 * @param input_buffer a buffer of bytes
 * @param input_size the size in bytes of input_buffer
 * @param output_buffer a buffer of bytes
 * @param output_size the size of output_buffer, must be at least DENSITY_MINIMUM_OUTPUT_BUFFER_SIZE
 * @param context a pointer to a context structure
 */
 density_processing_result density_compress_with_context(const uint8_t *input_buffer, const uint_fast64_t input_size, uint8_t *output_buffer, const uint_fast64_t output_size, density_context *const context);

/*
 * Compress an input_buffer of input_size bytes and store the result in output_buffer.
 *
 * @param input_buffer a buffer of bytes
 * @param input_size the size in bytes of input_buffer
 * @param output_buffer a buffer of bytes
 * @param output_size the size of output_buffer, must be at least DENSITY_MINIMUM_OUTPUT_BUFFER_SIZE
 * @param algorithm the algorithm to use
 */
 density_processing_result density_compress(const uint8_t *input_buffer, const uint_fast64_t input_size, uint8_t *output_buffer, const uint_fast64_t output_size, const DENSITY_ALGORITHM algorithm);

/*
 * Reads the compressed data's header and creates an adequate decompression context.
 *
 * @param input_buffer a buffer of bytes
 * @param input_size the size in bytes of input_buffer
 * @param custom_dictionary use a custom dictionary ? If set to true the context's dictionary will have to be allocated
 * @param mem_alloc the memory allocation function. If set to NULL, malloc() is used
 */
 density_processing_result density_decompress_prepare_context(const uint8_t *input_buffer, const uint_fast64_t input_size, const bool custom_dictionary, void *(*mem_alloc)(size_t));

/*
 * Decompress an input_buffer of input_size bytes and store the result in output_buffer, using the provided dictionary.
 * Important notes  * You must know in advance the algorithm used for compression to provide the proper dictionary.
 *                  * This function could be unsafe memory-wise if not used properly.
 *
 * @param input_buffer a buffer of bytes
 * @param input_size the size in bytes of input_buffer
 * @param output_buffer a buffer of bytes
 * @param output_size the size of output_buffer, must be at least DENSITY_MINIMUM_OUTPUT_BUFFER_SIZE
 * @param dictionaries a pointer to a dictionary
 */
 density_processing_result density_decompress_with_context(const uint8_t * input_buffer, const uint_fast64_t input_size, uint8_t *output_buffer, const uint_fast64_t output_size, density_context *const context);

/*
 * Decompress an input_buffer of input_size bytes and store the result in output_buffer.
 *
 * @param input_buffer a buffer of bytes
 * @param input_size the size in bytes of input_buffer
 * @param output_buffer a buffer of bytes
 * @param output_size the size of output_buffer, must be at least DENSITY_MINIMUM_OUTPUT_BUFFER_SIZE
 */
 density_processing_result density_decompress(const uint8_t *input_buffer, const uint_fast64_t input_size, uint8_t *output_buffer, const uint_fast64_t output_size);

void* malloc(size_t n);
void free(void* p);
    """
)

source = """
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "density_api.h"
"""
c_sources = []
for root, dirs, files in os.walk("./dep/src"):
    for file in files:
        if file.endswith(".c"):
            c_sources.append(os.path.join(root, file))

print(c_sources)

ffibuilder.set_source(
    "pydensity.backends.cffi._density",
    source,
    sources=c_sources,
    include_dirs=["./dep/src"],
)

if __name__ == "__main__":
    ffibuilder.compile()
