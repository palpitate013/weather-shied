#!/usr/bin/env python3
"""Setup configuration for Weather Shield."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="weather-shield",
    version="1.0.0",
    author="Weather Shield Contributors",
    author_email="dev@weather-shield.io",
    description="Real-time weather monitoring and computer control system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/palpitate013/weather-shield",
    project_urls={
        "Bug Tracker": "https://github.com/palpitate013/weather-shield/issues",
        "Documentation": "https://github.com/palpitate013/weather-shield",
        "Source Code": "https://github.com/palpitate013/weather-shield",
    },
    py_modules=["weather_shield"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Power (UPS)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "weather-shield=weather_shield:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
