Name:           compat-libgcrypt
Version:        1.5.5
Release:        5%{?dist}
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

BuildRequires:  gawk
BuildRequires:  libgpg-error-devel >= 1.4
BuildRequires:  pkgconfig
BuildRequires:  fipscheck
# This is needed only when patching the .texi doc.
BuildRequires:  texinfo

%description
Libgcrypt is a general purpose crypto library based on the code used in GNU
Privacy Guard. This is a development version.

%package devel
Summary:        Development files for the %{name} package
License:        LGPLv2+ and GPLv2+
Requires(pre):  /sbin/install-info
Requires(post): /sbin/install-info
Requires:       libgpg-error-devel
Requires:       %{name} = %{version}-%{release}

%description devel
Libgcrypt is a general purpose crypto library based on the code used in GNU
Privacy Guard. This package contains files needed to develop applications using
libgcrypt.

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
%make_install

# Change /usr/lib64 back to /usr/lib.  This saves us from having to patch the
# script to "know" that -L/usr/lib64 should be suppressed, and also removes
# a file conflict between 32- and 64-bit versions of this package.
# Also replace my_host with none.
sed -i -e 's,^libdir="/usr/lib.*"$,libdir="/usr/lib",g' %{buildroot}/%{_bindir}/libgcrypt-config
sed -i -e 's,^my_host=".*"$,my_host="none",g' %{buildroot}/%{_bindir}/libgcrypt-config

rm -f %{buildroot}/%{_infodir}/dir %{buildroot}/%{_libdir}/*.la
/sbin/ldconfig -n %{buildroot}/%{_libdir}

# Create /etc/gcrypt (hardwired, not dependent on the configure invocation) so
# that _someone_ owns it.
mkdir -p -m 755 %{buildroot}/etc/gcrypt

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post devel
/sbin/install-info %{_infodir}/gcrypt.info.gz %{_infodir}/dir || :

%preun devel
if [ $1 = 0 ] ; then
  /sbin/install-info --delete %{_infodir}/gcrypt.info.gz %{_infodir}/dir || :
fi

%files
%{!?_licensedir:%global license %%doc}
%license COPYING.LIB
%doc AUTHORS NEWS THANKS
%dir /etc/gcrypt
%{_libdir}/libgcrypt.so.*
%{_libdir}/.libgcrypt.so.*.hmac

%files devel
%{_bindir}/dumpsexp
%{_bindir}/hmac256
%{_bindir}/libgcrypt-config
%{_datadir}/aclocal/*
%{_includedir}/*
%{_infodir}/gcrypt.info*
%{_libdir}/*.so

%changelog
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
