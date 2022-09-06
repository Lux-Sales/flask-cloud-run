from uuid import uuid1


def generate_uuid() -> int:
    return uuid1().int >> 100
