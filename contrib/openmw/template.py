pkgname = "openmw"
pkgver = "0.48.0"
pkgrel = 0
build_style = "cmake"
configure_args = [
    # enable once we have proper qt6 support (0.49)
    "-DBUILD_OPENCS=OFF",
    "-DUSE_LUAJIT=OFF",
    "-DOPENMW_USE_SYSTEM_BULLET=OFF",
    "-DOPENMW_USE_SYSTEM_YAML_CPP=OFF",
    "-DOPENMW_LTO_BUILD=ON",
]
hostmakedepends = ["cmake", "ninja", "pkgconf", "qt6-qttools", "qt6-qtbase"]
makedepends = [
    "sdl-devel",
    "boost-devel",
    "ffmpeg-devel",
    "mygui-devel",
    "liblz4-devel",
    "openscenegraph-devel",
    "unshield-devel",
    "openal-soft-devel",
    "qt6-qtbase-devel",
    "lua5.1-devel",
    "libxt-devel",
]
pkgdesc = "Open implementation of Morrowind's engine"
maintainer = "q66 <q66@chimera-linux.org>"
license = "GPL-3.0-or-later"
url = "https://openmw.org"
# matches the files openmw declares in cmake
_recast_hash = "e75adf86f91eb3082220085e42dda62679f9a3ea"
_bullet_hash = "3.17"
_yaml_cpp_hash = "yaml-cpp-0.7.0"
source = [
    f"https://gitlab.com/OpenMW/{pkgname}/-/archive/{pkgname}-{pkgver}/{pkgname}-{pkgname}-{pkgver}.tar.gz",
    (
        f"https://github.com/recastnavigation/recastnavigation/archive/{_recast_hash}.zip",
        False,
    ),
    (
        f"https://github.com/bulletphysics/bullet3/archive/refs/tags/{_bullet_hash}.tar.gz",
        False,
    ),
    (
        f"https://github.com/jbeder/yaml-cpp/archive/refs/tags/{_yaml_cpp_hash}.zip",
        False,
    ),
]
sha256 = [
    "ebcc1e217479306a92036aabf6f8225a3d228759eef6255cda57fb8566b9d388",
    "d3339aaea1d81307bcac2bece176c5359ed5f8c8f9721fc360d28f82f9119253",
    "baa642c906576d4d98d041d0acb80d85dd6eff6e3c16a009b1abf1ccd2bc0a61",
    "4d5e664a7fb2d7445fc548cc8c0e1aa7b1a496540eb382d137e2cc263e6d3ef5",
]
# unit tests are off
options = ["!check"]

if self.profile().endian == "big":
    broken = "esm loader is not ready etc."


def post_extract(self):
    from cbuild.core import paths

    self.cp(paths.sources() / f"{pkgname}-{pkgver}/{_recast_hash}.zip", ".")
    self.cp(paths.sources() / f"{pkgname}-{pkgver}/{_yaml_cpp_hash}.zip", ".")
    self.cp(paths.sources() / f"{pkgname}-{pkgver}/{_bullet_hash}.tar.gz", ".")


@subpackage("esmtool")
def _esmtool(self):
    self.pkgdesc = "Tool for inspecting and extracitng Morrowind ESM files"

    return ["usr/bin/esmtool"]


@subpackage("bsatool")
def _bsatool(self):
    self.pkgdesc = "Tool for inspecting Bethesda BSA archives"

    return ["usr/bin/bsatool"]
