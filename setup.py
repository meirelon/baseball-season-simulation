import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mlb-standings-simulation", # Replace with your own username
    version="0.0.1",
    author="Michael Nestel",
    author_email="nestelm@gmail.com",
    description="A small package to simulate MLB season standings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meirelon/baseball-season-simulation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
