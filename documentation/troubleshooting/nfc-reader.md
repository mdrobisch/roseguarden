# ACR122U

## Install on Windows

### Install Swig for Windows

* download swigwin under http://www.swig.org/download.html
* For example in version swigwin-3.0.12
* Add directory of swigwin to Path system-varaiable
* e.g. 'E:\Programs\swigwin-3.0.12'

### Install Pyscard using pip

* pip install pyscard

### Test under Windows

* got to app/drivers/authentifiction-directory
* run acr122u_test.py

## Install on Raspberry Pi


### Install swig
* sudo apt-get install swig

### Compile and install libnfc
* wget https://github.com/nfc-tools/libnfc/releases/download/libnfc-1.7.0-rc7/libnfc-1.7.0-rc7.tar.gz
* tar -xvzf libnfc-1.7.0-rc7.tar.gz
* cd libnfc-1.7.0-rc7
* ./configure --with-drivers=acr122_usb
* make
* sudo make install

'sudo nfc-list' should no through an error "nfc-list: error while loading shared libraries: libnfc.so.4”. There are missing links for usr-libs. To fix it, do:

* sudo sh -c "echo /usr/local/lib > /etc/ld.so.conf.d/usr-local-lib.conf"
* sudo ldconfig

'sudo nfc-list' should no through "Unable to claim USB interface". It's because libnfc double init drivers. Fix it by excluding them:

* sudo nano /etc/modprobe.d/blacklist-libnfc.conf
* add the following lines
<pre>
  blacklist pn533
  blacklist nfc
</pre>
* sudo modprobe -r pn533 nfc (to remove the included drivers )

### Install pyscard
* pip intall pyscard

### Missing packages
Some of the following packages might be missing

* autoconf
* debhelper
* flex
* libusb-dev
* libpcsclite-dev
* libpcsclite1
* libccid
* pcscd
* pcsc-tools
* libpcsc-perl
* libusb-1.0-0-dev
* libtool
* libssl-dev
* cmake
* checkinstall

# Links

* http://nfc-tools.org/index.php?title=Libnfc#Debian_.2F_Ubuntu
* https://oneguyoneblog.com/2015/09/16/acr122u-nfc-usb-reader-raspberry-pi/