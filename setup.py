from setuptools import setup, find_packages

setup(
    name="ap-wrapper",
    version="1.1.0",
    description="AtomicParsley Wrapper - A user-friendly interface for AtomicParsley",
    author="Draeician",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ap=ap_wrapper.main:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 