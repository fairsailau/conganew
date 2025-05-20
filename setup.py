#!/usr/bin/env python3
from setuptools import setup, find_packages

# Core dependencies that are safe to install on all platforms
install_requires = [
    'streamlit==1.32.0',
    'python-docx==1.1.2',
    'requests==2.31.0',
    'python-box==7.1.1',
    'python-dateutil==2.9.0',
    'pytz==2024.1',
    'boxsdk==3.14.0',
    'python-jose==3.3.0',
    'cryptography==42.0.5',
    'PyJWT==2.8.0',
    'openai==1.12.0',
    'pandas==2.2.1',
    'numpy==1.26.4',
    'typing-extensions>=4.0.0',  # Required for Python < 3.10
    'importlib-metadata>=1.0.0'  # Required for Python < 3.8
]

# Make tiktoken optional
optional_deps = {
    'ai': ['tiktoken==0.5.2; python_version < "3.12" and platform_system != "Windows"']
}

setup(
    name="conga_to_box_converter",
    version="0.1.0",
    packages=find_packages(include=['app', 'app.*']),
    install_requires=install_requires,
    extras_require=optional_deps,
    python_requires=">=3.9,<3.10",
    entry_points={
        "console_scripts": [
            "conga-converter=app.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        'app': ['*.json', '*.md', '*.txt'],
    },
    zip_safe=False,
)
