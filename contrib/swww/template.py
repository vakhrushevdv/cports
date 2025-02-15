pkgname = "swww"
pkgver = "0.8.1"
pkgrel = 1
build_style = "cargo"
hostmakedepends = ["cargo"]
makedepends = ["rust-std"]
pkgdesc = "Solution to your Wayland Wallpaper Woes"
maintainer = "Froggo <froggo8311@proton.me>"
license = "GPL-3.0-only"
url = "https://github.com/Horus645/swww"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "7612ae780d0aa86b772d1e224346137d490eba48e158033185d52649ff01b757"


def post_install(self):
    self.install_bin(f"target/{self.profile().triplet}/release/swww-daemon")
