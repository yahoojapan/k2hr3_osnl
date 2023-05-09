%global srcname k2hr3_osnl
%global pypi_name k2hr3-osnl
Name:		python-k2hr3-osnl
Version:	1.0.5
Release:	%autorelease
Summary:	An OpenStack notification listener for K2HR3

License:	MIT
URL:		https://github.com/yahoojapan/%{srcname}
Source0:	https://github.com/yahoojapan/%{srcname}/archive/v%{version}/%{srcname}-%{version}.tar.gz

BuildArch:	noarch

%description
k2hr3_osnl is an OpenStack Notification Listener, which listens to 
notifications from OpenStack services. When catching a notification, it 
sends the notification payload to K2HR3, the OpenStack role-based ACL 
system developed by Yahoo Japan Corporation

%package -n python3-%{pypi_name}
Summary:	%{summary}
BuildRequires:	git
BuildRequires:	python3-devel
BuildRequires:	python3-oslo-config
BuildRequires:	python3-oslo-messaging
BuildRequires:	help2man
%if 0%{?fedora} >= 30
BuildRequires:	systemd-rpm-macros
%else
BuildRequires:	systemd
%endif 
%{?systemd_requires}
%{?python_provide:%python_provide python3-%{pypi_name}}

# python3-oslo-messaging found. python3x-oslo-messaging not found.
# Tested with OpenStack rocky on fc29
Requires:	python3-oslo-messaging >= 5.35.1
Requires:	python3-oslo-config >= 5.2.0

%description -n python3-%{pypi_name}
k2hr3_osnl is an OpenStack Notification Listener, which listens to 
notifications from OpenStack services. When catching a notification, it 
sends the notification payload to K2HR3, the OpenStack role-based ACL 
system developed by Yahoo Japan Corporation

%prep
%autosetup -n %{srcname}-%{version} -S git

%post
%systemd_post k2hr3-osnl.service

%preun
%systemd_preun k2hr3-osnl.service

%postun
%systemd_postun_with_restart k2hr3-osnl.service

%build
%py3_build

%install
%py3_install
mkdir -p -m755 %{buildroot}%{_sysconfdir}/k2hr3
mkdir -p -m755 %{buildroot}%{_unitdir}
mkdir -p -m755 %{buildroot}%{_mandir}/man1
install -pm 644 etc/k2hr3-osnl.conf %{buildroot}%{_sysconfdir}/k2hr3/k2hr3-osnl.conf
install -pm 644 k2hr3-osnl.service %{buildroot}%{_unitdir}/k2hr3-osnl.service
help2man --no-discard-stderr --version-string=%{version} %{buildroot}%{_bindir}/k2hr3-osnl > %{buildroot}%{_mandir}/man1/k2hr3-osnl.1
rm -rf %{buildroot}/usr/etc/k2hr3/k2hr3-osnl.conf

%check
%{__python3} -m unittest

%files -n python3-%{pypi_name}
%dir %{_sysconfdir}/k2hr3/
%config(noreplace) %{_sysconfdir}/k2hr3/k2hr3-osnl.conf
%doc README.rst
%license LICENSE
%{_bindir}/k2hr3-osnl
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/*.egg-info
%{_unitdir}/k2hr3-osnl.service
%{_mandir}/man1/k2hr3-osnl.1*

%changelog
%autochangelog
