%global scl_name_base python
%global scl_name_version 33
%global scl %{scl_name_base}%{scl_name_version}
## General notes about python33 SCL packaging
# - the names of packages are NOT prefixed with 'python3-' (e.g. are the same as in Fedora)
# - the names of binaries of Python 3 itself are both python{-debug,...} and python3{-debug,...}
#   so both are usable in shebangs, the non-versioned binaries are preferred.
# - the names of other binaries are NOT prefixed with 'python3-'.
# - there are both macros in '3' variant and non-versioned variant, e.g. both %{__python}
#   and %{__python3} are available

%scl_package %scl
%global _turn_off_bytecompile 1

%global install_scl 1

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary: Package that installs %scl
Name: %scl_name
Version: 1.1
Release: 13%{?dist}
License: GPLv2+
Source0: macros.additional.%{scl}
Source1: README
Source2: LICENSE
BuildRequires: help2man
# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=857354
BuildRequires: iso-codes
BuildRequires: scl-utils-build
%if 0%{?install_scl}
Requires: %{scl_prefix}python
Requires: %{scl_prefix}python-jinja2
Requires: %{scl_prefix}python-nose
Requires: %{scl_prefix}python-simplejson
Requires: %{scl_prefix}python-setuptools
Requires: %{scl_prefix}python-sphinx
Requires: %{scl_prefix}python-sqlalchemy
Requires: %{scl_prefix}python-virtualenv
%endif

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_scl_scripts}/root
mkdir -p %{buildroot}%{_root_prefix}/lib/rpm/redhat
cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
# For systemtap
export XDG_DATA_DIRS=%{_datadir}\${XDG_DATA_DIRS:+:\${XDG_DATA_DIRS}}
# For pkg-config
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
EOF
%scl_install

# Add the aditional macros to macros.%%{scl}-config
cat %{SOURCE0} >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config
sed -i 's|@scl@|%{scl}|g' %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Create the scldevel subpackage macros
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%files

%files runtime -f filesystem
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Mon Mar 31 2014 Honza Horak <hhorak@redhat.com> - 1.1-13
- Fix path typo in README
  Related: #1061458

* Thu Mar 20 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.1-12
- Use "-f filesystem for files section of -runtime on RHEL 7.
Resolves: rhbz#1072281

* Mon Feb 17 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.1-11
- Introduce README and LICENSE.
- Change version to 1.1.
Resolves: rhbz#1061458

* Wed Jan 22 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1-10
- Add scldevel subpackage.
Resolves: rhbz#1056415

* Mon Jan 20 2014 Tomas Radej <tradej@redhat.com> - 1-9
- Rebuilt with fixed scl-utils
Resolves: rhbz#1054734

* Mon Nov 25 2013 Robert Kuska <rkuska@redhat.com> - 1-8
- Add unversioned python macros for building depending packages

* Tue Nov 12 2013 Robert Kuska <rkuska@redhat.com> - 1-7
- Make building depending collections on top of python33 easier
- Add prep phase with setup macro because of rhel7 requirements

* Mon May 27 2013 Robert Kuska <rkuska@redhat.com> - 1-6
- Another fix of MANPATH (RHBZ #966393)

* Thu May 23 2013 Robert Kuska <rkuska@redhat.com> - 1-5
- Fix MANPATH (RHBZ #966393).

* Tue May 07 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-4
- Remove unneded rhel-5 specifics.
- Add some more dependencies to metapackage spec.
- Fix the enable scriptlet variable definition to be really secure.
- Move the rpm scripts to python-devel, so that possible depending
collections can use them as well.

* Thu Apr 11 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-3
- Define variables in enable scriptlets in a secure way (RHBZ #949000).

* Thu Jan 31 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-2
- Require the whole SCL on installation.

* Fri Dec 21 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1-1
- Initial package.
