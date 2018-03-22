"""Set of internal exceptions"""


class ZephyrLixWebError(Exception):
    """Base error for Rest.li Python Internal project."""

    def __init__(self, *args, **kwargs):
        super(ZephyrLixWebError, self).__init__(*args, **kwargs)


class LixNotFoundError(ZephyrLixWebError):
    """Lix Not found through Lix API"""
