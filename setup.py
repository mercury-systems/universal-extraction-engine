from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Extract structured data from HTML: metadata, tables, JSON-LD, CSS selectors"

setup(
    name="universal-extraction-engine",
    version="2.0.0",
    author="MERCURY-OPS",
    description="Extract structured data from HTML: metadata, tables, JSON-LD, CSS selectors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mercury-systems/universal-extraction-engine",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27.0",
        "lxml>=5.2.0",
        "cssselect>=1.2.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0", "pytest-asyncio>=0.23"],
    },
    entry_points={
        "console_scripts": [
            "extract=extraction_engine.cli:main",
        ],
    },
)
