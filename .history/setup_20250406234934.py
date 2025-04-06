from setuptools import setup, find_packages

setup(
    name="layout_designer_toolbox",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'layout-designer=layout_designer_toolbox.main:main',
        ],
    },
    author="Your Name",
    author_email="nikolasdrummond.com",
    description="A lightweight toolbox for designing scientific figure layouts with Tkinter.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/layout_designer_toolbox",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
