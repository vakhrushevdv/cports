pkgname = "vulkan-headers"
pkgver = "1.3.277"
pkgrel = 0
build_style = "cmake"
hostmakedepends = ["cmake", "ninja"]
pkgdesc = "Vulkan header files"
maintainer = "q66 <q66@chimera-linux.org>"
license = "Apache-2.0"
url = "https://www.khronos.org/vulkan"
source = (
    f"https://github.com/KhronosGroup/Vulkan-Headers/archive/v{pkgver}.tar.gz"
)
sha256 = "33e0c000f1e9a8019e4b86106d62b64133314a13fef712390c1f0563f4920614"
# no test suite
options = ["!check"]
