# Copyright 2015 Joao Cardoso
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import setup, find_packages

setup(
    name='pyrcos',
    version="0.0.1",
    packages=find_packages("."),
    install_requires=[
        "biopython>=1.65",
        "jinja2>=2",
    ],
    author='Joao Cardoso',
    author_email='jooaaoo@gmail.com',
    description='Python hi-level interface for circos',
    license='Apache License Version 2.0',
    keywords='bioinformatics high-throughput',
    url='TBD',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ],
)
