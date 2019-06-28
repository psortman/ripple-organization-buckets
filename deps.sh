#!/bin/bash -e

# zipimport.ZipImportError: can't decompress data; zlib not available:
#    You may need `xcode-select --install` on OS X
#    https://github.com/pyenv/pyenv/issues/451#issuecomment-151336786
# ERROR: The Python ssl extension was not compiled. Missing the OpenSSL lib?
#    CFLAGS="-I$(brew --prefix openssl)/include" \
#    LDFLAGS="-L$(brew --prefix openssl)/lib" \
#    pyenv install 3.7.2
pyenv install -s 3.7.2
pyenv virtualenv 3.7.2 ripple_qc_gui-3.7.2 || true
pyenv local ripple_qc_gui-3.7.2
mkdir -p .cached_deps
pip install --upgrade 'pip<19'
pip install --process-dependency-links --find-links=.cached_deps/ --no-cache-dir -r requirements.txt
pip install --process-dependency-links -e .
