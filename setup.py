import setuptools, os, sys

with open("README.md", "r") as fh:
    long_description = fh.read()

# Get the version from the patch module without importing it.
with open(os.path.join(os.path.dirname(__file__), "patch", "__init__.py"), "r") as f:
    for line in f:
        if "__version__ = " in line:
            exec(line.strip())
            break

setuptools.setup(
    name="nrn-patch",
    version=__version__,
    author="Robin De Schepper",
    author_email="robingilbert.deschepper@unipv.it",
    description="A Pythonic, object-oriented, monkey patch for NEURON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/helveg/patch",
    license="MIT",
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    package_data={
        "patch_extensions": [os.path.join("mod", "*.mod")],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points={"glia.package": ["patch_extensions = patch_extensions"]},
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "nrn-glia>=4.0.0a0",
        "errr>=1.2.0",
        "numpy>=1.21.0",
        "NEURON>=8.0",
    ],
    extras_require={
        "dev": [
            "sphinx",
            "pre-commit",
            "black>=22.1.0",
            "helveg--sphinx-code-tabs",
            "sphinx_rtd_theme",
        ]
    },
)
