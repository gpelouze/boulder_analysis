## Usage

### Scraper

~~~python
usage: scrape_boulders.py [-h] [--output OUTPUT] [--overwrite] [--append] url

Scrape boulders page.

positional arguments:
  url                   address of the page to scrape

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        yaml file where the results are saved
  --overwrite           overwrite the output file if it exists
  --append, -a          append to the output file if it exists
~~~

## Dependencies

**Required:**

- PyQt5 with QtWebEngine support (`pacman -S python-pyqtwebengine` on Arch Linux)
- [PyYAML](https://github.com/yaml/pyyaml) (`pip install PyYAML`, or `pacman -S
  python-yaml` on Arch Linux)

**Optional:**

- [fake-useragent](https://github.com/hellysmile/fake-useragent) (`pip install
  fake-useragent`)


## License

Copyright (c) 2019 Gabriel Pelouze

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
