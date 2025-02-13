from setuptools import setup, find_packages

setup(
    name="keymouse-visualizer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PySide6==6.6.1",
        "pynput==1.7.6",
        "keyboard==0.13.5",
        "mouse==0.7.1",
        "qt-material==2.14",
        "pillow==10.2.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.4",
            "black==24.1.1",
            "flake8==7.0.0",
            "mypy==1.8.0",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "keymouse=src.main:main",
        ],
    },
) 