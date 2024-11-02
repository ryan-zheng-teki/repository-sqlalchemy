from setuptools import setup, find_packages

setup(
    name="repository_sqlalchemy",
    version="0.1.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "sqlalchemy>=2.0.31",
    ],
    extras_require={
        "dev": [
            "pytest>=8.2.2",
            "pytest-asyncio>=0.23.7",
        ],
    },
    python_requires=">=3.8",
    author="Ryan Zheng",
    author_email="ryan.zheng.work@gmail.com",
    description="A small library to simplify SQLAlchemy usage with FastAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ryan-zheng-teki/repository_sqlalchemy",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    package_data={
        "repository_sqlalchemy": ["py.typed"],
    },
)
