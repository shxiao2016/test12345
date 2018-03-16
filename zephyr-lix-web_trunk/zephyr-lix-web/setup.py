import setuptools

from distgradle import GradleDistribution


setuptools.setup(
    distclass=GradleDistribution,
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'control = linkedin.apollo:main',
        ],
        'apollo.controllers': [
            'zephyr-lix-web = zephyrlixweb.controllers:SimpleWebAppController',
        ],
    },
)
