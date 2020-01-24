import setuptools
import patch

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nrn-patch",
    version=patch.__version__,
    author="Robin De Schepper",
    author_email="robingilbert.deschepper@unipv.it",
    description="A Pythonic, object-oriented, monkey patch for NEURON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/helveg/patch",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    extras_require={"dev": ["sphinx", "pre-commit", "black", "sphinxcontrib-contentui"]},
)
