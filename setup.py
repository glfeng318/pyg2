from setuptools import setup

setup(
    name='pyg2',
    version='0.1',
    packages=['pyg2'],
    include_package_data=True,
    package_dir = {'': 'src'},
    install_requires=['jinja2','ipython',],
    test_suite='nose.collector',
    tests_require=['nose'],
)