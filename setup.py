from setuptools import setup, find_packages


setup(
    name="bowser",
    description="bowser",
    packages=find_packages(),
    # entry_points={
    #     "console_scripts": [
    #         "pfbrowser = pfbrowser:cli",
    #     ]
    # },
    install_requires=[
        "selenium==4.27.1",
    ],
)
