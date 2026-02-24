from setuptools import setup, find_packages

setup(
    name="kivai_sdk",
    version="0.1.4",
    description="KIVAI SDK + reference gateway for validating and executing KIVAI intents",
    author="Tech4Life & Beyond LLC",
    license="Tech4Life Open Impact License (TOIL) v1.0",
    packages=find_packages(),
    package_data={
        # Packaged schema (fixes previous broken path)
        "kivai_sdk": ["schema/*.json"],
    },
    install_requires=[
        "jsonschema",
    ],
    entry_points={
        "console_scripts": [
            "kivai=kivai_sdk.cli:main",
        ],
    },
    keywords=["kivai", "intent", "validator", "jsonschema", "iot", "gateway"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
    ],
)
