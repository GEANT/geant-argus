from setuptools import setup, find_packages

setup(
    name="geant_argus",
    version="0.27",
    author="GEANT",
    author_email="swd@geant.org",
    description="Dashboard V3 framework",
    url="https://github.com/GEANT/geant-argus",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=("tests",)),
    install_requires=[
        "Django>=4.2.11,<5.1",
        "argus-server[htmx]",
        "django-widget-tweaks",
    ],
    extras_require={
        "prod": [
            "gunicorn",
            "uvicorn",
        ],
        "dev": [
            "black",
            "coverage",
            "django-extensions",
            "djlint",
            "flake8",
            "pytest",
            "pytest-django",
            "pytest-docker",
            "python-dotenv",
            "PyYAML",
        ],
    },
    include_package_data=True,
    license="MIT",
    license_files=("LICENSE.txt",),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
