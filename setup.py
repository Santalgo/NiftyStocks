from setuptools import setup, find_packages

setup(
    name="nse_fno_scanner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance",
        "pandas",
        "numpy",
        "tqdm",
    ],
    entry_points={
        "console_scripts": ["nse-fno-scan=run_scan:main"],
    },
    python_requires=">=3.8",
)
