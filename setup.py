from setuptools import setup, find_packages

setup(
    name="ghopper",
    version="0.1.0",  # Update to a more explicit version number
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'ghopper=ghopper.cli:cli',  # Ensure that 'cli' is correctly located in ghopper/cli.py
        ],
    },
    author="Suman Khadka",  # Replace with your actual name or handle
    author_email="khadkasuman324@gmail.com",  # Optional but recommended
    description="CLI tool to open GitHub repos and PRs quickly",
    long_description="A command-line tool to open GitHub repositories and PRs with ease. Manage multiple repos, add branches, and more.",
    long_description_content_type="text/markdown",  # You can use markdown for your long description
    url="https://github.com/sumann7916/ghopper",  # Update with your actual project URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Specify the minimum Python version required
)
