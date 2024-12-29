from setuptools import setup, find_packages
import os

# Read the contents of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="dst-server-manager",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "PyYAML>=6.0.1",
        "customtkinter>=5.2.0",
        "pillow>=10.0.0",  # Required by customtkinter
    ],
    entry_points={
        "console_scripts": [
            "dst-server=dst_server_manager.cli:main",
            "dst-server-gui=dst_server_manager.gui:main"
        ],
    },
    author="Marcos",
    author_email="your.email@example.com",  # Add your email
    description="A GUI tool for managing Don't Starve Together dedicated servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["don't starve together", "dst", "server", "manager", "gui", "game server"],
    url="https://github.com/yourusername/dst-server-manager",  # Update with your repo
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dst-server-manager/issues",
        "Documentation": "https://github.com/yourusername/dst-server-manager#readme",
        "Source Code": "https://github.com/yourusername/dst-server-manager",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
