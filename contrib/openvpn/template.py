pkgname = "openvpn"
pkgver = "2.6.8"
pkgrel = 0
build_style = "configure"
configure_args = [
    "--enable-strict",
    "--with-crypto-library=openssl",
    "--enable-x509-alt-username",
    "--prefix=/usr/bin",
]
make_dir = "."
hostmakedepends = [
        "automake",
        "pkgconf",
        "libtool",
        "python",
        "openssl",
        "cmocka",
]
makedepends = [
        "linux-pam-devel",
        "openssl-devel",
        "pcre2-devel",
        "lzo-devel",
        "lz4-devel",
        "libnl-devel",
        "libcap-ng-devel",
        "cmocka-devel",
]
pkgdesc = "Secure tunneling daemon"
maintainer = "Dmitriy Vakhrushev <dvakhrushev@netgate.com>"
license = "GPL-2.0-only"
url = "https://github.com/OpenVPN/openvpn"
source = f"{url}/releases/download/v{pkgver}/{pkgname}-{pkgver}.tar.gz"
sha256 = "5ede1565c8a6d880100f7f235317a7ee9eea83d5052db5547f13a9e76af7805d"
# Not available on nginx build tools
options = ["!check"]


def post_install(self):
    self.install_license("COPYRIGHT.GPL")

