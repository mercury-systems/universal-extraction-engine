from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="universal-extraction-engine",
    version="1.0.0",
    author="MERCURY-OPS",
    description="Universal web extraction engine for structured data scraping",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/mercury-systems/universal-extraction-engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="scraping extraction web-scraping data-mining",
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.9.0",
        "aiosqlite>=0.19.0",
        "httpx>=0.27.0",
        "lxml>=5.2.0",
    ],
    entry_points={
        "console_scripts": [
            "extract=main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/mercury-systems/universal-extraction-engine/issues",
        "Source": "https://github.com/mercury-systems/universal-extraction-engine",
    },
)
