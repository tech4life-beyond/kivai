from setuptools import setup, find_packages

setup(
    name="kivai_sdk",
    version="0.1.3",
    description="SDK for validating Kivai protocol commands",
    author="Tech4Life & Beyond LLC",
    license="Tech4Life Open Impact License (TOIL) v1.0",
    packages=find_packages(),
    package_data={
        "kivai_sdk": ["schema/kivai-command.schema.json"],
    },
    install_requires=["jsonschema"],
    entry_points={
        "console_scripts": [
            "kivai=kivai_sdk.cli:main",
        ],
    },
    keywords=["kivai", "validator", "jsonschema", "iot", "commands"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
    ],
)
