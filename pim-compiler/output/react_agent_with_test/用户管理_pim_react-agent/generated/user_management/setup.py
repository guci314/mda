from setuptools import setup, find_packages

setup(
    name="user_management",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.68.0",
        "uvicorn==0.15.0",
        "sqlalchemy==1.4.22",
        "psycopg2-binary==2.9.1",
        "pydantic==1.8.2",
        "python-jose==3.3.0",
        "passlib==1.7.4",
        "pytest==7.0.1",
        "pytest-asyncio==0.15.1",
    ],
)