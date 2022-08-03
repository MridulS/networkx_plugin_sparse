from setuptools import setup
setup(
    name='networkx_plugin_sparse',
    version='0.0.1',
    entry_points={'networkx.plugins': 'sparse = networkx_plugin_sparse'},
)