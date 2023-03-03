from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in capgrid/__init__.py
from capgrid import __version__ as version

setup(
	name="capgrid",
	version=version,
	description="ERPNext Customisations for Capgrid",
	author="Capgrid Solutions",
	author_email="venkatesh@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
