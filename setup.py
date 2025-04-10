from setuptools import setup, find_packages

setup(
    name='yophonepy',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
    ],
    author='David Kocharyan',
    author_email='davidkocharyan94@gmail.com',
    description='A synchronous Python library for interacting with the YoPhone API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/david-kocharyan/yophonepy',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
    ],
    keywords='yophone, yophonepy, api, synchronous, messaging',
    python_requires='>=3.7',
    project_urls={
        'Bug Tracker': 'https://github.com/david-kocharyan/yophonepy/issues',
        'Source Code': 'https://github.com/david-kocharyan/yophonepy',
    },
)
