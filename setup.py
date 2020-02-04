from setuptools import setup, find_packages
import io

setup(
    name="adaptive-alerting-detector-build",
    version="0.0.1",
    description="Adaptive Alerting Detector Build",
    long_description=io.open("README.md", encoding="utf-8").read(),
    author="Expedia Group",
    author_email="adaptive-alerting@expediagroup.com",
    url="https://github.com/ExpediaDotCom/adaptive-alerting-detector-build",
    license="Apache License 2.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "attrs==19.3.0",
        "cycler==0.10.0",
        "dataclasses==0.6",
        "docopt==0.6.2",
        "kiwisolver==1.1.0",
        "matplotlib==3.1.2",
        "numpy==1.18.1",
        "pandas==0.25.3",
        "patsy==0.5.1",
        "pyparsing==2.4.6",
        "python-dateutil==2.8.1",
        "pytz==2019.3",
        "related==0.7.2",
        "scipy==1.4.1",
        "seaborn==0.9.0",
        "six==1.13.0",
        "statsmodels==0.10.2",
    ],
    classifiers=["Programming Language :: Python :: 3",],
    entry_points = {
        "console_scripts": ["adaptive-alerting=adaptive_alerting_detector_build.cli:main"],
    },
)
