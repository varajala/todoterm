from setuptools import find_packages, setup


def read_long_descrition():
    with open('README.md') as file:
        return file.read()


setup(
    name = 'todoterm',
    version = '1.0.3',
    description = 'A simple TODO command line application',
    long_description = read_long_descrition(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/varajala/todoterm",
    
    author = 'Valtteri Rajalainen',
    author_email = 'rajalainen.valtteri@gmail.com',

    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    
    python_requires = '>=3.7',
    packages = find_packages(),
)
