import os
from setuptools import setup


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="ansible-hcv-client",
    version="0.1.0",
    author="James Riach",
    author_email="james@jriach.co.uk",
    description=("ansible-vault client script to access ansible-vault keys stored in Hashicorp Vault"),
    install_requires=[
        "fernetstring",
        "hvac",
        "tomli"
    ],
    license="",
    url="",
    packages=['ansiblehcv'],
    package_data={'ansiblehcv': ['data/default-config.toml']},
    long_description=read('README'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'ansible-hcv-client=ansiblehcv.ansible_hcv_client:main'
        ],
    },
)
