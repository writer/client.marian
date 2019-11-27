import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(here, "VERSION"), encoding="utf-8") as f:
    __version__ = f.read().strip()
    with open(
        os.path.join(here, "marian_client", "version.py"), "w+", encoding="utf-8"
    ) as v:
        v.write("# CHANGES HERE HAVE NO EFFECT: ../VERSION is the source of truth\n")
        v.write(f'__version__ = "{__version__}"')


setup(
    name="marian-client",
    packages=find_packages(),
    author="Qordoba",
    author_email="melisa@qordoba.com",
    url="https://github.com/Qordobacode/client.marian",
    version=__version__,
    license="unlicensed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6.4",
    install_requires=['websocket-client==0.56.0'],
)
