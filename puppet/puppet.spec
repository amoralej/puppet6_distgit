# Augeas and SELinux requirements may be disabled at build time by passing
# --without augeas and/or --without selinux to rpmbuild or mock

# Specifically not using systemd on F18 as it's technically a break between
# using SystemV on 2.7.x and Systemd on 3.1.0.
%if 0%{?fedora} || 0%{?rhel} >= 7
%global puppet_libdir   %{ruby_vendorlibdir}
%else
%global puppet_libdir   %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["sitelibdir"]')
%endif

%if 0%{?fedora} > 18 || 0%{?rhel} >= 7 || 0%{?suse_version}
%global _with_systemd 1
%endif

# FIXME(hguemar): RH products builds of facter and hiera have introduced epochs
# does not impact Fedora nor EPEL
%if 0%{?rhel} && 0%{?rhel} >= 7 && !0%{?epel}
%global has_epoch 1
%endif

%global confdir         conf
%global pending_upgrade_path %{_localstatedir}/lib/rpm-state/puppet
%global pending_upgrade_file %{pending_upgrade_path}/upgrade_pending

Name:           puppet
Version:        6.6.0
Release:        2%{?dist}
Summary:        A network tool for managing many disparate systems
License:        ASL 2.0
URL:            http://puppetlabs.com
Source0:        http://downloads.puppetlabs.com/%{name}/%{name}-%{version}.tar.gz
Source1:        http://downloads.puppetlabs.com/%{name}/%{name}-%{version}.tar.gz.asc
Source2:        puppet-nm-dispatcher
Source3:        puppet-nm-dispatcher.systemd
Source4:        start-puppet-wrapper

# Puppetlabs messed up with default paths
Patch01:        0001-Fix-puppet-paths.patch
Patch02:        0002-Revert-maint-Remove-puppetmaster.service.patch
Patch03:        0001-Adapt-path-for-vendored-modules-according-to-Fedora-.patch

BuildArch:      noarch
BuildRequires:  git
BuildRequires:  ruby-devel >= 2.3.0
# ruby-devel does not require the base package, but requires -libs instead
BuildRequires:  ruby >= 2.3.0

Requires:       puppet-headless = %{version}-%{release}

%if 0%{?_with_systemd}
%{?systemd_requires}
BuildRequires: systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%endif

%description
Puppet lets you centrally manage every important aspect of your system using a
cross-platform specification language that manages all the separate elements
normally aggregated in different files, like users, cron jobs, and hosts,
along with obviously discrete elements like packages, services, and files.

%package headless
Summary:        Headless Puppet
Conflicts:      puppet < 5.5.6-6
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       ruby(abi) = 1.8
%else
Requires:       ruby(release)
%endif
Requires:       ruby(shadow)
Requires:       rubygem(json)
Requires:       rubygem(pathspec)
Requires:       rubygem(rgen)
# Prevents jruby from being pulled in by dependencies (BZ #985208)
Requires:       ruby
# Pull in ruby selinux bindings where available
%{!?_without_selinux:Requires: ruby(selinux), libselinux-utils}

# Fedora 28 updates to facter3 where puppet needs to require the ruby bindings specifically
# RHEL8 has also moved to facter3
%if 0%{?fedora} >= 28 || 0%{?rhel} > 7
BuildRequires:  ruby-facter >= %{?has_epoch:1:}3.0
BuildRequires:  ruby-facter < %{?has_epoch:1:}4
Requires:       ruby-facter >= %{?has_epoch:1:}3.0
Requires:       ruby-facter < %{?has_epoch:1:}4
%else
BuildRequires:  facter >= %{?has_epoch:1:}2.0
BuildRequires:  facter < %{?has_epoch:1:}4
Requires:       facter >= %{?has_epoch:1:}2.0
Requires:       facter < %{?has_epoch:1:}4
%endif
BuildRequires:  hiera >= 2.0
BuildRequires:  hiera < %{?has_epoch:1:}4
Requires:       hiera >= 2.0
Requires:       hiera < %{?has_epoch:1:}4
Obsoletes:      hiera-puppet < 1.0.0-2
Provides:       hiera-puppet = %{version}-%{release}

%{!?_without_augeas:Requires: ruby(augeas)}
Requires:       tar
Requires(pre):  shadow-utils

# Add requires for modules and library unbundled in 6.0.0
Requires:       rubygem(semantic_puppet) >= 1.0.2
Requires:       rubygem(puppet-resource_api) >= 1.8.4
Requires:       puppet-augeas_core >= 1.0.4
Requires:       puppet-cron_core >= 1.0.1
Requires:       puppet-host_core >= 1.0.2
Requires:       puppet-mount_core >= 1.0.3
Requires:       puppet-scheduled_task >= 1.0.1
Requires:       puppet-selinux_core >= 1.0.2
Requires:       puppet-sshkeys_core >= 1.0.2
Requires:       puppet-yumrepo_core >= 1.0.3
Requires:       puppet-zfs_core >= 1.0.2
Requires:       puppet-zone_core >= 1.0.2

%description headless
This puppet headless subpackage may be used when there is no need to
have puppet agent running as a service, for example, in a container
image.

%prep
%autosetup -S git
# Unbundle
rm -r lib/puppet/vendor/pathspec
# Note(hguemar): remove unrelated OS/distro specific folders
# These mess-up with RPM automatic dependencies compute by adding
# unnecessary deps like /sbin/runscripts
rm -r ext/{debian,freebsd,gentoo,ips,osx,solaris,suse,windows}
rm ext/redhat/*.init
rm ext/{build_defaults.yaml,project_data.yaml}


%build
# Nothing to build

%install
rm -rf %{buildroot}
ruby install.rb --destdir=%{buildroot} \
     --configdir=%{_sysconfdir}/puppet \
     --bindir=%{_bindir} --vardir=%{_localstatedir}/cache/puppet \
     --logdir=%{_localstatedir}/log/puppet \
     --rundir=%{_localstatedir}/log/puppet \
     --localedir=%{_datadir}/%{name}/locale \
     --quick --no-rdoc --sitelibdir=%{puppet_libdir}


install -d -m0755 %{buildroot}%{_sysconfdir}/puppet/manifests
install -d -m0755 %{buildroot}%{_datadir}/%{name}/modules
install -d -m0755 %{buildroot}%{_localstatedir}/lib/puppet
install -d -m0755 %{buildroot}%{_localstatedir}/run/puppet
install -d -m0750 %{buildroot}%{_localstatedir}/log/puppet
install -d -m0750 %{buildroot}%{_localstatedir}/cache/puppet

%if 0%{?_with_systemd}
%{__install} -d -m0755  %{buildroot}%{_unitdir}
install -Dp -m0644 ext/systemd/puppet.service %{buildroot}%{_unitdir}/puppet.service
ln -s %{_unitdir}/puppet.service %{buildroot}%{_unitdir}/puppetagent.service
%else
install -Dp -m0644 %{confdir}/client.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/puppet
install -Dp -m0755 %{confdir}/client.init %{buildroot}%{_initrddir}/puppet
%endif

install -Dp -m0644 %{confdir}/auth.conf %{buildroot}%{_sysconfdir}/puppet/auth.conf
install -Dp -m0644 %{confdir}/puppet.conf %{buildroot}%{_sysconfdir}/puppet/puppet.conf
install -Dp -m0644 ext/redhat/logrotate %{buildroot}%{_sysconfdir}/logrotate.d/puppet

# Note(hguemar): Conflicts with config file from hiera package
rm %{buildroot}%{_sysconfdir}/puppet/hiera.yaml

# Install a NetworkManager dispatcher script to pickup changes to
# /etc/resolv.conf and such (https://bugzilla.redhat.com/532085).
%if 0%{?_with_systemd}
install -Dpv -m0755 %{SOURCE3} \
    %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/98-%{name}
%else
install -Dpv -m0755 %{SOURCE2} \
    %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/98-%{name}
%endif

# Install the ext/ directory to %%{_datadir}/%%{name}
install -d %{buildroot}%{_datadir}/%{name}
cp -a ext/ %{buildroot}%{_datadir}/%{name}

chmod 0755 %{buildroot}%{_datadir}/%{name}/ext/regexp_nodes/regexp_nodes.rb

# Install wrappers for SELinux
install -Dp -m0755 %{SOURCE4} %{buildroot}%{_bindir}/start-puppet-agent
install -Dp -m0755 %{SOURCE4} %{buildroot}%{_bindir}/start-puppet-master
install -Dp -m0755 %{SOURCE4} %{buildroot}%{_bindir}/start-puppet-ca
%if 0%{?_with_systemd}
sed -i 's|^ExecStart=.*/bin/puppet|ExecStart=/usr/bin/start-puppet-agent|' \
  %{buildroot}%{_unitdir}/puppet.service
%endif

%if 0%{?fedora} >= 15
# Setup tmpfiles.d config
mkdir -p %{buildroot}%{_tmpfilesdir}
echo "D /var/run/%{name} 0755 %{name} %{name} -" > \
    %{buildroot}%{_tmpfilesdir}/%{name}.conf
%endif

# Create puppet modules directory for puppet module tool
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/modules

# Create directory for vendored modules
mkdir -p %{buildroot}%{puppet_libdir}/puppet/vendor_modules

%files
%if 0%{?_with_systemd}
%{_unitdir}/puppet.service
%{_unitdir}/puppetagent.service
%else
%{_initrddir}/puppet
%config(noreplace) %{_sysconfdir}/sysconfig/puppet
%endif
%if 0%{?fedora} >= 15
%{_tmpfilesdir}/%{name}.conf
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/puppet
%dir %{_sysconfdir}/NetworkManager
%dir %{_sysconfdir}/NetworkManager/dispatcher.d
%{_sysconfdir}/NetworkManager/dispatcher.d/98-puppet

%files headless
%doc README.md examples
%license LICENSE
%{_bindir}/puppet
%{_bindir}/start-puppet-*
%{puppet_libdir}/*
%dir %{_sysconfdir}/puppet
%dir %{_sysconfdir}/%{name}/modules
%config(noreplace) %{_sysconfdir}/puppet/puppet.conf
%config(noreplace) %{_sysconfdir}/puppet/auth.conf
%{_datadir}/%{name}
# These need to be owned by puppet so the server can
# write to them
%attr(-, puppet, puppet) %{_localstatedir}/run/puppet
%attr(0750, puppet, puppet) %{_localstatedir}/log/puppet
%attr(-, puppet, puppet) %{_localstatedir}/lib/puppet
%attr(0750, puppet, puppet) %{_localstatedir}/cache/puppet
%{_mandir}/man5/puppet.conf.5.gz
%{_mandir}/man8/puppet.8.gz
%{_mandir}/man8/puppet-agent.8.gz
%{_mandir}/man8/puppet-apply.8.gz
%{_mandir}/man8/puppet-catalog.8.gz
%{_mandir}/man8/puppet-describe.8.gz
%{_mandir}/man8/puppet-config.8.gz
%{_mandir}/man8/puppet-device.8.gz
%{_mandir}/man8/puppet-doc.8.gz
%{_mandir}/man8/puppet-facts.8.gz
%{_mandir}/man8/puppet-filebucket.8.gz
%{_mandir}/man8/puppet-generate.8.gz
%{_mandir}/man8/puppet-help.8.gz
%{_mandir}/man8/puppet-epp.8.gz
%{_mandir}/man8/puppet-key.8.gz
%{_mandir}/man8/puppet-lookup.8.gz
%{_mandir}/man8/puppet-man.8.gz
%{_mandir}/man8/puppet-module.8.gz
%{_mandir}/man8/puppet-node.8.gz
%{_mandir}/man8/puppet-parser.8.gz
%{_mandir}/man8/puppet-plugin.8.gz
%{_mandir}/man8/puppet-report.8.gz
%{_mandir}/man8/puppet-resource.8.gz
%{_mandir}/man8/puppet-script.8.gz
%{_mandir}/man8/puppet-ssl.8.gz
%{_mandir}/man8/puppet-status.8.gz

# Fixed uid/gid were assigned in bz 472073 (Fedora), 471918 (RHEL-5),
# and 471919 (RHEL-4)
%pre headless
getent group puppet &>/dev/null || groupadd -r puppet -g 52 &>/dev/null
getent passwd puppet &>/dev/null || \
useradd -r -u 52 -g puppet -d %{_localstatedir}/lib/puppet -s /sbin/nologin \
    -c "Puppet" puppet &>/dev/null
# ensure that old setups have the right puppet home dir
if [ $1 -gt 1 ]; then
  usermod -d %{_localstatedir}/lib/puppet puppet &>/dev/null
fi
exit 0

%post
%if 0%{?_with_systemd}
%systemd_post puppet.service
%else
# If there's a running puppet agent, restart it during upgrade. Fixes
# BZ #1024538.
if [ "$1" -ge 1 ]; then
  pid="%{_localstatedir}/run/puppet/agent.pid"
  if [ -e "$pid" ]; then
    if ps -p "$(< "$pid")" -o cmd= | grep -q "puppet agent"; then
      kill "$(< "$pid")" \
      && rm -f "$pid" \
      && /sbin/service puppet start
    fi &>/dev/null
  fi
fi
/sbin/chkconfig --add puppet
%endif
exit 0

%preun
%if 0%{?_with_systemd}
%systemd_preun puppet.service
%else
if [ "$1" -eq 0 ]; then
  /sbin/service puppet stop &>/dev/null
  /sbin/chkconfig --del puppet
fi
%endif
exit 0

%postun
%if 0%{?_with_systemd}
%systemd_postun_with_restart puppet.service
%else
if [ "$1" -ge 1 ]; then
  /sbin/service puppet condrestart &>/dev/null
fi
%endif
exit 0

%changelog
* Thu Jul 18 2019 Alfredo Moralejo <amoralej@redhat.com> - 6.6.0-2
- Added rubygem(puppet-resource_api) as requirement.

* Fri Jul 12 2019 Alfredo Moralejo <amoralej@redhat.com> - 6.6.0-1
- Update to 6.6.0
- Removed subpackage puppet-server.

* Wed May 08 2019 Yatin Karel <ykarel@redhat.com> - 6.4.1-1
- Update to 6.4.1
- Remove unnecessary patches with 6.4.1 Move

* Wed Mar 13 2019 Terje Rosten <terje.rosten@ntnu.no> - 5.5.10-4
- Minor clean up

* Thu Mar 07 2019 Terje Rosten <terje.rosten@ntnu.no> - 5.5.10-3
- Move sysconfdirs to headless too

* Thu Mar 07 2019 Terje Rosten <terje.rosten@ntnu.no> - 5.5.10-2
- Move reqs to headless

* Thu Mar 07 2019 Terje Rosten <terje.rosten@ntnu.no> - 5.5.10-1
- 5.5.10

* Thu Mar 07 2019 Terje Rosten <terje.rosten@ntnu.no> - 5.5.6-6
- Split off headless subpackage, based on idea from Bogdan Dobrelya

* Sun Feb 17 2019 Bogdan Dobrelya <bdobreli@redhat.com> - 5.5.6-5
- Revert use of systemd_ordering macro

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.5.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Jan 22 2019 Bogdan Dobrelya <bdobreli@redhat.com> - 5.5.6-3
- Use systemd_ordering macro

* Wed Oct 31 2018 Haïkel Guémar <hguemar@fedoraproject.org> - 5.5.6-1
- Upstream 5.5.6
- Fix issues with RHEL > 7

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue May  8 2018 Haïkel Guémar <hguemar@fedoraproject.org> - 5.5.1-1
- Upstream 5.5.1
- Unmaintained editor extensions were removed upstream (PUP-7558)
- Deprecated commands were removed: inspect (PUP-893), extlookup2hiera (PUP-3478)
- Refreshed patches

* Thu Mar 15 2018 Terje Rosten <terje.rosten@ntnu.no> - 4.10.10-1
- Update to 4.10.10

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.10.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Nov 07 2017 James Hogarth <james.hogarth@gmail.com> - 4.10.1-3
- F28 facter3 change means puppet needs to require the ruby bindings for facter

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed May 31 2017 Dominic Cleal <dominic@cleal.org> - 4.10.1-1
- Update to 4.10.1

* Wed May 31 2017 Dominic Cleal <dominic@cleal.org> - 4.8.2-2
- Remove Fedora release restrictions from DNF package provider

* Thu May 25 2017 Dominic Cleal <dominic@cleal.org> - 4.8.2-1
- Update to 4.8.2

* Tue May 23 2017 Ville Skyttä <ville.skytta@iki.fi> - 4.6.2-5
- Move tmpfiles.d config to %%{_tmpfilesdir}
- Install LICENSE as %%license

* Tue May 23 2017 Dominic Cleal <dominic@cleal.org> - 4.6.2-4
- Fix remote code exec via YAML deserialization (BZ#1452654, CVE-2017-2295)

* Thu May 18 2017 Dominic Cleal <dominic@cleal.org> - 4.6.2-3
- Fix Ruby 2.4 compatibility, xmlrpc + OpenSSL errors (BZ#1443673, BZ#1440710)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.6.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Sep 13 2016 Haïkel Guémar <hguemar@fedoraproject.org> - 4.6.2-1
- Upstream 4.6.2

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jul 29 2015 Gael Chamoulaud <gchamoul@redhat.com> - 4.2.1-2
- Remove usage of vendored library safe_yaml (rhbz#1261091)

* Wed Jul 29 2015 Gael Chamoulaud <gchamoul@redhat.com> - 4.2.1-1
- Upstream 4.2.1

* Tue Jul 28 2015 Lukas Zapletal <lzap+rpm@redhat.com> 4.1.0-4
- 1246238 - systemd service type changed to 'simple'

* Tue Jul 21 2015 Lukas Zapletal <lzap+rpm@redhat.com> 4.1.0-3
- Puppet agent is started via exec rather than sub-process

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 23 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 4.1.0-1
- Upstream 4.1.0
- Fix Puppet belief that Fedora is OpenBSD (PUP-4491)

* Sun May 17 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 4.0.0-2
- Fix puppet paths and unit files (upstream #12185)

* Tue Apr 28 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 4.0.0-1
- Upstream 4.0.0

* Mon Apr 27 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 4.0.0-0.1rc1
- Upstream 4.0.0
- Fix issue codedir path
- Fix init provider for Fedora (systemd is default on all supported releases now)

* Wed Apr 22 2015 Orion Poplawski <orion@cora.nwra.com> - 3.7.5-4
- Do not unbundle puppet's semantic module

* Sun Apr 19 2015 Orion Poplawski <orion@cora.nwra.com> - 3.7.5-3
- Require rubygem(pathspec) and rubygem(semantic)

* Tue Mar 31 2015 Orion Poplawski <orion@cora.nwra.com> - 3.7.5-2
- Unbundle libs (bug #1198366)

* Tue Mar 31 2015 Orion Poplawski <orion@cora.nwra.com> - 3.7.5-1
- Update to 3.7.5

* Sat Feb 28 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 3.7.1-3
- Use systemd macros (RHBZ #1197239)

* Tue Sep 30 2014 Orion Poplawski <orion@cora.nwra.com> - 3.7.1-2
- Drop server deps and configuration changes (bug #1144298)

* Wed Sep 17 2014 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 3.7.1-1
- Update to 3.7.1

* Tue Aug 19 2014 Lukas Zapletal <lzap+rpm@redhat.com> 3.6.2-3
- 1131398 - added start-puppet-ca SELinux wrapper binary

* Mon Jun 30 2014 Pádraig Brady <pbrady@redhat.com> - 3.6.2-2
- Allow yumrepo proxy attribute to be set to _none_

* Mon Jun 16 2014 Orion Poplawski <orion@cora.nwra.com> - 3.6.2-1
- Update to 3.6.2

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun May 18 2014 Sam Kottler <skottler@fedoraproject.org> 3.6.0-1
- Remove logic specific to unsupported versions of Fedora
- Update to 3.6.0

* Mon Apr 28 2014 Sam Kottler <skottler@fedoraproject.org> 3.5.1-1
- Update to 3.5.1

* Tue Apr 08 2014 Lukas Zapletal <lzap+rpm@redhat.com> 3.4.3-3
- RHBZ#1070395 - fixed error in postun scriplet
- Reformatted all scriplets and corrected exit codes

* Tue Apr 08 2014 Lukas Zapletal <lzap+rpm@redhat.com> 3.4.3-2
- Fixed systemd unit files - wrappers are now in use and master starts
  with correct context

* Mon Feb 24 2014 Sam Kottler <skottler@fedoraproject.org> - 3.4.3-1
- Update to 3.4.3

* Wed Jan 29 2014 Sam Kottler <skottler@fedoraproject.org> - 3.4.2-5
- Add rubygem(rgen) runtime dependency

* Thu Jan 23 2014 Sam Kottler <skottler@fedoraproject.org> - 3.4.2-4
- Use localstatedir macro instead of /tmp

* Fri Jan 17 2014 Sam Kottler <skottler@fedoraproject.org> - 3.4.2-3
- Enable puppet.service during upgrade if puppetagent.service was previously enabled

* Thu Jan 16 2014 Sam Kottler <skottler@fedoraproject.org> - 3.4.2-2
- Remove F18 conditionals now that it's EOL

* Tue Jan 14 2014 Sam Kottler <skottler@fedoraproject.org> - 3.4.2-1
- Update to 3.4.2 to mitigate CVE-2013-4969 (BZ#1047792)

* Mon Nov 18 2013 Sam Kottler <skottler@fedoraproject.org> - 3.3.2-1
- Update to 3.3.2 (BZ#1031810)

* Sat Nov 16 2013 Sam Kottler <skottler@fedoraproject.org> - 3.3.1-3
- Add patch to convert nil resource parameter values to undef (BZ#1028930)

* Fri Nov 1 2013 Lukas Zapletal <lzap+rpm[@]redhat.com> - 3.3.1-2
- Added SELinux wrappers for daemon processes

* Mon Oct 7 2013 Orion Poplawski <orion@cora.nwra.com> - 3.3.1-1
- Update to 3.3.1

* Fri Sep 13 2013 Sam Kottler <skottler@fedoraproject.org> - 3.3.0-1
- Update to 3.3.0 and remove the rundir-perms patch since it's no longer needed

* Fri Aug 30 2013 Sam Kottler <skottler@fedoraproject.org> - 3.2.4-1
- Update to 3.2.4 to fix CVE-2013-4761 and CVE-2013-4956

* Thu Aug 29 2013 Sam Kottler <skottler@fedoraproject.org> - 3.2.2-1
- Update to 3.2.2

* Wed Aug 7 2013 Sam Kottler <skottler@fedoraproject.org> - 3.1.1-6
- Add tar as an installation requirement

* Tue Jul 30 2013 Orion Poplawski <orion@cora.nwra.com> - 3.1.1-5
- Use systemd semantics and name in NM dispatcher script

* Fri Jul 26 2013 Sam Kottler <skottler@fedoraproject.org> - 3.1.1-4
- Add hard dependency on ruby

* Tue Apr 16 2013 Orion Poplawski <orion@cora.nwra.com> - 3.1.1-3
- Add upstream patch for ruby 2.0 support
- Fix rhel ruby conditional

* Fri Mar 15 2013 Vít Ondruch <vondruch@redhat.com> - 3.1.1-2
- Rebuild for https://fedoraproject.org/wiki/Features/Ruby_2.0.0

* Wed Mar 13 2013 Michael Stahnke <stahnma@puppetlabs.com> - 3.1.1-1
- Fixes for CVE-2013-1640 CVE-2013-1652 CVE-2013-1653 CVE-2013-1654
- CVE-2013-1655 CVE-2013-2274 CVE-2013-2275

* Thu Mar 07 2013 Michael Stahnke <stahnma@puppetlabs.com> - 3.1.0-4
- Disable systemd in F18 as per bz#873853
- Update Patch0 to work with 3.1

* Thu Mar  7 2013 Daniel Drake <dsd@laptop.org> - 3.1.0-2
- Improve server compatibility with old puppet clients (#831303)

* Mon Feb 11 2013 Sam Kottler <shk@redhat.com> - 3.1.0-1
- Update to 3.1.0

* Tue Oct 30 2012 Moses Mendoza <moses@puppetlabs.com> - 3.0.2-1
- Update to 3.0.2
- Update new dependencies (ruby >= 1.8.7, facter >= 1.6.6, hiera >= 1.0.0)
- Update for manpage and file changes in upstream
- Add conditionals for systemd service management
- Remove 0001-Ruby-1.9.3-has-a-different-error-when-require-fails.patch
- Remove 0001-Preserve-timestamps-when-installing-files.patch

* Wed Jul 11 2012 Todd Zullinger <tmz@pobox.com> - 2.7.18-1
- Update to 2.7.17, fixes CVE-2012-3864, CVE-2012-3865, CVE-2012-3866,
  CVE-2012-3867
- Improve NetworkManager compatibility, thanks to Orion Poplawski (#532085)
- Preserve timestamps when installing files

* Wed Apr 25 2012 Todd Zullinger <tmz@pobox.com> - 2.7.13-1
- Update to 2.7.13
- Change license from GPLv2 to ASL 2.0
- Drop %%post hacks to deal with upgrades from 0.25
- Minor rpmlint fixes
- Backport patch to silence confine warnings in ruby-1.9.3

* Wed Apr 11 2012 Todd Zullinger <tmz@pobox.com> - 2.6.16-1
- Update to 2.6.16, fixes CVE-2012-1986, CVE-2012-1987, and CVE-2012-1988
- Correct permissions of /var/log/puppet (0750)

* Wed Feb 22 2012 Todd Zullinger <tmz@pobox.com> - 2.6.14-1
- Update to 2.6.14, fixes CVE-2012-1053 and CVE-2012-1054

* Mon Feb 13 2012 Todd Zullinger <tmz@pobox.com> - 2.6.13-3
- Move rpmlint fixes to %%prep, add a few additional fixes
- Bump minimum ruby version to 1.8.5 now that EL-4 is all but dead
- Update install locations for Fedora-17 / Ruby-1.9
- Use ruby($lib) for augeas and shadow requirements
- Only try to run 0.25.x -> 2.6.x pid file updates on EL

* Thu Jan 05 2012 Todd Zullinger <tmz@pobox.com> - 2.6.13-2
- Revert to minimal patch for augeas >= 0.10 (bz#771097)

* Wed Dec 14 2011 Todd Zullinger <tmz@pobox.com> - 2.6.13-1
- Update to 2.6.13
- Cherry-pick various augeas fixes from upstream (bz#771097)

* Sun Oct 23 2011 Todd Zullinger <tmz@pobox.com> - 2.6.12-1
- Update to 2.6.12, fixes CVE-2011-3872
- Add upstream patch to restore Mongrel XMLRPC functionality (upstream #10244)
- Apply partial fix for upstream #9167 (tagmail report sends email when nothing
  happens)

* Thu Sep 29 2011 Todd Zullinger <tmz@pobox.com> - 2.6.6-3
- Apply upstream patches for CVE-2011-3869, CVE-2011-3870, CVE-2011-3871, and
  upstream #9793

* Tue Sep 27 2011 Todd Zullinger <tmz@pobox.com> - 2.6.6-2
- Apply upstream patch for CVE-2011-3848

* Wed Mar 16 2011 Todd Zullinger <tmz@pobox.com> - 2.6.6-1
- Update to 2.6.6
- Ensure %%pre exits cleanly
- Fix License tag, puppet is now GPLv2 only
- Create and own /usr/share/puppet/modules (#615432)
- Properly restart puppet agent/master daemons on upgrades from 0.25.x
- Require libselinux-utils when selinux support is enabled
- Support tmpfiles.d for Fedora >= 15 (#656677)
- Apply a few upstream fixes for 0.25.5 regressions

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.25.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon May 17 2010 Todd Zullinger <tmz@pobox.com> - 0.25.5-1
- Update to 0.25.5
- Adjust selinux conditional for EL-6
- Apply rundir-perms patch from tarball rather than including it separately
- Update URL's to reflect the new puppetlabs.com domain

* Fri Jan 29 2010 Todd Zullinger <tmz@pobox.com> - 0.25.4-1
- Update to 0.25.4

* Tue Jan 19 2010 Todd Zullinger <tmz@pobox.com> - 0.25.3-2
- Apply upstream patch to fix cron resources (upstream #2845)

* Mon Jan 11 2010 Todd Zullinger <tmz@pobox.com> - 0.25.3-1
- Update to 0.25.3

* Tue Jan 05 2010 Todd Zullinger <tmz@pobox.com> - 0.25.2-1.1
- Replace %%define with %%global for macros

* Tue Jan 05 2010 Todd Zullinger <tmz@pobox.com> - 0.25.2-1
- Update to 0.25.2
- Fixes CVE-2010-0156, tmpfile security issue (#502881)
- Install auth.conf, puppetqd manpage, and queuing examples/docs

* Wed Nov 25 2009 Jeroen van Meeuwen <j.van.meeuwen@ogd.nl> - 0.25.1-1
- New upstream version

* Tue Oct 27 2009 Todd Zullinger <tmz@pobox.com> - 0.25.1-0.3
- Update to 0.25.1
- Include the pi program and man page (R.I.Pienaar)

* Sat Oct 17 2009 Todd Zullinger <tmz@pobox.com> - 0.25.1-0.2.rc2
- Update to 0.25.1rc2

* Tue Sep 22 2009 Todd Zullinger <tmz@pobox.com> - 0.25.1-0.1.rc1
- Update to 0.25.1rc1
- Move puppetca to puppet package, it has uses on client systems
- Drop redundant %%doc from manpage %%file listings

* Fri Sep 04 2009 Todd Zullinger <tmz@pobox.com> - 0.25.0-1
- Update to 0.25.0
- Fix permissions on /var/log/puppet (#495096)
- Install emacs mode and vim syntax files (#491437)
- Install ext/ directory in %%{_datadir}/%%{name} (/usr/share/puppet)

* Mon May 04 2009 Todd Zullinger <tmz@pobox.com> - 0.25.0-0.1.beta1
- Update to 0.25.0beta1
- Make Augeas and SELinux requirements build time options

* Mon Mar 23 2009 Todd Zullinger <tmz@pobox.com> - 0.24.8-1
- Update to 0.24.8
- Quiet output from %%pre
- Use upstream install script
- Increase required facter version to >= 1.5

* Tue Dec 16 2008 Todd Zullinger <tmz@pobox.com> - 0.24.7-4
- Remove redundant useradd from %%pre

* Tue Dec 16 2008 Jeroen van Meeuwen <kanarip@kanarip.com> - 0.24.7-3
- New upstream version
- Set a static uid and gid (#472073, #471918, #471919)
- Add a conditional requirement on libselinux-ruby for Fedora >= 9
- Add a dependency on ruby-augeas

* Wed Oct 22 2008 Todd Zullinger <tmz@pobox.com> - 0.24.6-1
- Update to 0.24.6
- Require ruby-shadow on Fedora and RHEL >= 5
- Simplify Fedora/RHEL version checks for ruby(abi) and BuildArch
- Require chkconfig and initstripts for preun, post, and postun scripts
- Conditionally restart puppet in %%postun
- Ensure %%preun, %%post, and %%postun scripts exit cleanly
- Create puppet user/group according to Fedora packaging guidelines
- Quiet a few rpmlint complaints
- Remove useless %%pbuild macro
- Make specfile more like the Fedora/EPEL template

* Mon Jul 28 2008 David Lutterkort <dlutter@redhat.com> - 0.24.5-1
- Add /usr/bin/puppetdoc

* Thu Jul 24 2008 Brenton Leanhardt <bleanhar@redhat.com>
- New version
- man pages now ship with tarball
- examples/code moved to root examples dir in upstream tarball

* Tue Mar 25 2008 David Lutterkort <dlutter@redhat.com> - 0.24.4-1
- Add man pages (from separate tarball, upstream will fix to
  include in main tarball)

* Mon Mar 24 2008 David Lutterkort <dlutter@redhat.com> - 0.24.3-1
- New version

* Wed Mar  5 2008 David Lutterkort <dlutter@redhat.com> - 0.24.2-1
- New version

* Sat Dec 22 2007 David Lutterkort <dlutter@redhat.com> - 0.24.1-1
- New version

* Mon Dec 17 2007 David Lutterkort <dlutter@redhat.com> - 0.24.0-2
- Use updated upstream tarball that contains yumhelper.py

* Fri Dec 14 2007 David Lutterkort <dlutter@redhat.com> - 0.24.0-1
- Fixed license
- Munge examples/ to make rpmlint happier

* Wed Aug 22 2007 David Lutterkort <dlutter@redhat.com> - 0.23.2-1
- New version

* Thu Jul 26 2007 David Lutterkort <dlutter@redhat.com> - 0.23.1-1
- Remove old config files

* Wed Jun 20 2007 David Lutterkort <dlutter@redhat.com> - 0.23.0-1
- Install one puppet.conf instead of old config files, keep old configs
  around to ease update
- Use plain shell commands in install instead of macros

* Wed May  2 2007 David Lutterkort <dlutter@redhat.com> - 0.22.4-1
- New version

* Thu Mar 29 2007 David Lutterkort <dlutter@redhat.com> - 0.22.3-1
- Claim ownership of _sysconfdir/puppet (bz 233908)

* Mon Mar 19 2007 David Lutterkort <dlutter@redhat.com> - 0.22.2-1
- Set puppet's homedir to /var/lib/puppet, not /var/puppet
- Remove no-lockdir patch, not needed anymore

* Mon Feb 12 2007 David Lutterkort <dlutter@redhat.com> - 0.22.1-2
- Fix bogus config parameter in puppetd.conf

* Sat Feb  3 2007 David Lutterkort <dlutter@redhat.com> - 0.22.1-1
- New version

* Fri Jan  5 2007 David Lutterkort <dlutter@redhat.com> - 0.22.0-1
- New version

* Mon Nov 20 2006 David Lutterkort <dlutter@redhat.com> - 0.20.1-2
- Make require ruby(abi) and buildarch: noarch conditional for fedora 5 or
  later to allow building on older fedora releases

* Mon Nov 13 2006 David Lutterkort <dlutter@redhat.com> - 0.20.1-1
- New version

* Mon Oct 23 2006 David Lutterkort <dlutter@redhat.com> - 0.20.0-1
- New version

* Tue Sep 26 2006 David Lutterkort <dlutter@redhat.com> - 0.19.3-1
- New version

* Mon Sep 18 2006 David Lutterkort <dlutter@redhat.com> - 0.19.1-1
- New version

* Thu Sep  7 2006 David Lutterkort <dlutter@redhat.com> - 0.19.0-1
- New version

* Tue Aug  1 2006 David Lutterkort <dlutter@redhat.com> - 0.18.4-2
- Use /usr/bin/ruby directly instead of /usr/bin/env ruby in
  executables. Otherwise, initscripts break since pidof can't find the
  right process

* Tue Aug  1 2006 David Lutterkort <dlutter@redhat.com> - 0.18.4-1
- New version

* Fri Jul 14 2006 David Lutterkort <dlutter@redhat.com> - 0.18.3-1
- New version

* Wed Jul  5 2006 David Lutterkort <dlutter@redhat.com> - 0.18.2-1
- New version

* Wed Jun 28 2006 David Lutterkort <dlutter@redhat.com> - 0.18.1-1
- Removed lsb-config.patch and yumrepo.patch since they are upstream now

* Mon Jun 19 2006 David Lutterkort <dlutter@redhat.com> - 0.18.0-1
- Patch config for LSB compliance (lsb-config.patch)
- Changed config moves /var/puppet to /var/lib/puppet, /etc/puppet/ssl
  to /var/lib/puppet, /etc/puppet/clases.txt to /var/lib/puppet/classes.txt,
  /etc/puppet/localconfig.yaml to /var/lib/puppet/localconfig.yaml

* Fri May 19 2006 David Lutterkort <dlutter@redhat.com> - 0.17.2-1
- Added /usr/bin/puppetrun to server subpackage
- Backported patch for yumrepo type (yumrepo.patch)

* Wed May  3 2006 David Lutterkort <dlutter@redhat.com> - 0.16.4-1
- Rebuilt

* Fri Apr 21 2006 David Lutterkort <dlutter@redhat.com> - 0.16.0-1
- Fix default file permissions in server subpackage
- Run puppetmaster as user puppet
- rebuilt for 0.16.0

* Mon Apr 17 2006 David Lutterkort <dlutter@redhat.com> - 0.15.3-2
- Don't create empty log files in post-install scriptlet

* Fri Apr  7 2006 David Lutterkort <dlutter@redhat.com> - 0.15.3-1
- Rebuilt for new version

* Wed Mar 22 2006 David Lutterkort <dlutter@redhat.com> - 0.15.1-1
- Patch0: Run puppetmaster as root; running as puppet is not ready
  for primetime

* Mon Mar 13 2006 David Lutterkort <dlutter@redhat.com> - 0.15.0-1
- Commented out noarch; requires fix for bz184199

* Mon Mar  6 2006 David Lutterkort <dlutter@redhat.com> - 0.14.0-1
- Added BuildRequires for ruby

* Wed Mar  1 2006 David Lutterkort <dlutter@redhat.com> - 0.13.5-1
- Removed use of fedora-usermgmt. It is not required for Fedora Extras and
  makes it unnecessarily hard to use this rpm outside of Fedora. Just
  allocate the puppet uid/gid dynamically

* Sun Feb 19 2006 David Lutterkort <dlutter@redhat.com> - 0.13.0-4
- Use fedora-usermgmt to create puppet user/group. Use uid/gid 24. Fixed
problem with listing fileserver.conf and puppetmaster.conf twice

* Wed Feb  8 2006 David Lutterkort <dlutter@redhat.com> - 0.13.0-3
- Fix puppetd.conf

* Wed Feb  8 2006 David Lutterkort <dlutter@redhat.com> - 0.13.0-2
- Changes to run puppetmaster as user puppet

* Mon Feb  6 2006 David Lutterkort <dlutter@redhat.com> - 0.13.0-1
- Don't mark initscripts as config files

* Mon Feb  6 2006 David Lutterkort <dlutter@redhat.com> - 0.12.0-2
- Fix BuildRoot. Add dist to release

* Tue Jan 17 2006 David Lutterkort <dlutter@redhat.com> - 0.11.0-1
- Rebuild

* Thu Jan 12 2006 David Lutterkort <dlutter@redhat.com> - 0.10.2-1
- Updated for 0.10.2 Fixed minor kink in how Source is given

* Wed Jan 11 2006 David Lutterkort <dlutter@redhat.com> - 0.10.1-3
- Added basic fileserver.conf

* Wed Jan 11 2006 David Lutterkort <dlutter@redhat.com> - 0.10.1-1
- Updated. Moved installation of library files to sitelibdir. Pulled
initscripts into separate files. Folded tools rpm into server

* Thu Nov 24 2005 Duane Griffin <d.griffin@psenterprise.com>
- Added init scripts for the client

* Wed Nov 23 2005 Duane Griffin <d.griffin@psenterprise.com>
- First packaging
