%global toolchain clang

# Opt out of https://fedoraproject.org/wiki/Changes/fno-omit-frame-pointer
# https://bugzilla.redhat.com/show_bug.cgi?id=2158587
%undefine _include_frame_pointers

%global pkg_name lld
%global install_prefix /usr
%global install_includedir %{_includedir}
%global install_libdir %{_libdir}
%global install_datadir %{_datadir}

Name:		lld
Version:	14.0.6
Release:	1
Summary:	The LLVM Linker
License:	Apache-2.0 WITH LLVM-exception OR NCSA
URL:		http://llvm.org
Source :	%{name}-%{version}.tar.xz

Patch0:		0001-add-cmake-modules.patch
Patch1:		0002-PATCH-lld-Import-compact_unwind_encoding.h-from-libu.patch

BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	llvm-devel >= %{version}
BuildRequires:	ncurses-devel
BuildRequires:	zlib-devel

Requires: %{name}-libs = %{version}-%{release}

%description
The LLVM project linker.

%package devel
Summary:	Libraries and header files for LLD
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
This package contains library and header files needed to develop new native
programs that use the LLD infrastructure.

%package libs
Summary:	LLD shared libraries

%description libs
Shared libraries for LLD.

%prep

%autosetup  -n %{name}-%{version}/upstream/lld -p2

%build

mkdir -p build
pushd build

%cmake ../ \
	-GNinja \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_COMPONENTS="all" \
	-DLLVM_COMMON_CMAKE_UTILS=%{install_datadir}/llvm/cmake \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DLLVM_INCLUDE_TESTS=OFF \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_LIT_ARGS="-sv \
	--path %{_libdir}/llvm" \
	-DLLVM_LIBDIR_SUFFIX= \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src

ninja
popd

%install
pushd build
DESTDIR=%{buildroot} ninja install
rm %{buildroot}%{install_includedir}/mach-o/compact_unwind_encoding.h

popd

# Required when using update-alternatives:
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Alternatives/
touch %{buildroot}%{_bindir}/ld

install -D -m 644 -t  %{buildroot}%{_mandir}/man1/ docs/ld.lld.1

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.TXT
%ghost %{_bindir}/ld
%{_bindir}/lld*
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/wasm-ld
%{_mandir}/man1/ld.lld.1*

%files devel
%{install_includedir}/lld
%{install_libdir}/liblld*.so
%{install_libdir}/cmake/lld/

%files libs
%{install_libdir}/liblld*.so.*
