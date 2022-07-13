# cython: language_level=3
# cython: cdivision=True
from libc.stdint cimport uint8_t, uint_fast64_t


cdef extern from "<stdbool.h>" nogil:
    ctypedef int bool

cdef extern from "density_api.h" nogil:
    ctypedef uint8_t density_byte
    ctypedef bool density_bool
    ctypedef enum DENSITY_ALGORITHM:
        DENSITY_ALGORITHM_CHAMELEON
        DENSITY_ALGORITHM_CHEETAH
        DENSITY_ALGORITHM_LION
    ctypedef enum DENSITY_STATE:
        DENSITY_STATE_OK
        DENSITY_STATE_ERROR_INPUT_BUFFER_TOO_SMALL
        DENSITY_STATE_ERROR_OUTPUT_BUFFER_TOO_SMALL
        DENSITY_STATE_ERROR_DURING_PROCESSING
        DENSITY_STATE_ERROR_INVALID_CONTEXT
        DENSITY_STATE_ERROR_INVALID_ALGORITHM
    ctypedef struct density_context:
        DENSITY_ALGORITHM algorithm
        bool dictionary_type
        size_t dictionary_size
        void* dictionary
    ctypedef struct density_processing_result:
        DENSITY_STATE state
        uint_fast64_t bytesRead
        uint_fast64_t bytesWritten
        density_context* context

    uint8_t density_version_major()
    uint8_t density_version_minor()
    uint8_t density_version_revision()
    size_t density_get_dictionary_size(DENSITY_ALGORITHM algorithm)
    uint_fast64_t density_compress_safe_size(const uint_fast64_t input_size)
    uint_fast64_t density_decompress_safe_size(const uint_fast64_t expected_decompressed_output_size)
    void density_free_context(density_context * context, void (*mem_free)(void *))
    density_processing_result density_compress_prepare_context(const DENSITY_ALGORITHM algorithm,
                                                               const bool custom_dictionary, void *(*mem_alloc)(size_t))
    density_processing_result density_compress_with_context(const uint8_t *input_buffer, const uint_fast64_t input_size,
                                                            uint8_t *output_buffer, const uint_fast64_t output_size,
                                                            density_context * context )
    density_processing_result density_compress(const uint8_t *input_buffer, const uint_fast64_t input_size,
                                               uint8_t *output_buffer, const uint_fast64_t output_size,
                                               const DENSITY_ALGORITHM algorithm)

    density_processing_result density_decompress_prepare_context(const uint8_t *input_buffer,
                                                                 const uint_fast64_t input_size,
                                                                 const bool custom_dictionary,
                                                                 void *(*mem_alloc)(size_t))
    density_processing_result density_decompress_with_context(const uint8_t * input_buffer,
                                                              const uint_fast64_t input_size, uint8_t *output_buffer,
                                                              const uint_fast64_t output_size, density_context * context )
    density_processing_result density_decompress(const uint8_t *input_buffer, const uint_fast64_t input_size,
                                                 uint8_t *output_buffer, const uint_fast64_t output_size)
