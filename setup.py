# derived from Apache 2.0 licensed https://github.com/opendatacube/datacube-core/blob/develop/setup.py
import configparser
from fnmatch import fnmatch
from itertools import chain
import os
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command import build_py
import shutil

import versioneer


class BuildPluginCommand(build_py.build_py):
    """A custom command to build a simple zip archive that QGIS can install as a plugin"""

    description = 'Build QGIS Plugin zip archive'
    user_options = build_py.build_py.user_options + [
        ('plugin-dir=', None, 'path to save plugin archive'),
    ]

    def initialize_options(self):
        self.plugin_dir = None
        super().initialize_options()

    def run(self):
        super().run()
        plugin_dir = Path(self.plugin_dir).resolve()
        basename = '{}-{}'.format(self.distribution.metadata.name, self.distribution.metadata.version)
        self.mkpath(str(plugin_dir))
        self.make_archive(plugin_dir/basename, 'zip', self.build_lib)
        shutil.rmtree(self.build_lib)


def get_package_data(package, path, excludes=None):
    _excludes = ['*.py*']
    if excludes is not None:
        if isinstance(excludes, str):
            _excludes += [excludes]
        else:
            _excludes += excludes
    relative_to = package.replace('.', '/')
    for root, dirs, files in os.walk(path):
        for f in files:
            p = Path(root,f).relative_to(relative_to)
            if not any(fnmatch(p, x) for x in _excludes):
                yield str(p)  # Avoid "TypeError: 'WindowsPath' object does not support indexing" on Win


def main():

    version = versioneer.get_version()
    cmdclass = versioneer.get_cmdclass()

    config = configparser.ConfigParser()
    config.read('METADATA.in')
    config['general']['version']=version
    with open('datacube_query/metadata.txt', 'w') as metadata:
        config.write(metadata)
    shutil.copy('LICENSE', 'datacube_query/LICENSE')

    install_requires = [
        'datacube',
        'dask[array]',
        'numpy',
        'pandas',
        'rasterio>=0.9a10',  # required for zip reading, 0.9 gets around 1.0a ordering problems
        'xarray>=0.9',  # >0.9 fixes most problems with `crs` attributes being lost
    ]

    tests_require = ['pytest'] + install_requires

    extras_require = {
        'doc': ['Sphinx',
                'setuptools',
                'sphinx_rtd_theme>=0.2.5'],
        'test': tests_require
    }
    # An 'all' option, following ipython naming conventions.
    extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

    package_data = {'datacube_query':
                        chain(get_package_data('datacube_query', 'datacube_query/help', excludes='*doctree*'),
                              get_package_data('datacube_query', 'datacube_query/i18n'),
                              get_package_data('datacube_query', 'datacube_query/icons'),
                              ('LICENSE', 'metadata.txt')),
                    'datacube_query.ui':
                        get_package_data('datacube_query.ui', 'datacube_query/ui')
                    }

    cmdclass.update({'build_plugin': BuildPluginCommand})

    setup(
        name='datacube_query',
        version=version,
        cmdclass=cmdclass,
        python_requires='>=3.5.2',
        url='https://github.com/lpinner/datacube_query',
        author=config['general']['author'],
        maintainer=config['general']['author'],
        maintainer_email=config['general']['email'],
        description=config['general']['description'],
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

        packages=find_packages(
            exclude=('test', 'test/.*')
        ),

        package_data=package_data,

        setup_requires=[
            'pytest-runner'
        ],
        install_requires=install_requires,

        extras_require=extras_require,
        tests_require=tests_require,
    )
    os.unlink('datacube_query/metadata.txt')
    os.unlink('datacube_query/LICENSE')


if __name__ == '__main__':
    main()