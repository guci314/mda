from setuptools import setup, find_packages

setup(
    name='pim-compiler',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'pimc=src.cli:main',
        ],
    },
)
