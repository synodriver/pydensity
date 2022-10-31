"""
Copyright (c) 2008-2022 synodriver <synodriver@gmail.com>
"""
import sys

sys.path.append(".")
from random import randint
from unittest import TestCase

import pydensity


class TestAll(TestCase):
    def setUp(self) -> None:
        pass

    def test_encode(self):
        for i in range(10000):
            length = randint(1, 1000)
            value = bytes([randint(0, 255) for _ in range(length)])
            size = pydensity.decompress_safe_size(length)
            compressed = pydensity.compress(value, pydensity.Algorithm.lion)
            self.assertEqual(pydensity.decompress(compressed, size), value)

    def tearDown(self) -> None:
        pass

if __name__ == "__main__":
    import unittest
    unittest.main()