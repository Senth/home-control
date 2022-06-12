from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

project_slug = "home-control"

setup(
    name=project_slug,
    version="2.0.2",
    url="https://github.com/Senth/home-control",
    license="MIT",
    author="Matteus Magnusson",
    author_email="senth.wallace@gmail.com",
    description="Personal python script to automate various home devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={"console_scripts": [f"{project_slug}=homecontrol.__main__:main"]},
    include_package_data=True,
    data_files=[("config", [f"config/{project_slug}-example.cfg"])],
    install_requires=[
        "apscheduler",
        "blulib",
        "requests",
        "pyunifi",
        "flask",
        "tealprint",
    ],
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
