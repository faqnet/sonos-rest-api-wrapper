from distutils.core import setup

setup(
        name='sonos-rest-api-wrapper',
        version='0.0.1',
        description='sonos rest api wrapper',
        license='MIT',
        packages=['sonos-rest-api-wrapper'],
        author='Robin Schoch',
        author_email='robin.schoch@fhnw.ch',
        keywords=['sonos'],
        url='https://github.com/faqnet/sonos-rest-api-wrapper',
        download_url='https://github.com/faqnet/sonos-rest-api-wrapper/archive/v01.tar.gz',
        install_requires=[
            'validators',
            'beautifulsoup4',
            'typing',
            'requests',
            'json',
            'logging'
            ],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            ],
        )
