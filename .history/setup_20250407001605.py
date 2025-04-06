from setuptools import setup, find_packages

setup(
    name="axisblueprint",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'axisblueprint=axisblueprint.main:BlueprintBuilder',
        ],
    },
    author="Nik Drummond",
    author_email="nikolasdrummond@gmail.com",
    description="A toolbox for designing scientific figure layouts with Tkinter.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NikDrummond/AxisBlueprint",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # Tkinter is usually included with Python,
        # but you can list additional dependencies here.
        "ipywidgets>=7.6.0",
        "panel>=0.12.0",
        "ipython>=7.0.0",
        # Add any other required packages here
    ],
)
