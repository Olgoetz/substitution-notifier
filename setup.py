from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='substitution-notifier',
    version='1.0',
    packages=find_packages(),
    package_data={'': ['creds/*.json', 'templates/*.html']},
    install_requires=required,
    entry_points='''
        [console_scripts]
        substitution-notifier=src.main:cli
    ''',
)