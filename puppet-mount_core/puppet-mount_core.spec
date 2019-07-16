%global lib_name mount_core
%global repo_name puppetlabs-%{lib_name}
%global puppet_libdir  %{ruby_vendorlibdir}

Name:           puppet-%{lib_name}
Version:        1.0.3
Release:        1%{?dist}
Summary:        Manages mounted filesystems and mount tables.
License:        ASL 2.0

URL:            https://github.com/puppetlabs/%{repo_name}

Source0:        https://github.com/puppetlabs/%{repo_name}/archive/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  git
BuildRequires:  ruby-devel

%description
Manages mounted filesystems and mount tables.

%prep
%autosetup -n %{repo_name}-%{version} -S git

%build

%install

mkdir -p %{buildroot}%{puppet_libdir}/puppet/vendor_modules/%{lib_name}
cp -rp * %{buildroot}%{puppet_libdir}/puppet/vendor_modules/%{lib_name}


%files
%{puppet_libdir}/puppet/vendor_modules/%{lib_name}

%changelog
* Mon Jul 15 2019 Alfredo Moralejo <amoralej@redhat.com> - 1.0.3-1
- Initial package
