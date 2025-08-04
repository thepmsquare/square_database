from setuptools import find_packages, setup

package_name = "square_database"

setup(
    name=package_name,
    version="3.2.3",
    packages=find_packages(),
    package_data={
        package_name: ["data/*", "pydantic_models/*"],
    },
    install_requires=[
        "sqlalchemy>=2.0.23",
        "uvicorn>=0.24.0.post1",
        "fastapi>=0.104.1",
        "python-multipart>=0.0.6",
        "websockets>=12.0",
        "httpx>=0.26.0",
        "square_logger>=2.0.0",
        "square_commons>=2.1.0",
        "pydantic>=2.9.2",
    ],
    extras_require={
        "all": [
            "square_database_structure>=2.5.9",
            "pytest>=8.0.0",
            "pytest-cov>=6.2.1",
        ],
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=6.2.1",
        ],
        "square": [
            "square_database_structure>=2.5.9",
        ],
    },
    author="thePmSquare",
    author_email="thepmsquare@gmail.com",
    description="database layer for my personal server.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url=f"https://github.com/thepmsquare/{package_name}",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
