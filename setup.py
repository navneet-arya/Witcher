try:
	from setuptools import setup
except ImportError:
	from disutils.core import setup

from codecs import open
import sys

if sys.version_info[:3] < (3,0,0):
	print("Requires Python 3 to run.")
	sys.exit(1)

# with open("README.md", encoding='utf-8') as file:
# 	readme = file.read()

setup(
	name="boomerang-cli",
	version="1.0.0",
	description="Command line tool that automatically fetches Stack Overflow after complier error.",
	url="https://github.com/navneet-arya/Boomerang",
	author="narya",
	author_email="navneet.arya1994@gmail.com",
	classifiers=[
		"Environment :: Console",
		"Intended Audience :: Developers",
		"Natural Language :: English",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3",
	],
	keywords = "stackoverflow stack overflow debug debugging error-handling compile errors error message cli search commandline",
	include_package_data =True,
	packages = ["src"],
	entry_points={"console_scripts":["src = src.boomerang:main"]},
	install_requires = ["BeautifulSoup4", "requests", "urllib3", "urwid"],
	requires=["BeautifulSoup4", "requests", "urllib3", "urwid"],
	python_requires= ">= 3",
	license="MIT"
	)