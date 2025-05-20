from setuptools import setup, find_packages
import sys

# Core dependencies that are safe to install on all platforms
install_requires = [
    'streamlit>=1.32.0,<2.0.0',
    'python-docx>=1.1.2,<2.0.0',
    'requests>=2.31.0,<3.0.0',
    'python-box>=7.1.1,<8.0.0',
    'python-dateutil>=2.9.0,<3.0.0',
    'pytz>=2024.1,<2025.0',
    'boxsdk>=3.14.0,<4.0.0',
    'python-jose>=3.3.0,<4.0.0',
    'cryptography>=42.0.5,<43.0.0',
    'PyJWT>=2.8.0,<3.0.0',
    'openai>=1.12.0,<2.0.0',
    'pandas>=2.2.1,<3.0.0',
    'numpy>=1.26.4,<2.0.0'
]

# Platform-specific dependencies
if sys.platform != 'win32':
    install_requires.append('tiktoken>=0.5.2,<0.6.0')

setup(
    name="conga_to_box_converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.8,<3.11",  # Strictly limit to Python 3.8-3.10 for better compatibility
    entry_points={
        "console_scripts": [
            "conga-to-box=app.app:main",
        ],
    },
    include_package_data=True,
)
