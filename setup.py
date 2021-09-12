import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

EXTRA_REQUIRES = {
    "lint": ["black==21.6b0", "flake8==3.9.2", "isort==5.9.3"],
    "mypy": ["mypy==0.910", "mypy-extensions==0.4.3", "typing-extensions==3.10.0.0"],
    "test": ["pytest==6.2.4", "pytest-cov==2.12.1"],
    "prec": ["pre-commit==2.13.0", "pydocstyle==5.1.1"],
}
EXTRA_REQUIRES["devel"] = (
    EXTRA_REQUIRES["lint"] + EXTRA_REQUIRES["mypy"] + EXTRA_REQUIRES["test"] + EXTRA_REQUIRES["prec"]
)


setuptools.setup(
    name="python-degiro",
    author="Jorrick Sleijster",
    author_email="jorricks3@gmail.com",
    description="An unofficial API for the trading platform DeGiro written in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jorricks/python-degiro",
    setup_requires=["setuptools_scm"],
    packages=setuptools.find_packages(),
    install_requires=["requests>=2.0.0"],
    extras_require=EXTRA_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
