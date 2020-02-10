from setuptools import setup, find_packages
from adaptive_alerting_detector_build import __version__
import io

setup(
    name="adaptive-alerting-detector-build",
    version=__version__,
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
        "docopt==0.6.2",
        "future==0.18.2",
        "kiwisolver==1.1.0",
        "matplotlib==3.1.3",
        "numpy==1.18.1",
        "pandas==1.0.0",
        "patsy==0.5.1",
        "pyparsing==2.4.6",
        "python-dateutil==2.8.1",
        "pytz==2019.3",
        "pyyaml==5.3",
        "related==0.7.2",
        "scipy==1.4.1",
        "seaborn==0.10.0",
        "six==1.14.0",
        "statsmodels==0.11.0",
    ],
    classifiers=["Programming Language :: Python :: 3",],
    entry_points={
        "console_scripts": [
            "adaptive-alerting=adaptive_alerting_detector_build.cli:console_script_entrypoint"
        ],
    },
)
