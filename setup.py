from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="conga_to_box_converter",
    version="0.1.0",
    packages=find_packages(include=['app', 'app.*']),
    package_data={
        'app': ['*.py', '*.json'],
    },
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'conga-converter=app.app:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to convert Conga templates to Box DocGen format",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/conga-to-box-converter",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
