from setuptools import setup, find_packages

setup(
    name="conga_to_box_converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.32.0',
        'python-docx>=1.1.2',
        'requests>=2.31.0',
        'python-box>=7.1.1',
        'python-dateutil>=2.9.0',
        'pytz>=2024.1',
        'boxsdk>=3.14.0',
        'python-jose>=3.3.0',
        'cryptography>=42.0.5',
        'PyJWT>=2.8.0',
        'openai>=1.12.0',
        'tiktoken>=0.5.2',
        'pandas>=2.2.1',
        'numpy>=1.26.4',
    ],
    python_requires='>=3.8',
)
