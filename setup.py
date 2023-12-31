from setuptools import setup, find_packages

package_name = "square_database"

setup(
    name=package_name,
    version="0.0.2",
    packages=find_packages(),
    package_data={
        package_name: ["data/*", "pydantic_models/*"],
    },
    install_requires=[
        "sqlalchemy>=2.0.23",
        "psycopg2>=2.9.9",
        "uvicorn>=0.24.0.post1",
        "fastapi>=0.104.1",
        "python-multipart>=0.0.6",
        "square_logger~=1.0",
        "websockets>=12.0"
    ],
    extras_require={
        'all': [
            'database_structure~=0.0.1',
        ],
    },
    author="thePmSquare, Amish Palkar, Lav Sharma",
    author_email="thepmsquare@gmail.com, amishpalkar302001@gmail.com, lavsharma2016@gmail.com",
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
