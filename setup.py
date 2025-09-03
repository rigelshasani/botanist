from setuptools import setup

setup(
    name="botanist",
    version="0.1.1",
    description="CLI time tracker that grows an ASCII garden",
    author="Rigels Hasani",
    packages=["botanist_pkg"],
    py_modules=["botanist"],
    entry_points={
        "console_scripts": [
            "botanist=botanist_pkg.cli:main",
        ],
    },
    license="MIT",
    python_requires=">=3.7",
    project_urls = {
    "Homepage": "https://github.com/rigelshasani/botanist",
    "Source": "https://github.com/rigelshasani/botanist",
    "Issues": "https://github.com/rigelshasani/botanist/issues",
}
)
