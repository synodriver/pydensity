<h1 align="center"><i>✨ pydensity ✨ </i></h1>

<h3 align="center">The python binding for <a href="https://github.com/k0dai/density">density</a> </h3>

[![pypi](https://img.shields.io/pypi/v/pydensity.svg)](https://pypi.org/project/pydensity/)
![python](https://img.shields.io/pypi/pyversions/pydensity)
![implementation](https://img.shields.io/pypi/implementation/pydensity)
![wheel](https://img.shields.io/pypi/wheel/pydensity)
![license](https://img.shields.io/github/license/synodriver/pydensity)
![action](https://img.shields.io/github/workflow/status/synodriver/pydensity/build%20wheel)

## 安装
```bash
pip install pydensity
```


## 使用
- encode
```python
import pydensity
origin = b"121212121212121"
size = pydensity.decompress_safe_size(len(origin))
data = pydensity.compress(origin, pydensity.Algorithm.lion)
print(pydensity.decompress(data, size))
```

## 公开函数
```python
from typing import Any
import enum

class Algorithm(enum.Enum):
    chameleon: Any
    cheetah: Any
    lion: Any

def format_state(state) -> str: ...
def major_version(): ...
def minor_version(): ...
def revision_version(): ...
def get_dictionary_size(algorithm: Algorithm): ...
def compress_safe_size(input_size: int): ...
def decompress_safe_size(input_size: int): ...

class Compressor:
    c_state: Any
    context: Any
    def __init__(self, algorithm: Algorithm, custom_dictionary: bool) -> None: ...
    @property
    def state(self): ...
    def compress(self, data: bytes) -> bytes: ...
    def __del__(self) -> None: ...

class DeCompressor:
    c_state: Any
    context: Any
    def __init__(self, data: bytes, custom_dictionary: bool) -> None: ...
    @property
    def state(self): ...
    def decompress(self, data: bytes, decompress_safe_size: int) -> bytes: ...
    def __del__(self) -> None: ...

def compress(data: bytes, algorithm: Algorithm) -> bytes: ...
def compress_into(data: bytes, out: bytearray, algorithm: Algorithm) -> int: ...
def decompress(data: bytes, decompress_safe_size: int) -> bytes: ...
def decompress_into(data: bytes, out: bytearray) -> int: ...
```

### 本机编译
```
python -m pip install setuptools wheel cython cffi
git clone https://github.com/synodriver/pydensity
cd pydensity
git submodule update --init --recursive
python setup.py bdist_wheel --use-cython --use-cffi
```

### 后端选择
默认由py实现决定，在cpython上自动选择cython后端，在pypy上自动选择cffi后端，使用```DENSITY_USE_CFFI```环境变量可以强制选择cffi