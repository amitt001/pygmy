from pygmy.core.hashdigest import HashDigest
from pygmy.model import LinkManager


def next_short_code():
    """Pass a long link and it returns a base62 short code."""
    link_manager = LinkManager()
    link = link_manager.latest_default_link()
    # First link
    if link is None:
        base_id = 1
        base_str = HashDigest().shorten(base_id)
    else:
        base_id = HashDigest().decode(link.short_code) + 1
        base_str = HashDigest().shorten(base_id)
        while link_manager.find(short_code=base_str):
            print(base_str)
            base_id += 1
            base_str = HashDigest().shorten(base_id)
    return base_str


def long_url_exists(long_url):
    link_manager = LinkManager()
    link = link_manager.find(long_url=long_url)
    if link is None:
        return False
    if link.is_disabled:
        return False
    return True
