from setuptools import setup


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='m1_api_wrapper',
    version='2.1.2',
    description='M1 RetroScore API Wrapper',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Molecule.one',
    author_email='support@molecule.one',
    url='https://github.com/molecule-one/m1wrapper-python',
    license=license,
    packages=['m1wrapper'],
    install_requires=[
        'requests==2.28.2',
        'urllib3==1.25.11'
    ] 
)

