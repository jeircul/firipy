# Firi API wrapper

[![Upload Python Package](https://github.com/jeircul/firipy/actions/workflows/publish.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/publish.yml)
[![PyPi Version](https://img.shields.io/pypi/v/firipy.svg)](https://pypi.python.org/jeircul/firipy/)
![GitHub](https://img.shields.io/github/license/jeircul/firipy)

Python3 wrapper around the [Firi Trading API (1.0.0)](https://developers.firi.com/)

## 📦 Installation
PyPI
```pip
pip install -U firipy
```

## 🚀 Usage

**API Key** from firi.no is required:
```python
from firipy import FiriAPI

firi = FiriAPI(token='YOUR_API_KEY')
print(firi.balance())
```
