# -*- coding: utf-8 -*-
import random
import hashlib


def get_hash():
    return hashlib.sha224(
        str(random.getrandbits(256)).encode('utf-8')).hexdigest()[:40]
