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
%define _default_patch_fuzz 999

Name: coolkey
Version: 1.1.0
Release: 39%{?dist}
Summary: CoolKey PKCS #11 module
License: LGPLv2
URL: http://directory.fedora.redhat.com/wiki/CoolKey
Source: coolkey-%{version}.tar.gz
Patch1: coolkey-cache-dir-move.patch
Patch2: coolkey-gcc43.patch
Patch3: coolkey-latest.patch
Patch4: coolkey-simple-bugs.patch
Patch5: coolkey-pcsc-usb.patch
Patch6: coolkey-cac-rhl6.patch
Patch7: coolkey-pcscd-restart.patch
Patch8: coolkey-piv.patch
Patch9: coolkey-thread-fix.patch
Patch10: coolkey-mem-leak.patch
Patch11: coolkey-spice-fix.patch
Patch12: coolkey-1.1.0-fussy_piv.patch
Patch13: coolkey-1.1.0-broken_gemalto.patch
Patch14: coolkey-1.1.0-gvt_piv.patch
Patch15: coolkey-ecc-el6.patch
Patch16: coolkey-1.1.0-noegate.patch
Patch17: coolkey-1.1.0-mem-over.patch
Patch18: coolkey-coverity-6.5.patch
Patch19: coolkey-1.1.0-add-sql.patch
Patch20: coolkey-1.1.0-noapplet.patch
Patch21: coolkey-1.1.0-uninit-var.patch
Patch22: coolkey-1.1.0-contactless.patch
Patch23: coolkey-1.1.0-alt-cac.patch
Patch24: coolkey-1.1.0-hp-fix.patch 
Patch25: coolkey-1.1.0-alt-cac-2.patch
Patch26: coolkey-1.1.0-move-cache.patch
Patch27: coolkey-1.1.0-hp-fix-2.patch 

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
%patch2 -b .coolkey-gcc43 %{?_rawbuild}
%patch3 -b .coolkey-latest
%patch4 -b .coolkey-simple-bugs
%patch5 -b .coolkey-pcsc-usb
%patch6 -b .cac-rhl6
%patch7 -b .pcscd-restart
%patch8 -b .piv
%patch9 -b .thread
%patch10 -b .mem-leak
%patch11 -b .spice-fix
%patch12 -b .fussy_piv
%patch13 -b .broken_gemalto
%patch14 -b .gvt_piv
%patch15 -b .ecc
%patch16 -b .noegate
%patch17 -b .mem-over
%patch18 -b .coverity
%patch19 -b .sql
%patch20 -b .noapplet
%patch21 -b .uninit-var
%patch22 -b .contactless
%patch23 -b .alt_cac
%patch24 -b .hp_fix
%patch25 -b .alt_cac_2
%patch26 -b .move_cache
%patch27 -b .hp_fix_2

%build
autoconf
%configure --with-debug --disable-dependency-tracking --enable-pk11install
make %{?_smp_mflags} CFLAGS="$CFLAGS -g -O2 -fno-strict-aliasing" CXXFLAGS="$CXXFLAGS -g -O2 -fno-strict-aliasing"

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
ln -s pkcs11/libcoolkeypk11.so $RPM_BUILD_ROOT/%{_libdir}
mkdir -p $RPM_BUILD_ROOT/var/cache/coolkey

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
if [ -x %{_bindir}/pk11install ]; then
   isThere=`modutil -rawlist -dbdir dbm:%{nssdb} | grep %{coolkey_module} || echo NO`
   if [ "$isThere" == "NO" ]; then
      pk11install -l -p %{nssdb} 'name=%{coolkey_module} library=libcoolkeypk11.so' ||:
   fi
   isThere=`modutil -rawlist -dbdir sdb:%{nssdb} | grep %{coolkey_module} || echo NO`
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
%{_libdir}/pkcs11/libcoolkeypk11.so
%{_libdir}/libckyapplet.so.1
%{_libdir}/libckyapplet.so.1.0.0
%attr(1777,root,root) /var/cache/coolkey

%files devel
%defattr(-,root,root,-)
%{_libdir}/libckyapplet.so
%{_libdir}/pkgconfig/libckyapplet.pc
%{_includedir}/*.h


%changelog
* Wed Dec 7 2016 Bob Relyea <rrelyea@redhat.com> - 1.1.0-39
- fix hang when using hp keyboard with CAC and coolkey cards

* Wed Sep 28 2016 Bob Relyea <rrelyea@redhat.com> - 1.1.0-38
- rename the cache changes done in -36 so that they have issues with old
  cache values
- fix cac 1 alt tokens that store certs beyond the top three slots
- fix hand when using hp keyboard

* Tue Jan 19 2016 Bob Relyea <rrelyea@redhat.com> - 1.1.0-37
- Make sure the /var/cache/coolkey directory has the correct permissions in
  the spec file.

* Tue Jan 19 2016 Bob Relyea <rrelyea@redhat.com> - 1.1.0-36
- Recognize up to 10 certs and keys on PIV and CAC cards.
- Allow cards to have no cert in slot '0'.
- Allow cards to have ECC and RSA certs and keys

* Wed Apr 8 2015 Bob Relyea <rrelyea@redhat.com> - 1.1.0-35
- Fix typo that broke ESC phone home.

* Fri Feb 27 2015 Bob Relyea <rrelyea@redhat.com> - 1.1.0-34
- make contactless support more reliable. Make signing work.

* Thu Feb 26 2015 Bob Relyea <rrelyea@redhat.com> - 1.1.0-33
- contactless support

* Thu Jul 31 2014 Bob Relyea <rrelyea@redhat.com> - 1.1.0-32
- initialize the ATR length so it doesn't accidentally fall into
  the auto allocate value.

* Fri Sep 6 2013 Bob Relyea <rrelyea@redhat.com> - 1.1.0-31
- make coolkey work when no applet is installed.

* Fri Sep 6 2013 Bob Relyea <rrelyea@redhat.com> - 1.1.0-30
- update pk11install to work with sqlite databases

* Tue Aug 13 2013 Bob Relyea <rrelyea@redhat.com> - 1.1.0-29
- silence coverity warnings

* Tue Aug 6 2013 Bob Relyea <rrelyea@redhat.com> - 1.1.0-27
- restore dummy E-gate fix 
- add ECC

* Wed Dec 19 2012 Bob Relyea <rrelyea@redhat.com> - 1.1.0-26
- Drop dummy E-gate fix from previous build

* Wed Dec 19 2012 Bob Relyea <rrelyea@redhat.com> - 1.1.0-25
- Fix PIV-II cards.
- Remove dummy E-gate reader

* Thu Nov 29 2012 Bob Relyea <rrelyea@redhat.com> - 1.1.0-24
- Sigh, dependencies are space sensitive.

* Tue Nov 27 2012 Bob Relyea <rrelyea@redhat.com> - 1.1.0-23
- Fix rpmdiff issue (make cookey-devel depend on exact version of coolkey)

* Mon Nov 26 2012 Bob Relyea <rrelyea@redhat.com> - 1.1.0-22
- Some Gemalto Card Managers silently ignore SELECT APDU's for applets 
  that don't exist. This makes coolkeys with this cards look like PIV.
  Check the data returned from select and make sure the PIV is for real.

* Mon Oct 1 2012 Bob Relyea <rrelyea@redhat.com> - 1.1.0-21
- Testing coolkey applet first confuses some PIV cards, so test PIV first.

* Mon Mar 6 2012 Bob Relyea <rrelyea@redhat.com> - 1.1.0-20
- Fix Spice issue where we disconnected if we couldn't find the applet
  rather then treating the applet as empty. 
- Fix memory leak in machdep error path

* Wed Sep 7 2011 Bob Relyea <rrelyea@redhat.com> - 1.1.0-19
- Allow raw builds to complete
- Allow coolkey to be called by threaded only apps

* Wed Aug 10 2011 Bob Relyea <rrelyea@redhat.com> - 1.1.0-18
- Support PIV cards

* Tue Jan 18 2011 Bob Relyea <rrelyea@redhat.com> - 1.1.0-17
- Handle pcsc-lite restarts
  Resolves: #210200

* Wed Aug 11 2010 Ray Strode <rstrode@redhat.com> 1.1.0-16
- Work with newer piv-like CAC cards
  Resolves: #622916

* Tue Jul 27 2010 Bob Relyea <rrelyea@redhat.com> - 1.1.0-15
- Own the coolkey cache directory.
- Bugzilla #604086

* Thu Jun 16 2010 Jack Magne <jmagne@redhat.com> - 1.1.0-14
- Smooth over issue with USB Gemalto key impersonating CAC card.
- Bugzilla #604214.

* Thu Jan 14 2010 Bob Relyea <rrelyea@redhat.com> - 1.1.0-13
- ifd-egate is no longer needed, and has been removed from RHEL-6

* Tue Jan 12 2010 Bob Relyea <rrelyea@redhat.com> - 1.1.0-12
- spec file clean up from  package wrangler

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

* Fri Aug 20 2007 Bob Relyea <rrelyea@redhat.com> - 1.1.0-4
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

* Thu Oct 4 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-7
- silence modutil warnings

* Thu Sep 30 2006 Bob Relyea <rrelyea@redhat.com> - 1.0.1-5
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
