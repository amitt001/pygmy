
def make_url_from_id(_id, url_type):
    """Builds an url from the object passed."""
    url_type_mapping = dict(
        user='http://127.0.0.1:9119/api/user/{}',
        link='http://127.0.0.1:9119/api/link/{}',
        links_list='http://127.0.0.1:9119/api/user/{}/links'
    )
    return url_type_mapping.get(url_type).format(_id)