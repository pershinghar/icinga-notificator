from setuptools import setup, find_packages
import sys

#
#
with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_reqs = fh.read().split()

setup(
    name="icinga_notificator",
    version="2.0.15",
    packages=[
        "icinga_notificator",
        "icinga_notificator.base",
        "icinga_notificator.functions",
        "icinga_notificator.classes",
        "icinga_notificator.utils",
    ],
    license="GPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ls-tech-team/monitoring/icinga/icinga-notificator",
    classifiers=["Programming language :: Python :: 3", "Operating System :: Linux"],
    setup_requires=["pytest-runner"],
    include_package_data=True,
    tests_require=["pytest", "mock", "paramiko==2.6.0", "elasticsearch==7.0.2"],
    test_suite="tests",
    install_requires=install_reqs,
    scripts=["icinga_notificator/scripts/icinga-notificator.py"],
)
