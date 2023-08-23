# Firi API wrapper

[![Upload Python Package](https://github.com/jeircul/firipy/actions/workflows/publish.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/publish.yml)
[![Ruff](https://github.com/jeircul/firipy/actions/workflows/ruff.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/ruff.yml)
![PyPI - Version](https://img.shields.io/pypi/v/firipy)
![GitHub](https://img.shields.io/github/license/jeircul/firipy)

Python3 wrapper around the [Firi Trading API (1.0.0)](https://developers.firi.com/)

## 📦 Installation
PyPI
```pip
pip install -U firipy
```

## 🚀 Usage

**API Key** from [Firi](https://platform.firi.com/) is required:
```python
from firipy import FiriAPI

firi = FiriAPI(token='YOUR_API_KEY')
print(firi.balance())
```
