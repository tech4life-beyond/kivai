from setuptools import setup, find_packages

setup(
    name="kivai_sdk",
    version="0.1.4",
    description="SDK for validating Kivai intents (schema-driven)",
    author="Tech4Life & Beyond LLC",
    license="Tech4Life Open Impact License (TOIL) v1.0",
    packages=find_packages(),
    package_data={
        # Ship schemas inside the Python package so pip installs are self-contained.
        "kivai_sdk": [
            "schema/*.json",
            "schema/legacy/*.json",
        ],
    },
    install_requires=["jsonschema"],
    entry_points={
        "console_scripts": [
            "kivai=kivai_sdk.cli:main",
        ],
    },
    keywords=["kivai", "validator", "jsonschema", "iot", "intents", "interoperability"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
    ],
)
