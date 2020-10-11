import setuptools, os, sys

with open("README.md", "r") as fh:
    long_description = fh.read()

# Get the version from the patch module without importing it.
with open(os.path.join(os.path.dirname(__file__), "patch", "__init__.py"), "r") as f:
    for line in f:
        if "__version__ = " in line:
            exec(line.strip())
            break

# Collect all files recursively from the data folder
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "patch", "data"))
data_files = []
for (dirpath, dirnames, filenames) in os.walk(data_folder):
    rel_folder = os.path.relpath(dirpath, "patch")
    if len(filenames) > 0:
        data_files.append(os.path.join(rel_folder, "*"))

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
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "patch": data_files,
        "patch_extensions": [os.path.join("mod", "*.mod")],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={"glia.package": ["patch_extensions = patch_extensions"]},
    install_requires=["setuptools", "nrn-glia>=0.3.7", "mpi4py", "errr>=1.0.0"],
    extras_require={"dev": ["sphinx", "pre-commit", "black>=20.8b1", "sphinxcontrib-contentui"]},
)
