from setuptools import setup, find_packages
import io

setup(
    name="adaptive_alerting_detector_build",
    version="0.0.1",
    description="Adaptive Alerting Detector Build",
    long_description=io.open("README.md", encoding="utf-8").read(),
    author="Expedia Group",
    author_email="adaptive-alerting@expediagroup.com",
    url="https://github.com/ExpediaDotCom/adaptive-alerting-detector-build",
    license="Apache License 2.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=["dataclasses==0.6"],
    classifiers=["Programming Language :: Python :: 3",],
)
