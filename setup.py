"""Setup configuration for SuperAgent AI Framework."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="superagent-ai",
    version="1.0.0",
    author="SuperAgent Team",
    description="Advanced AI agent framework for autonomous software development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/superagent",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "anthropic>=0.25.0",
        "langchain>=0.1.20",
        "langchain-anthropic>=0.1.11",
        "aiohttp>=3.9.5",
        "redis>=5.0.4",
        "click>=8.1.7",
        "rich>=13.7.1",
        "fastapi>=0.111.0",
        "uvicorn>=0.30.0",
        "pydantic>=2.7.2",
        "GitPython>=3.1.43",
        "pytest>=8.2.1",
        "structlog>=24.2.0",
    ],
    entry_points={
        "console_scripts": [
            "superagent=superagent.cli:main",
        ],
    },
)





