import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='epftools',
    author='gaurav meena',
    author_email='gauravmeena0708@gmail.com',
    description='epftools (Python Package Index) Package',
    keywords='example, pypi, package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gauravmeena0708/epftools',
    project_urls={
        'Documentation': 'https://github.com/gauravmeena0708/epftools',
        'Bug Reports': 'https://github.com/gauravmeena0708/epftools/issues',
        'Source Code': 'https://github.com/gauravmeena0708/epftools',
        # 'Funding': '',
        # 'Say Thanks!': '',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas>=1.3.0',
        'numpy>=1.20.0',
        'reportlab>=3.6.0',
        'pdfkit>=1.0.0',
        'PyPDF2>=2.0.0',
        'beautifulsoup4>=4.9.0',
        'plotly>=5.0.0',
        'requests>=2.31.0',
        'python-docx>=1.0.0',
        'xlsxwriter>=3.1.0',
        'openpyxl>=3.1.0',
        'xlrd>=2.0.1',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'ocr': ['pytesseract>=0.3.8', 'pdf2image>=1.16.0', 'Pillow>=8.0.0'],
        'ml': ['scikit-learn>=1.0.0'],
    },

)
