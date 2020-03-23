import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csv2libsvm", # Replace with your own username
    version="0.0.1",
    author="Eric E. Graves",
    author_email="gravcon5@gmail.com",
    description="Convert csv files to libsvm format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zelazny7/csv2libsvm.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)