import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='nrn-patch',
     version='0.0.2',
     author="Robin De Schepper",
     author_email="robingilbert.deschepper@unipv.it",
     description="A Pythonic, object-oriented, minimalistic wrapper for NEURON",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/helveg/patch",
     license='MIT',
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
     ],
     install_requires= [

     ]
 )
