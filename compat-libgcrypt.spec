Name:           compat-libgcrypt
Version:        1.5.5
Release:        6%{?dist}
URL:            http://www.gnupg.org/
License:        LGPLv2+
Summary:        A general-purpose cryptography library

Source0:        https://gnupg.org/ftp/gcrypt/libgcrypt/libgcrypt-%{version}.tar.bz2

# Red Hat approved ECC support (from 1.5.3)
Source1:        ecc.c
Source2:        curves.c

# make FIPS hmac compatible with fipscheck - non upstreamable
Patch2:         libgcrypt-1.5.0-use-fipscheck.patch
# fix tests in the FIPS mode, fix the FIPS-186-3 DSA keygen
Patch5:         libgcrypt-1.5.0-tests.patch
# add configurable source of RNG seed and seed by default
# from /dev/urandom in the FIPS mode
Patch6:         libgcrypt-1.5.0-fips-cfgrandom.patch
# make the FIPS-186-3 DSA CAVS testable
Patch7:         libgcrypt-1.5.0-fips-cavs.patch
# fix for memory leaks an other errors found by Coverity scan
Patch9:         libgcrypt-1.5.0-leak.patch
# use poll instead of select when gathering randomness
Patch11:        libgcrypt-1.5.1-use-poll.patch
# compile rijndael with -fno-strict-aliasing
Patch12:        libgcrypt-1.5.2-aliasing.patch
# slight optimalization of mpicoder.c to silence Valgrind (#968288)
Patch13:        libgcrypt-1.5.2-mpicoder-gccopt.patch
# fix tests to work with approved ECC
Patch14:        libgcrypt-1.5.3-ecc-test-fix.patch
# pbkdf2 speedup - upstream
Patch15:        libgcrypt-1.5.3-pbkdf-speedup.patch
# fix bug in whirlpool implementation (for backwards compatibility
# with files generated with buggy version set environment
# varible GCRYPT_WHIRLPOOL_BUG
Patch16:        libgcrypt-1.5.3-whirlpool-bug.patch

BuildRequires:  gcc
BuildRequires:  gawk
BuildRequires:  libgpg-error-devel >= 1.4
BuildRequires:  pkgconfig
BuildRequires:  fipscheck

%description
Libgcrypt is a general purpose crypto library based on the code used in GNU
Privacy Guard. This is a development version.

%prep
%setup -q -n libgcrypt-%{version}
%patch2 -p1 -b .use-fipscheck
%patch5 -p1 -b .tests
%patch6 -p1 -b .cfgrandom
%patch7 -p1 -b .cavs
%patch9 -p1 -b .leak
%patch11 -p1 -b .use-poll
%patch12 -p1 -b .aliasing
%patch13 -p1 -b .gccopt
%patch14 -p1 -b .eccfix
%patch15 -p1 -b .pbkdf-speedup
%patch16 -p1 -b .whirlpool-bug

# Overwrite stuff
cp -f %{SOURCE1} cipher/ecc.c
cp -f %{SOURCE2} tests/curves.c

%build
%configure --disable-static \
%ifarch sparc64
     --disable-asm \
%endif
     --enable-noexecstack \
     --enable-hmac-binary-check \
     --enable-pubkey-ciphers='dsa elgamal rsa ecc' \
     --disable-O-flag-munging
make %{?_smp_mflags}

%check
fipshmac src/.libs/libgcrypt.so.??
make check

# Add generation of HMAC checksums of the final stripped binaries 
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    fipshmac %{buildroot}%{_libdir}/*.so.?? \
%{nil}

%install
install -D -m755 src/.libs/libgcrypt.so.11.8.4 %{buildroot}/%{_libdir}/libgcrypt.so.11.8.4
ldconfig -nv %{buildroot}/%{_libdir}
mkdir -p -m 755 %{buildroot}/etc/gcrypt

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license COPYING.LIB
%dir /etc/gcrypt
%{_libdir}/libgcrypt.so.*
%{_libdir}/.libgcrypt.so.*.hmac

%changelog
* Wed Oct 12 2016 Simone Caronni <negativo17@gmail.com> - 1.5.5-6
- Remove devel subpackage.
- Make the package much smaller in terms of functionality, similar to other
  compat packages.

* Fri Apr 01 2016 Simone Caronni <negativo17@gmail.com> - 1.5.5-1
- Update to 1.5.5.
- Use new scriptlets for install-info.
- Add license macro.
- Clean up files list.
- Remove obsolete tags.
- Get rid of defines.
- Remove option to relocate libraries.

* Wed May 21 2014 Sandro Mathys <red@fedoraproject.org> 1.5.3-4
- Turned the non-current libgcrypt package into a compat package

* Tue Jan 21 2014 Tomáš Mráz <tmraz@redhat.com> 1.5.3-3
- add back the nistp521r1 EC curve
- fix a bug in the Whirlpool hash implementation
- speed up the PBKDF2 computation
