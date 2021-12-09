pkgname = "grub"
pkgver = "2.06"
pkgrel = 0
configure_args = [
    "--sysconfdir=/etc", "--prefix=/usr", "--libdir=/usr/lib",
    "--sbindir=/usr/bin", "--disable-werror", "--enable-device-mapper",
    "--enable-cache-stats", "--enable-nls", "--enable-grub-mkfont",
    "--enable-grub-mount",
]
make_cmd = "gmake"
# our strip wrapper prevents correct kernel.img generation
make_install_env = {"CBUILD_BYPASS_STRIP_WRAPPER": "1"}
hostmakedepends = [
    "gmake", "pkgconf", "flex", "bison", "help2man", "python",
    "gettext-tiny", "font-unifont-bdf", f"binutils-{self.profile().arch}",
]
makedepends = [
    "gettext-tiny-devel", "freetype-devel", "ncurses-devel", "liblzma-devel",
    "device-mapper-devel", "fuse-devel",
]
depends = ["os-prober"]
pkgdesc = "GNU GRUB (version 2)"
maintainer = "q66 <q66@chimera-linux.org>"
license = "GPL-3.0-or-later"
url = "https://www.gnu.org/software/grub"
source = f"$(GNU_SITE)/{pkgname}/{pkgname}-{pkgver}.tar.xz"
sha256 = "b79ea44af91b93d17cd3fe80bdae6ed43770678a9a5ae192ccea803ebb657ee1"
# the freestanding bits
nopie_files = ["usr/lib/grub/*"]
# we carry low level freestanding stuff
options = ["foreignelf"]

exec_wrappers = []
# fool the build system into using binutils for these tools
for tool in ["objcopy", "strip", "ar", "ranlib", "nm"]:
    tpl = self.profile().triplet
    exec_wrappers += [
        (f"/usr/bin/{tpl}-g{tool}", f"{tpl}-{tool}"),
    ]

# we can use this as simple conditions
_have_x86 = False
_have_arm64 = False
_have_ppc = False
_have_rv64 = False
# all platforms
_platforms = []

match self.profile().arch:
    case "x86_64":
        _have_x86 = True
    case "ppc64le" | "ppc64":
        _have_ppc = True
    case "aarch64":
        _have_arm64 = True
    case "rsicv64":
        _have_rv64 = True

if _have_x86:
    # the default build is BIOS, we also want EFI
    # (32 and 64 bit) as well as coreboot and Xen
    _platforms = [
        ("i386", "pc"),
        ("i386", "efi"),
        ("i386", "coreboot"),
        ("x86_64", "efi"),
        ("x86_64", "xen"),
    ]
elif _have_ppc:
    _platforms = [
        ("powerpc", "ieee1275"),
    ]
elif _have_arm64:
    _platforms = [
        ("arm64", "efi"),
    ]
elif _have_rv64:
    _platforms = [
        ("riscv64", "efi"),
    ]
else:
    broken = f"Unsupported platform ({self.profile().arch})"

def init_configure(self):
    from cbuild.util import make
    self.make = make.Make(self)

def do_configure(self):
    # configure tools build
    self.mkdir("build")
    self.do(
        self.chroot_cwd / "configure", f"--host={self.profile().triplet}",
        f"--with-platform=none", *configure_args,
        wrksrc = "build"
    )
    # platforms build
    for arch, platform in _platforms:
        bdir = f"build_{arch}_{platform}"
        self.mkdir(bdir)
        cfl = "-fno-stack-protector -no-integrated-as"
        ldfl = ""
        # otherwise broken grubcore is built
        if arch == "powerpc":
            cfl += " -mno-altivec"
        # configure freestanding
        self.do(
            self.chroot_cwd / "configure", f"--host={self.profile().triplet}",
            f"--target={arch}", f"--with-platform={platform}",
            "--disable-efiemu", *configure_args,
            wrksrc = bdir, env = {
                "BUILD_CFLAGS": cfl,
                "BUILD_LDFLAGS": ldfl,
                "CFLAGS": cfl,
                "LDFLAGS": ldfl
            }
        )

def do_build(self):
    # primary build
    self.make.build(wrksrc = "build")
    # extra targets
    for arch, platform in _platforms:
        self.make.build(wrksrc = f"build_{arch}_{platform}")

def do_install(self):
    # populate extra targets first
    for arch, platform in _platforms:
        bdir = f"build_{arch}_{platform}"
        # full install
        self.make.install(wrksrc = bdir)
        # remove stuff that is not platform specific
        for d in ["etc", "usr/share", "usr/bin"]:
            self.rm(self.destdir / d, recursive = True, force = True)
    # install tools last
    self.make.install(wrksrc = "build")
    # remove fat module files
    for d in (self.destdir / "usr/lib/grub").iterdir():
        for f in d.glob("*.module"):
            f.unlink()

def post_install(self):
    # kernel hook
    self.install_file(
        self.files_path / "99-grub.sh", "etc/kernel.d", mode = 0o755
    )
    # conf file
    self.install_file(
        self.files_path / "grub.default", "etc/default", name = "grub"
    )
    # update-grub
    with open(self.destdir / "usr/bin/update-grub", "w") as ug:
        ug.write("""#!/bin/sh

exec /usr/bin/grub-mkconfig -o /boot/grub/grub.cfg
""")
    (self.destdir / "usr/bin/update-grub").chmod(0o755)
    # move completions
    self.install_dir("usr/share/bash-completion/completions")
    self.mv(
        self.destdir / "etc/bash_completion.d/grub",
        self.destdir / "usr/share/bash-completion/completions"
    )
    # unused tools
    self.rm(self.destdir / "usr/bin/grub-ofpathname")
    self.rm(self.destdir / "usr/bin/grub-sparc64-setup")

@subpackage("grub-utils")
def _utils(self):
    self.pkgdesc = f"{pkgdesc} (additional utilities)"
    self.depends = [f"{pkgname}={pkgver}-r{pkgrel}"]

    return [
        "usr/bin/grub-menulst2cfg",
        "usr/bin/grub-fstest",
        "usr/bin/grub-mkfont",
    ]

@subpackage("grub-i386-coreboot", _have_x86)
def _i386_coreboot(self):
    self.pkgdesc = f"{pkgdesc} (i386 coreboot support)"
    self.depends = [f"{pkgname}={pkgver}-r{pkgrel}"]

    return ["usr/lib/grub/i386-coreboot"]

@subpackage("grub-i386-pc", _have_x86)
def _i386_pc(self):
    self.pkgdesc = f"{pkgdesc} (i386 PC/BIOS support)"
    self.depends = [f"{pkgname}={pkgver}-r{pkgrel}"]

    return ["usr/lib/grub/i386-pc"]

@subpackage("grub-x86_64-efi", _have_x86)
def _x86_64_efi(self):
    self.pkgdesc = f"{pkgdesc} (x86_64 EFI support)"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}", "dosfstools", "efibootmgr"
    ]

    return ["usr/lib/grub/x86_64-efi"]

@subpackage("grub-x86_64-xen", _have_x86)
def _x86_64_xen(self):
    self.pkgdesc = f"{pkgdesc} (x86_64 Xen PV support)"
    self.depends = [f"{pkgname}={pkgver}-r{pkgrel}"]

    return ["usr/lib/grub/x86_64-xen"]

@subpackage("grub-i386-efi", _have_x86)
def _i386_efi(self):
    self.pkgdesc = f"{pkgdesc} (i386 EFI support)"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}", "dosfstools", "efibootmgr"
    ]

    return ["usr/lib/grub/i386-efi"]

@subpackage("grub-arm64-efi", _have_arm64)
def _arm64_efi(self):
    self.pkgdesc = f"{pkgdesc} (AArch64 EFI support)"
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}", "dosfstools", "efibootmgr"
    ]

    return ["usr/lib/grub/arm64-efi"]

@subpackage("grub-powerpc-ieee1275", _have_ppc)
def _ppc(self):
    self.pkgdesc = f"{pkgdesc} (PowerPC OpenFirmware support)"
    self.depends = [f"{pkgname}={pkgver}-r{pkgrel}", "powerpc-utils"]

    return ["usr/lib/grub/powerpc-ieee1275"]
