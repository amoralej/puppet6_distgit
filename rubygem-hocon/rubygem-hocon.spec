# Generated from hocon-0.9.3.gem by gem2rpm -*- rpm-spec -*-
%global gem_name hocon

%if 0%{?el7} || 0%{?el8}
%global enable_checks 0
%else
%global enable_checks 1
%endif

Name: rubygem-%{gem_name}
Version: 1.2.5
Release: 4%{?dist}
Summary: HOCON Config Library
License: ASL 2.0
URL: https://github.com/puppetlabs/ruby-hocon
Source0: https://rubygems.org/gems/%{gem_name}-%{version}.gem

BuildRequires: ruby(release)
BuildRequires: rubygems-devel
BuildRequires: ruby >= 1.9.0
%if 0%{?enable_checks}
BuildRequires: rubygem(rspec)
%endif
BuildArch: noarch

%description
A port of the Java Typesafe Config
library to Ruby.
https://github.com/typesafehub/config

%package doc
Summary: Documentation for %{name}
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

%description doc
Documentation for %{name}.

%prep
gem unpack %{SOURCE0}

%setup -q -D -T -n  %{gem_name}-%{version}

gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec
sed -i 's/\/usr\/bin\/env ruby/\/usr\/bin\/ruby/' bin/hocon

%build
# Create the gem as gem install only works on a gem file
gem build %{gem_name}.gemspec

# %%gem_install compiles any C extensions and installs the gem into ./%%gem_dir
# by default, so that we can move it into the buildroot in %%install
%gem_install

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/
mkdir -p %{buildroot}%{_bindir}
mv %{buildroot}%{gem_instdir}/bin/hocon %{buildroot}/%{_bindir}/hocon


%check
%if 0%{?enable_checks}
rspec spec/
%endif

%files
%dir %{gem_instdir}
%license %{gem_instdir}/LICENSE
%{gem_libdir}
%exclude %{gem_cache}
%exclude %{gem_instdir}/spec
%{gem_spec}
%{_bindir}/hocon

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/CHANGELOG.md
%doc %{gem_instdir}/HISTORY.md
%doc %{gem_instdir}/README.md

%changelog
* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Nov 03 2017 Steve Traylen <steve.traylen@cern.ch> - 1.2.5-1
- Update to 1.2.5

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Mar 23 2017 Steve Traylen <steve.traylen@cern.ch> - 1.2.4-1
- Update to 1.2.4

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 14 2015 Steve Traylen <steve.traylen@cern.ch> - 0.9.3-3
- Remove references to fc21.

* Thu Dec 03 2015 Steve Traylen <steve.traylen@cern.ch> - 0.9.3-2
- Use spec tests from upstream source.

* Tue Nov 03 2015 Steve Traylen <steve.traylen@cern.ch> - 0.9.3-1
- Initial package
