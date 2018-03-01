# derived from Apache 2.0 licensed https://github.com/opendatacube/datacube-core/blob/develop/setup.py

import versioneer
from setuptools import setup, find_packages

print(list(find_packages(exclude=('test', 'test/.*'))))

tests_require = [
    'pytest',
    'datacube',
    'numpy',
    'pandas',
    'rasterio',
    'xarray']

extras_require = {
    'doc': ['Sphinx',
            'setuptools',
            'sphinx_rtd_theme>=0.2.5'],
    'test': tests_require
}
# An 'all' option, following ipython naming conventions.
extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

setup(
    name='datacube_query',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    python_requires='>=3.5.2',

    url='https://github.com/lpinner/datacube_query',
    author='Luke Pinner',
    maintainer='Luke Pinner',
    maintainer_email='',
    description='A QGIS 3 processing plugin to query and return data from an Open Data Cube instance',
    long_description=open('README.rst').read(),
    license='Apache License 2.0',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],

    # package_dir={'': 'src'},

    packages=find_packages(
        exclude=('test', 'test/.*')
    ),
    package_data={
        'datacube_query': ['help', 'help/*.*', 'help/*/*.*'],
        'datacube_query': ['i18n', 'i18n/*.*'],
        'datacube_query': ['icons', 'icons/*.*'],
        'datacube_query.ui': ['*.ui'],
        },
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'datacube',
        'dask[array]',
        'numpy',
        'pandas',
        'rasterio>=0.9a10',  # required for zip reading, 0.9 gets around 1.0a ordering problems
        'xarray>=0.9',  # >0.9 fixes most problems with `crs` attributes being lost
   ],

    extras_require=extras_require,
    tests_require=tests_require,
)