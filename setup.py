from setuptools import setup

setup(
    name="dreamtable",
    version="0.1",
    description="An infinite canvas for retro game assets.",
    url="https://github.com/vreon/dream-table",
    author="Jesse Dubay",
    author_email="jesse@jessedubay.com",
    license="MIT",
    packages=["dreamtable"],
    include_package_data=True,
    install_requires=[
        "esper==1.3",
        "raylib @ git+git://github.com/electronstudio/raylib-python-cffi.git#egg=raylib-dev",
    ],
    entry_points={"console_scripts": ["dreamtable=dreamtable.main:main"]},
    zip_safe=False,
)
