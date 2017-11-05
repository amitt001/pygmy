from pygmy.config import config

def make_url_from_id(_id, url_type):
    """Builds an url from the object passed."""
    base_url = config.webservice_url
    url_type_mapping = dict(
        user=base_url + '/api/user/{}',
        link=base_url + '/api/link/{}',
        links_list=base_url + '/api/user/{}/links'
    )
    return url_type_mapping.get(url_type).format(_id)