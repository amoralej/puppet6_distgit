%global gem_name puppet-resource_api

Name:           rubygem-%{gem_name}
Version:        1.8.4
Release:        1%{?dist}
Summary:        This is an implementation of the Resource API specification.
License:        ASL 2.0

URL:            https://github.com/puppetlabs/%{gem_name}

Source0:        https://rubygems.org/downloads/%{gem_name}-%{version}.gem

BuildArch:      noarch

BuildRequires:  rubygems-devel

%description
This is an implementation of the Resource API specification. The puppet-resource_apixi
 gem is part of the Puppet 6 Platform.

%prep
%setup -q -n  %{gem_name}-%{version}

%build
gem build ../%{gem_name}-%{version}.gemspec

%gem_install

%install

mkdir -p %{buildroot}%{gem_dir}
cp -a ./%{gem_dir}/* %{buildroot}%{gem_dir}/


%files
%{gem_dir}

%changelog
* Tue Jul 16 2019 Alfredo Moralejo <amoralej@redhat.com> - 1.8.4-1
- Initial package
