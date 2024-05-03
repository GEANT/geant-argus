from setuptools import setup, find_packages

setup(
    name="geant_argus",
    version="0.1",
    author="GEANT",
    author_email="swd@geant.org",
    description="Dashboard V3 framework",
    url="https://github.com/GEANT/geant-argus",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=("tests",)),
    install_requires=[
        "Django>=4.2.11,<5.1",
    ],
    extras_require={
        "dev": [
            "black",
            "coverage",
            "python-dotenv",
            "django-extensions",
            "flake8",
        ]
    },
    include_package_data=True,
    license="MIT",
    license_files=("LICENSE.txt",),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
