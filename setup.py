"""Setup script for handover-check CLI tool."""

from setuptools import setup, find_packages

setup(
    name="handover-check",
    version="1.0.0",
    description="CLI tool for validating project delivery folders against client specifications",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["profiles/*.yaml", "profiles/_common/*.yaml"],
    },
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "PyYAML>=6.0",
        "pandas>=1.5",
        "openpyxl>=3.0",
        "PyQt5>=5.15",
    ],
    extras_require={
        "segy": ["segyio>=1.9"],
        "dev": ["pytest>=7.0", "pytest-cov", "pyinstaller>=6.0"],
    },
    entry_points={
        "console_scripts": [
            "handover-check=handover_check.cli:main",
        ],
        "gui_scripts": [
            "handover-check-gui=handover_check.gui:main",
        ],
    },
)
