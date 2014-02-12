# -*- coding: utf-8 -*-
import random
import hashlib


def get_hash():
    return hashlib.sha224(
        str(random.getrandbits(256)).encode('utf-8')).hexdigest()[:40]


def is_password_valid(password):
    if not password:
        return False, "Password can't be empty."
    if len(password) <= 5:
        return False, "Need at least 6 characters for your password."
    if not any(char.isalpha() for char in password):
        return False, "Need at least one alpha character in password."
    if not any(char.isdigit() for char in password):
        return False, "Need at least one numerical character in password."
    return True, None
