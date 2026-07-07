from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="big-mamba",
    version="1.0.0",
    author="Big Mamba Team",
    description="Big Mamba - The shorthand programming language. Python, but faster to type.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redhatsam09/big-mamba",
    project_urls={
        "Bug Tracker": "https://github.com/redhatsam09/big-mamba/issues",
        "Documentation": "https://github.com/redhatsam09/big-mamba#readme",
        "Source Code": "https://github.com/redhatsam09/big-mamba",
    },
    packages=find_packages(),
    py_modules=["mamba"],
    python_requires=">=3.6",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mamba=mamba:main",
            "bigmamba=mamba:main",
            "big-mamba=mamba:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Natural Language :: English",
    ],
    keywords="programming-language transpiler shorthand mamba big-mamba",
)
