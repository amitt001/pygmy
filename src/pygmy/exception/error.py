
class PygmyExcpetion(Exception):
    """Pygmy base custom exception class."""


class LinkExpired(PygmyExcpetion):
    """Pygmy base custom exception class."""


class LinkInvalid(PygmyExcpetion):
    """Raised in case an invalid link is passed"""


class ShortURLUnavailable(PygmyExcpetion):
    """Raised when a short url already exists and a new insert comes with same
    short url."""
