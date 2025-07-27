from setuptools import setup, find_packages

setup(
    name='file-organizer',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # List any dependencies here, e.g., 'Click>=7.0'
    ],
    entry_points={
        'console_scripts': [
            'file-organizer=file_organizer.cli:main',
        ],
    },
    author='Your Name', # Replace with your name
    author_email='your.email@example.com', # Replace with your email
    description='A simple command-line tool to organize files by type.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/file-organizer', # Replace with your project URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)