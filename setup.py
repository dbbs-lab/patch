import setuptools, os, sys
import patch

with open("README.md", "r") as fh:
    long_description = fh.read()

# Collect all files recursively from the data folder
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "patch", "data"))
data_files = []
for (dirpath, dirnames, filenames) in os.walk(data_folder):
    rel_folder = os.path.relpath(dirpath, "patch")
    if len(filenames) > 0:
        data_files.append(os.path.join(rel_folder, "*"))

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
    include_package_data=True,
    package_data={"patch": data_files, "patch_extensions": [os.path.join("mod","*.mod")]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={"glia.package": ["patch_extensions = patch_extensions"]},
    install_requires=["setuptools", "nrn-glia"],
    extras_require={"dev": ["sphinx", "pre-commit", "black", "sphinxcontrib-contentui"]},
)
