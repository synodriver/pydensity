# -*- coding: utf-8 -*-
import enum

from pydensity.backends.cffi._density import ffi, lib


class Algorithm(enum.Enum):
    chameleon = lib.DENSITY_ALGORITHM_CHAMELEON
    cheetah = lib.DENSITY_ALGORITHM_CHEETAH
    lion = lib.DENSITY_ALGORITHM_LION


def format_state(state) -> str:
    if state == lib.DENSITY_STATE_ERROR_INPUT_BUFFER_TOO_SMALL:
        return "input_buffer_too_small"
    elif state == lib.DENSITY_STATE_ERROR_OUTPUT_BUFFER_TOO_SMALL:
        return "output buffer too small"
    elif state == lib.DENSITY_STATE_ERROR_DURING_PROCESSING:
        return "error during processing"
    elif state == lib.DENSITY_STATE_ERROR_INVALID_CONTEXT:
        return "invalid context"
    elif state == lib.DENSITY_STATE_ERROR_INVALID_ALGORITHM:
        return "invalid algorithm"
    else:
        return ""


def major_version():
    return lib.density_version_major()


def minor_version():
    return lib.density_version_minor()


def revision_version():
    return lib.density_version_revision()


def get_dictionary_size(algorithm: Algorithm):
    if not isinstance(algorithm, Algorithm):
        raise ValueError("algorithm should be an instance of Algorithm")
    v = algorithm.value
    return lib.density_get_dictionary_size(v)


def compress_safe_size(input_size: int):
    return lib.density_compress_safe_size(input_size)


def decompress_safe_size(input_size: int):
    return lib.density_decompress_safe_size(input_size)


class Compressor:
    def __init__(self, algorithm: Algorithm, custom_dictionary: bool):
        if not isinstance(algorithm, Algorithm):
            raise ValueError("algorithm should be an instance of Algorithm")
        v = algorithm.value
        result = lib.density_compress_prepare_context(v, custom_dictionary, lib.malloc)
        self.c_state = result.state
        self.context = result.context

    @property
    def state(self):
        return self.c_state

    def compress(self, data: bytes) -> bytes:
        input_size = len(data)
        out_size = lib.density_compress_safe_size(input_size)
        out = ffi.new(f"char[{out_size}]")
        result = lib.density_compress_with_context(
            ffi.cast("uint8_t*", ffi.from_buffer(data)),
            input_size,
            ffi.cast("uint8_t*", out),
            out_size,
            self.context,
        )
        if result.state != lib.DENSITY_STATE_OK:
            raise ValueError(format_state(result.state))
        self.c_state = result.state
        return ffi.unpack(out, result.bytesWritten)

    def __del__(self):
        lib.density_free_context(self.context, lib.free)


class DeCompressor:
    def __init__(self, data: bytes, custom_dictionary: bool):
        result = lib.density_decompress_prepare_context(
            ffi.cast("uint8_t*", ffi.from_buffer(data)),
            len(data),
            custom_dictionary,
            lib.malloc,
        )
        self.c_state = result.state
        self.context = result.context

    @property
    def state(self):
        return self.c_state

    def decompress(self, data: bytes, decompress_safe_size: int) -> bytes:
        input_size = len(data)
        out = ffi.new(f"char[{decompress_safe_size}]")
        result = lib.density_decompress_with_context(
            ffi.cast("uint8_t*", ffi.from_buffer(data)),
            input_size,
            ffi.cast("uint8_t*", out),
            decompress_safe_size,
            self.context,
        )
        if result.state != lib.DENSITY_STATE_OK:
            raise ValueError(format_state(result.state))
        self.c_state = result.state
        return ffi.unpack(out, result.bytesWritten)

    def __del__(self):
        lib.density_free_context(self.context, lib.free)


def compress(data: bytes, algorithm: Algorithm) -> bytes:
    if not isinstance(algorithm, Algorithm):
        raise ValueError("algorithm should be an instance of Algorithm")
    v = algorithm.value
    text_length = len(data)
    compress_safe_size = lib.density_compress_safe_size(text_length)
    out = ffi.new(f"char[{compress_safe_size}]")
    result = lib.density_compress(
        ffi.cast("uint8_t*", ffi.from_buffer(data)),
        text_length,
        ffi.cast("uint8_t*", out),
        compress_safe_size,
        v,
    )
    if result.state != lib.DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return ffi.unpack(out, result.bytesWritten)


def compress_into(data: bytes, out: bytearray, algorithm: Algorithm) -> int:
    if not isinstance(algorithm, Algorithm):
        raise ValueError("algorithm should be an instance of Algorithm")
    v = algorithm.value
    text_length = len(data)
    result = lib.density_compress(
        ffi.cast("uint8_t*", ffi.from_buffer(data)),
        text_length,
        ffi.cast("uint8_t*", ffi.from_buffer(out)),
        len(out),
        v,
    )
    if result.state != lib.DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return result.bytesWritten


def decompress(data: bytes, decompress_safe_size: int) -> bytes:
    text_length = len(data)
    out = ffi.new(f"char[{decompress_safe_size}]")
    result = lib.density_decompress(
        ffi.cast("uint8_t*", ffi.from_buffer(data)),
        text_length,
        ffi.cast("uint8_t*", out),
        decompress_safe_size,
    )
    if result.state != lib.DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return ffi.unpack(out, result.bytesWritten)


def decompress_into(data: bytes, out: bytearray) -> int:
    text_length = len(data)

    result = lib.density_decompress(
        ffi.cast("uint8_t*", ffi.from_buffer(data)),
        text_length,
        ffi.cast("uint8_t*", ffi.from_buffer(out)),
        len(out),
    )
    if result.state != lib.DENSITY_STATE_OK:
        raise ValueError(format_state(result.state))
    return result.bytesWritten
