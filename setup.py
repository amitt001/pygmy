import setuptools

setuptools.setup(
    name            = 'pygmy',
    description     = 'Pygmy - URL Shortner',
    author          = 'amit',
    author_email    = '',
    url             = 'iamit.xyz',
    version         = '0.1',
    license         = 'GPLv3',
    keywords        = 'url',
    packages        = setuptools.find_packages('src'),
    package_dir     = {'': 'src'},
    include_package_data = True,
    install_requires ={
        'sqlalchemy'
    }
)
