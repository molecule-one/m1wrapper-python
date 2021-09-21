from setuptools import setup


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='m1_api_wrapper',
    version='2.0.1',
    description='Molecule One API Wrapper',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Szymon Pilkowski',
    author_email='szymon.pilkowski@molecule.one',
    url='https://github.com/molecule-one/m1wrapper-python',
    license=license,
    packages=['m1wrapper'],
    install_requires=[
        'requests'
    ] 
)

