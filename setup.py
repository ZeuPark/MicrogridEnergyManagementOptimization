"""Setup script for microgrid optimization package."""

from setuptools import setup, find_packages

setup(
    name="microgrid-optimization",
    version="1.0.0",
    description="Microgrid Energy Management Optimization using Linear Programming",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/MicrogridEnergyManagementOptimization",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "cvxpy>=1.4.0",
        "highspy>=1.5.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mg-ingest=scripts.ingest_data:main",
            "mg-baseline=scripts.run_baseline:main",
            "mg-optimize=scripts.run_optimization:main",
            "mg-sensitivity=scripts.run_sensitivity:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)
