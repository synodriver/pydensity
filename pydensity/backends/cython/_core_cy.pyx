# cython: language_level=3
# cython: cdivision=True
cimport cython
from cpython.bytes cimport PyBytes_AS_STRING, PyBytes_FromStringAndSize
from cpython.mem cimport PyMem_Free, PyMem_Malloc
from libc.stdint cimport uint8_t, uint_fast64_t

from pydensity.backends.cython.density cimport (
    DENSITY_ALGORITHM, DENSITY_ALGORITHM_CHAMELEON, DENSITY_ALGORITHM_CHEETAH,
    DENSITY_ALGORITHM_LION, DENSITY_STATE,
    DENSITY_STATE_ERROR_DURING_PROCESSING,
    DENSITY_STATE_ERROR_INPUT_BUFFER_TOO_SMALL,
    DENSITY_STATE_ERROR_INVALID_ALGORITHM, DENSITY_STATE_ERROR_INVALID_CONTEXT,
    DENSITY_STATE_ERROR_OUTPUT_BUFFER_TOO_SMALL, DENSITY_STATE_OK,
    density_compress, density_compress_prepare_context,
    density_compress_safe_size, density_compress_with_context, density_context,
    density_decompress, density_decompress_prepare_context,
    density_decompress_safe_size, density_decompress_with_context,
    density_free_context, density_get_dictionary_size,
    density_processing_result, density_version_major, density_version_minor,
    density_version_revision)

import enum


class Algorithm(enum.Enum):
    chameleon = DENSITY_ALGORITHM_CHAMELEON
    cheetah = DENSITY_ALGORITHM_CHEETAH
    lion = DENSITY_ALGORITHM_LION

cdef inline str format_state(DENSITY_STATE state):
    if state == DENSITY_STATE_ERROR_INPUT_BUFFER_TOO_SMALL:
        return "input_buffer_too_small"
    elif state == DENSITY_STATE_ERROR_OUTPUT_BUFFER_TOO_SMALL:
        return "output buffer too small"
    elif state == DENSITY_STATE_ERROR_DURING_PROCESSING:
        return "error during processing"
    elif state == DENSITY_STATE_ERROR_INVALID_CONTEXT:
        return "invalid context"
    elif state == DENSITY_STATE_ERROR_INVALID_ALGORITHM:
        return "invalid algorithm"
    else:
        return ""

cpdef inline uint8_t major_version() nogil:
    return density_version_major()

cpdef inline uint8_t minor_version() nogil:
    return density_version_minor()

cpdef inline uint8_t revision_version() nogil:
    return density_version_revision()

cpdef inline size_t get_dictionary_size(object algorithm):
    if not isinstance(algorithm, Algorithm):
        raise ValueError("algorithm should be an instance of Algorithm")
    cdef DENSITY_ALGORITHM v = algorithm.value
    with nogil:
        return density_get_dictionary_size(v)

cpdef inline uint_fast64_t compress_safe_size(const uint_fast64_t input_size) nogil:
    return density_compress_safe_size(input_size)

cpdef inline uint_fast64_t decompress_safe_size(const uint_fast64_t input_size) nogil:
    return density_decompress_safe_size(input_size)

cdef inline void* mem_alloc(size_t size) nogil:
    with gil:
        return PyMem_Malloc(size)

cdef inline void mem_free(void* p) nogil:
    with gil:
        PyMem_Free(p)

@cython.freelist(8)
@cython.no_gc
@cython.final
cdef class Compressor:
    cdef DENSITY_STATE c_state
    cdef density_context * context

    def __cinit__(self, object algorithm, bint custom_dictionary):
        if not isinstance(algorithm, Algorithm):
            raise ValueError("algorithm should be an instance of Algorithm")
        cdef DENSITY_ALGORITHM v = algorithm.value
        cdef density_processing_result result = density_compress_prepare_context(v, custom_dictionary,
                                                                                 mem_alloc)
        self.c_state = result.state
        self.context = result.context

    @property
    def state(self):
        return self.c_state

    cpdef inline bytes compress(self, const uint8_t[::1] data):
        cdef uint_fast64_t input_size  = <uint_fast64_t>data.shape[0]
        cdef uint_fast64_t out_size = density_compress_safe_size(input_size)
        cdef bytes out = PyBytes_FromStringAndSize(NULL,<Py_ssize_t>out_size)
        if <void*>out == NULL:
            raise
        cdef uint8_t* out_ptr = <uint8_t* > PyBytes_AS_STRING(out)
        cdef density_processing_result result
        with nogil:
            result = density_compress_with_context(&data[0],input_size,out_ptr,out_size, self.context)
        if result.state != DENSITY_STATE_OK:
            raise ValueError(format_state(result.state))
        self.c_state = result.state
        return out[:result.bytesWritten]

    def __dealloc__(self):
        density_free_context(self.context, mem_free)

@cython.freelist(8)
@cython.no_gc
@cython.final
cdef class DeCompressor:
    cdef DENSITY_STATE c_state
    cdef density_context * context

    def __cinit__(self, const uint8_t[::1] data, bint custom_dictionary):
        cdef density_processing_result result = density_decompress_prepare_context(&data[0],<uint_fast64_t>data.shape[0],custom_dictionary,
                                                                                 mem_alloc)
        self.c_state = result.state
        self.context = result.context

    @property
    def state(self):
        return self.c_state

    cpdef inline bytes decompress(self, const uint8_t[::1] data, uint_fast64_t decompress_safe_size):
        cdef uint_fast64_t input_size = <uint_fast64_t> data.shape[0]
        cdef bytes out = PyBytes_FromStringAndSize(NULL, <Py_ssize_t> decompress_safe_size)
        if <void *> out == NULL:
            raise
        cdef uint8_t * out_ptr = <uint8_t *> PyBytes_AS_STRING(out)
        cdef density_processing_result result
        with nogil:
            result = density_decompress_with_context(&data[0], input_size, out_ptr, decompress_safe_size, self.context)
        if result.state != DENSITY_STATE_OK:
            raise ValueError(format_state(result.state))
        self.c_state = result.state
        return out[:result.bytesWritten]


    def __dealloc__(self):
        density_free_context(self.context, mem_free)


cpdef inline bytes compress(const uint8_t[::1] data, object algorithm):
    if not isinstance(algorithm, Algorithm):
        raise ValueError("algorithm should be an instance of Algorithm")
    cdef DENSITY_ALGORITHM v = algorithm.value

    cdef uint_fast64_t text_length = <uint_fast64_t>data.shape[0]
    cdef uint_fast64_t compress_safe_size = density_compress_safe_size(text_length)
    cdef bytes out = PyBytes_FromStringAndSize(NULL, <Py_ssize_t>compress_safe_size)
    if <void*>out == NULL:
        raise
    cdef uint8_t* out_ptr = <uint8_t*>PyBytes_AS_STRING(out)
    cdef density_processing_result result
    with nogil:
        result = density_compress(&data[0], text_length, out_ptr, compress_safe_size, v)
    if result.state != DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return out[:result.bytesWritten]


cpdef inline uint_fast64_t compress_into(const uint8_t[::1] data, uint8_t[::1] out, object algorithm) except 0:
    if not isinstance(algorithm, Algorithm):
        raise ValueError("algorithm should be an instance of Algorithm")
    cdef DENSITY_ALGORITHM v = algorithm.value
    cdef uint_fast64_t text_length = <uint_fast64_t>data.shape[0]
    cdef density_processing_result result
    with nogil:
        result = density_compress(&data[0], text_length, &out[0], <uint_fast64_t>out.shape[0], v)
    if result.state != DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return result.bytesWritten


cpdef inline bytes decompress(const uint8_t[::1] data, uint_fast64_t decompress_safe_size):
    cdef uint_fast64_t text_length = <uint_fast64_t> data.shape[0]
    cdef bytes out = PyBytes_FromStringAndSize(NULL, <Py_ssize_t> decompress_safe_size)
    if <void *> out == NULL:
        raise
    cdef uint8_t * out_ptr = <uint8_t *> PyBytes_AS_STRING(out)
    cdef density_processing_result result
    with nogil:
        result = density_decompress(&data[0], text_length, out_ptr, decompress_safe_size)
    if result.state != DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return out[:result.bytesWritten]


cpdef inline uint_fast64_t decompress_into(const uint8_t[::1] data, uint8_t[::1] out) except 0:
    cdef uint_fast64_t text_length = <uint_fast64_t> data.shape[0]
    cdef density_processing_result result
    with nogil:
        result = density_decompress(&data[0], text_length, &out[0], <uint_fast64_t>out.shape[0])
    if result.state != DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return result.bytesWritten