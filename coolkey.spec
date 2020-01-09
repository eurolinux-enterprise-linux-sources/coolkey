# BEGIN COPYRIGHT BLOCK
# Copyright (C) 2005 Red Hat, Inc.
# All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation version
# 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# END COPYRIGHT BLOCK

%define coolkey_module "CoolKey PKCS #11 Module"
%define nssdb %{_sysconfdir}/pki/nssdb

Name: coolkey
Version: 1.1.0
Release: 37.51%{?dist}
Summary: CoolKey PKCS #11 module
License: LGPLv2
URL: http://directory.fedora.redhat.com/wiki/CoolKey
Source: coolkey-%{version}.tar.gz
Source1: coolkey.module
Patch1: coolkey-cache-dir-move.patch
Patch2: coolkey-gcc43.patch
Patch3: coolkey-latest.patch
Patch4: coolkey-simple-bugs.patch
Patch5: coolkey-thread-fix.patch
Patch6: coolkey-cac.patch
Patch7: coolkey-cac-1.patch
Patch8: coolkey-pcsc-lite-fix.patch
Patch9: coolkey-fix-token-removal-failure.patch
Patch10: coolkey-piv-ecc-el7.patch
Patch20: coolkey-1.1.0-noapplet.patch
Patch21: coolkey-1.1.0-fix-spurious-event.patch
Patch22: coolkey-1.1.0-p15.patch
Patch23: coolkey-1.1.0-p15-coverity.patch
Patch24: coolkey-1.1.0-more-keys.patch
Patch25: coolkey-1.1.0-fail-on-bad-mechanisms.patch
Patch26: coolkey-1.1.0-max-cpu-bug.patch
Patch27: coolkey-1.1.0-rhel7-alt-cac.patch
Patch28: coolkey-1.1.0-cardos-5-3.patch
Patch29: coolkey-1.1.0-alt-tokens-2.patch


Group: System Environment/Libraries
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: autoconf
BuildRequires: pcsc-lite-devel
BuildRequires: zlib-devel
BuildRequires: nss-devel
Requires: nss-tools
Requires: pcsc-lite 
Requires: pcsc-lite-libs
Requires: ccid
Provides: CoolKey Openkey
Obsoletes: CoolKey Openkey
# 390 does not have libusb or smartCards
ExcludeArch: s390 s390x

%description
Linux Driver support for the CoolKey and CAC products. 

%package devel
Summary: CoolKey Applet libraries
Group: System Environment/Libraries
Requires: coolkey = %{version}-%{release}

%description devel
Linux Driver support to access the CoolKey applet.


%prep
%setup -q
%patch1 -b .cache.dir.move
%patch2 -b .coolkey-gcc43
%patch3 -b .coolkey-latest
%patch4 -b .coolkey-simple-bugs
%patch5 -b .coolkey-thread-fix
%patch6 -b .cac
%patch7 -b .cac-1
%patch8 -b .reader-state-fix
%patch9 -p1 -b .fix-token-removal-failure
%patch10 -b .piv-ecc
%patch20 -b .noapplet
%patch21 -b .fix-spurious
%patch22 -b .p15
%patch23 -b .p15-coverity
%patch24 -b .more-keys
%patch25 -b .fail-on-bad-mechanisms
%patch26 -b .max-cpu-bug
%patch27 -b .alt-cac
%patch28 -b .cardos-5-3
%patch29 -b .alt-tokens-2

%build
autoconf
%configure --with-debug --disable-dependency-tracking --enable-pk11install
make %{?_smp_mflags} CFLAGS="$CFLAGS -g -O2 -fno-strict-aliasing $CFLAGS " CXXFLAGS="$CXXFLAGS -g -O2 -fno-strict-aliasing $CFLAGS"

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
ln -s pkcs11/libcoolkeypk11.so $RPM_BUILD_ROOT/%{_libdir}
mkdir -p $RPM_BUILD_ROOT/var/cache/coolkey
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/p11-kit/modules/
cp %{SOURCE1} $RPM_BUILD_ROOT/%{_datadir}/p11-kit/modules/

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
if [ -x %{_bindir}/pk11install ]; then
  isThere=`modutil -rawlist -dbdir dbm:%{nssdb} | grep %{coolkey_module} || echo NO`
  if [ "$isThere" == "NO" ]; then
      pk11install -l -p %{nssdb} 'name=%{coolkey_module} library=libcoolkeypk11.so' ||:
   fi
  isThere=`modutil -rawlist -dbdir sql:%{nssdb} | grep %{coolkey_module} || echo NO`
  if [ "$isThere" == "NO" ]; then
      pk11install -s -p %{nssdb} 'name=%{coolkey_module} library=libcoolkeypk11.so' ||:
   fi
fi


%postun
/sbin/ldconfig
if [ $1 -eq 0 ]; then
   modutil -delete %{coolkey_module} -dbdir dbm:%{nssdb} -force || :
   modutil -delete %{coolkey_module} -dbdir sql:%{nssdb} -force || :
fi


%files
%defattr(-,root,root,-)
%doc ChangeLog LICENSE 
%{_bindir}/pk11install
%{_libdir}/libcoolkeypk11.so
%{_libdir}/pkcs11
%{_libdir}/libckyapplet.so.1
%{_libdir}/libckyapplet.so.1.0.0
%{_datadir}/p11-kit/modules/coolkey.module
%attr(1777,root,root) /var/cache/coolkey


%files devel
%{_libdir}/libckyapplet.so
%{_libdir}/pkgconfig/libckyapplet.pc
%{_includedir}/*.h


%changelog
* Mon Jun 25 2018 Robert Relyea <rrelyea@redhat.com> - 1.1.0-37.51
- Fix regression in alt token patch that prevented blank cards from working
  in ESC.

* Mon Apr 23 2018 Robert Relyea <rrelyea@redhat.com> - 1.1.0-37.50
- support cac alt tokens which don't have a cert is slot 0, don't have
  a CCC, and uses a ACA.

* Tue Mar 14 2017 Robert Relyea <rrelyea@redhat.com> - 1.1.0-37
- get Cardos 5.3 cards working properly

* Thu Dec 1 2016 Robert Relyea <rrelyea@redhat.com> - 1.1.0-36
- recognize up to 10 cac and PIV certs rather than 3

* Thu Jun 30 2016 Robert Relyea <rrelyea@redhat.com> - 1.1.0-35
- include sleep on unknown reader errors.

* Mon Jun 13 2016 Robert Relyea <rrelyea@redhat.com> - 1.1.0-34
- recognize up to 32 keys and certs in coolkeys. (can go up to 62 with just #define changes)
- own our cache file.
- verify we are using the correct mechanisms

* Mon Jul 6 2015 Robert Relyea <rrelyea@redhat.com> - 1.1.0-33
- fix more coverity issues in p15 patch

* Mon Jul 6 2015 Robert Relyea <rrelyea@redhat.com> - 1.1.0-32
- fix coverity issues in p15 patch

* Mon Jul 6 2015 Robert Relyea <rrelyea@redhat.com> - 1.1.0-31
- fix requires as identified in rpmdiff

* Mon Jul 6 2015 Robert Relyea <rrelyea@redhat.com> - 1.1.0-30
- Add pk11-kit modules file

* Mon Jul 6 2015 Robert Relyea <rrelyea@redhat.com> - 1.1.0-29
- Add partical support for pkcs15 tokens

* Fri Sep 26 2014 Robert Relyea <rrelyea@redhat.com> - 1.1.0-28
- update coolkey to handle the new error ccid/pcsc-lite returns on reader
  removal.

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.1.0-27
- Mass rebuild 2013-12-27

* Tue Nov 26 2013 Robert Relyea <rrelyea@redhat.com> - 1.1.0-26
- delete coolkey from sql db as well as the old one.

* Wed Nov 6 2013 Robert Relyea <rrelyea@redhat.com> - 1.1.0-25
- delete coolkey from sql db as well as the old one.

* Sun Sep 8 2013 Robert Relyea <rrelyea@redhat.com> - 1.1.0-24
- Add ECC and PIV support

* Wed May 22 2013 Ray Strode <rstrode@redhat.com> 1.1.0-23
- Fix token removal issue

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Oct 19 2010 Ville Skyttä <ville.skytta@iki.fi> - 1.1.0-18
- Own the %%{_libdir}/pkcs11 dir.

* Wed Sep 8 2010 Robert Relyea <rrelyea@redhat.com> - 1.1.0-17
- pscs-lite removed SCARD_READERSTATE_A definition. revert to the prefered
  SCARD_READERSTATE

* Wed Jun 23 2010 Jack Magne <jmagne@redhat.com> - 1.1.0-16
- fix possible crash when loading cac certs.

* Wed Jun 16 2010 Robert Relyea <rrelyea@redhat.com> - 1.1.0-15
- better cac support.

* Mon Feb 22 2010 Robert Relyea <rrelyea@redhat.com> - 1.1.0-14
- remove dependency on ifd-egate

* Tue Jan 5 2010 Robert Relyea <rrelyea@redhat.com> - 1.1.0-13
- bump the release number to rebuild

* Fri Dec 18 2009 Robert Relyea <rrelyea@redhat.com> - 1.1.0-12
- Fix threading issue. Coolkey will now work with non-threaded applications 
- that don't link with libpthread.

* Wed Sep 16 2009 Jack magne <jmagne@redhat.com> - 1.1.0-11
- Misc bug fixes. Resolves: 485032, #250738, #497758.

* Fri Sep 11 2009 Jack Magne <jmagne@redhat.com> - 1.1.0-10
- Include latest changes for Gemalto 64K and Safenet 330J.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Sep 14 2008 Matt Domsch <mdomsch@fedoraproject.org> - 1.1.0-7
- BR: nss-devel not mozilla-nss-devel (FTBFS BZ#440753)

* Wed Feb 13 2008 Jack magne <jmagne@redhat.com>  - 1.1.0-6
- Clean up building with gcc 4.3.
* Thu Sep 27 2007 Jack Magne <jmagne@redhat.com>  - 1.1.0-5
- Include patch for moving the cache directory to a safe location. 
- Bug #299481.
* Mon Aug 20 2007 Bob Relyea <rrelyea@redhat.com> - 1.1.0-4
- Update License description to the new Fedora standard

* Thu Jun 21 2007 Kai Engert <kengert@redhat.com> - 1.1.0-3.1
- rebuild

* Tue Jun 5 2007 Bob Relyea <rrelyea@redhat.com> - 1.1.0-3
- add build requires, bump version number for make tag.

* Thu May 31 2007 Bob Relyea <rrelyea@redhat.com> - 1.1.0-2
- Back out RHEL-4 version of spec from CVS, add pcsc-lite-lib requires.

* Tue Feb 20 2007 Bob Relyea <rrelyea@redhat.com> - 1.1.0-1
- Pick up lates release.

* Wed Nov 1 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-15
- Don't grab the CUID on cac's. Resting the card causes it to
- logout of other applications.

* Wed Nov 1 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-14
- Shared memory directory needs to be writeable by all so
- coolkey can create caches for any user. (lack of caches
- show up in screen savers reactly slowly).

* Fri Oct 20 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-13
- fix login hw race failures

* Fri Oct 20 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-12
- add the dist flag

* Wed Oct 18 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-11
- CAC cards sometimes need to reset before they can get their
- initial transaction (problem is noticed on insertion an removal)

* Tue Oct 17 2006 Jesse Keating <jkeating@redhat.com> - 1.0.1-10
- Only run pk11install if the binary is there (multilib fun)

* Mon Oct 09 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-9
- use pk11install which does not require loading the module to install it.

* Mon Oct 09 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-8
- pcscd must be running in order to add coolkey.

* Wed Oct 4 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-7
- silence modutil warnings

* Fri Sep 29 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-5
- install and uninstall coolkey in the system secmod.db

* Thu Sep 7 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-4
- make the coolkey token caches persist over application calls.
- make a separate cache for each user.

* Sun Jul 16 2006 Florian La Roche <laroche@redhat.com> - 1.0.1-2
- fix excludearch line

* Mon Jul 10 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-1
- Don't require pthread library in coolkey

* Mon Jul 10 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.0-2
- remove s390 from the build

* Mon Jun 5 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.0-1
- Initial revision for fedora
