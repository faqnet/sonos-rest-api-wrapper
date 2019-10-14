from setuptools import setup

setup(
        name='sonosrestapi',
        version='0.0.4',
        description='sonos rest api wrapper',
        license='MIT',
        packages=['sonosrestapi'],
        author='Fagnet',
        author_email='robin.schoch@fhnw.ch',
        keywords=['sonos'],
        url='https://github.com/faqnet/sonos-rest-api-wrapper',
        download_url='https://github.com/faqnet/sonos-rest-api-wrapper/archive/0.0.4.tar.gz',
        install_requires=[
            'typing',
            'requests'
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
