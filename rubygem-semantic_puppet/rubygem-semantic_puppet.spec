%global gem_name semantic_puppet

Name:           rubygem-%{gem_name}
Version:        1.0.2
Release:        1%{?dist}
Summary:        Tools used by Puppet to parse, validate, and compare Semantic Versions
License:        ASL 2.0

URL:            https://github.com/puppetlabs/semantic_puppet

Source0:        https://rubygems.org/downloads/semantic_puppet-%{version}.gem

BuildArch:      noarch

BuildRequires:  rubygems-devel

%description
Tools used by Puppet to parse, validate, and compare Semantic Versionsand Version
Ranges and to query and resolve module dependencies.

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
* Mon Jul 15 2019 Alfredo Moralejo <amoralej@redhat.com> - 1.0.2-1
- Initial package
