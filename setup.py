import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.readlines()

setuptools.setup(
    name="dictus",
    version="0.1.0",
    author="Zachary Silver",
    author_email="zsilver96@gmail.com",
    description="A package to generate html dictionaries from markdown files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zsilver1/dictus",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["dictus = dictus.dictus:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires=">=3.7",
)
