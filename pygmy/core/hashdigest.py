#!/usr/bin/env python3

# Base-62 hash

import string
import time

_BASE = 62


class HashDigest:
    """Base base 62 hash library."""

    def __init__(self):
        self.base = string.ascii_letters + string.digits
        self.short_str = ''

    def encode(self, j):
        """Returns the repeated div mod of the number.

        :param j: int
        :return: list
        """
        if j == 0:
            return [j]
        r = []
        dividend = j
        while dividend > 0:
            dividend, remainder = divmod(dividend, _BASE)
            r.append(remainder)
        r = list(reversed(r))
        return r

    def decode(self, short_str):
        """

        :param short_str:
        :return:
        """
        # slow
        val_hash = []
        for shrt in short_str:
            val_hash.append(self.base.index(shrt))
        val_hash = list(reversed(val_hash))
        _id = 0
        for idx, val in enumerate(val_hash):
            _id += (val * (_BASE ** idx))
        return _id

    def shorten(self, i):
        """
        :param i:
        :return: str
        """
        self.short_str = ""
        encoded_list = self.encode(i)
        for val in encoded_list:
            self.short_str += self.base[val]
        return self.short_str

    def unshorten(self, s):
        """Just for shorten/unshorten naming convention."""
        return self.decode(s)


if __name__ == '__main__':
    hd = HashDigest()
    t = time.time()
    for i in range(1000):
        sh = hd.shorten(1099)
        hd.decode(sh)
