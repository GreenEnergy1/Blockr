# Building Blockr installers

Blockr ships as four artifacts: `.exe` (Windows), `.dmg` (macOS), and `.deb` /
`.rpm` (Linux). PyInstaller does **not** cross-compile — each artifact has to
be built on that same OS. There's no way around this without a CI matrix
(GitHub Actions with `windows-latest` / `macos-latest` / `ubuntu-latest`
runners is the standard way to automate all three from one push).

All commands below are run **from the project root**, not from inside
`packaging/`.

---

## 1. Windows — `.exe`

**Run on:** Windows
**Requires:** Python 3.10+, pip

```powershell
python -m pip install pyinstaller PyQt6
pyinstaller packaging\windows\blockr-win.spec
```

Output: `dist\blockr.exe`

That's it — a single windowed executable, no installer wrapper needed. It
requests elevation (UAC prompt) on launch since it edits a protected system
file.

---

## 2. macOS — `.dmg`

**Run on:** macOS
**Requires:** Python 3.10+, pip, Xcode Command Line Tools (`xcode-select --install`)

Step 1 — build the `.app` bundle:

```bash
python3 -m pip install pyinstaller PyQt6
pyinstaller packaging/mac/blockr-mac.spec
```

Output: `dist/Blockr.app`

Step 2 — wrap it in a `.dmg`:

```bash
chmod +x packaging/mac/build-dmg.sh
./packaging/mac/build-dmg.sh 1.0.0
```

Output: `dist/Blockr-1.0.0.dmg`

**Gatekeeper note:** this build is unsigned. On first launch, macOS will
refuse to open it with an "unidentified developer" warning. Users can
right-click `Blockr.app` → **Open** to bypass this once, or you can clear the
quarantine flag yourself with `xattr -cr dist/Blockr.app`. To avoid the
warning for end users entirely, you'd need an Apple Developer ID
($99/year) to codesign and notarize the app — out of scope here, but
`codesign --deep --sign "Developer ID Application: ..." dist/Blockr.app`
followed by `xcrun notarytool submit` is the path if you want it later.

---

## 3. Linux — `.deb` and `.rpm`

**Run on:** Linux (build on the oldest distro/glibc version you want to
support — e.g. Ubuntu 22.04 — since the binary links against the host's
glibc and won't run on older systems than the one it was built on)

**Requires:** Python 3.10+, pip, and [fpm](https://github.com/jordansissel/fpm)
(a packaging tool that builds `.deb`/`.rpm` from a plain directory, so you
don't need to hand-write `debian/control` or a `.spec` RPM file):

```bash
sudo apt install ruby ruby-dev build-essential   # Debian/Ubuntu
sudo gem install --no-document fpm
```

Step 1 — build the binary:

```bash
python3 -m pip install pyinstaller PyQt6
pyinstaller packaging/linux/blockr-linux.spec
```

Output: `dist/blockr`

Step 2 — package it:

```bash
chmod +x packaging/linux/build-deb.sh packaging/linux/build-rpm.sh
./packaging/linux/build-deb.sh 1.0.0
./packaging/linux/build-rpm.sh 1.0.0
```

Output: `dist/blockr_1.0.0_amd64.deb` and `dist/blockr-1.0.0-1.x86_64.rpm`

Both packages install:
- the binary to `/usr/bin/blockr`
- a `.desktop` launcher entry to `/usr/share/applications/blockr.desktop`
- the app icon to `/usr/share/pixmaps/blockr.png`
- a dependency on `policykit-1` (Debian) / `polkit` (Fedora/RHEL) — this is
  what makes the graphical "enter your password" elevation prompt work when
  Blockr relaunches itself with `pkexec`. It's preinstalled on virtually
  every desktop Linux distro already.

### No `fpm`? Manual fallback

<details>
<summary>Manual <code>dpkg-deb</code> build (Debian/Ubuntu)</summary>

```bash
mkdir -p pkg/DEBIAN pkg/usr/bin pkg/usr/share/applications pkg/usr/share/pixmaps
cp dist/blockr pkg/usr/bin/blockr
cp packaging/linux/blockr.desktop pkg/usr/share/applications/
cp icon.png pkg/usr/share/pixmaps/blockr.png
cat > pkg/DEBIAN/control <<EOF
Package: blockr
Version: 1.0.0
Architecture: amd64
Maintainer: Joel Kajubi <joelkajubi2@gmail.com>
Depends: policykit-1
Section: utils
Priority: optional
Description: Block distracting websites at the system level via the hosts file.
EOF
dpkg-deb --build --root-owner-group pkg dist/blockr_1.0.0_amd64.deb
```

</details>

<details>
<summary>Manual <code>rpmbuild</code> build (Fedora/RHEL)</summary>

```bash
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cat > ~/rpmbuild/SPECS/blockr.spec <<'EOF'
Name: blockr
Version: 1.0.0
Release: 1
Summary: Block distracting websites at the system level via the hosts file.
License: MIT
Requires: polkit
%description
Block distracting websites at the system level via the hosts file.
%install
mkdir -p %{buildroot}/usr/bin %{buildroot}/usr/share/applications %{buildroot}/usr/share/pixmaps
cp %{_sourcedir}/blockr %{buildroot}/usr/bin/blockr
cp %{_sourcedir}/blockr.desktop %{buildroot}/usr/share/applications/
cp %{_sourcedir}/blockr.png %{buildroot}/usr/share/pixmaps/
%files
/usr/bin/blockr
/usr/share/applications/blockr.desktop
/usr/share/pixmaps/blockr.png
EOF
cp dist/blockr packaging/linux/blockr.desktop icon.png ~/rpmbuild/SOURCES/
mv ~/rpmbuild/SOURCES/icon.png ~/rpmbuild/SOURCES/blockr.png
rpmbuild -bb ~/rpmbuild/SPECS/blockr.spec
```

</details>

---

## Icons

`icon.icns` (macOS) is already generated and checked into the repo root
alongside `icon.ico` (Windows) and `icon.png` (Linux/runtime), so none of
the steps above need to regenerate it. If you replace `icon.png` with a new
design, regenerate `icon.icns` with:

```bash
python3 -c "
from PIL import Image
im = Image.open('icon.png').convert('RGBA')
im.save('icon.icns', sizes=[(16,16),(32,32),(64,64),(128,128),(256,256),(512,512),(1024,1024)])
"
```

(No macOS-only tools like `iconutil` needed — Pillow writes ICNS directly.)
