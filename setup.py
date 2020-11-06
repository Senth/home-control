from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="home-control",
    version="2.0.1",
    url="https://github.com/Senth/home-control",
    license="MIT",
    author="Matteus Magnusson",
    author_email="senth.wallace@gmail.com",
    description="Personal python script to automate various home devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["homecontrol"],
    entry_points={"console_scripts": ["home-control=homecontrol.__main__:main"]},
    include_package_data=True,
    data_files=[("config/home-control", ["config/config.example.py"])],
    install_requires=["apscheduler", "requests", "pytradfri", "pyunifi", "suntime"],
    classifiers=[
        "Licence :: OSI Approved :: MIT Licence" "Programming Language :: Python :: 3"
    ],
    python_requires=">=3.8",
)
