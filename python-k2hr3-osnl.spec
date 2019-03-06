%global srcname k2hr3_osnl
%global pypi_name k2hr3-osnl
Name:		python-k2hr3-osnl
Version:	0.9.0
Release:	1%{?dist}
Summary:	An OpenStack notification listener for K2HR3

License:	MIT
URL:		https://github.com/yahoojapan/%{srcname}
Source0:	https://github.com/yahoojapan/%{srcname}/archive/%{version}/%{srcname}-%{version}.tar.gz

BuildArch:	noarch

%description
k2hr3_osnl is an OpenStack Notification Listener, which listens to 
notifications from OpenStack services. When catching a notification, it 
sends the notification payload to K2HR3, the OpenStack role-based ACL 
system developed by Yahoo Japan Corporation.

%package -n python3-%{pypi_name}
Summary:	%{summary}
BuildRequires:	git
BuildRequires:	python3-devel
BuildRequires:	python3-oslo-config
BuildRequires:	python3-oslo-messaging
BuildRequires:	help2man
%if 0%{?fedora} >= 30
BuildRequires:	systemd-rpm-macros
%endif 
%{?systemd_requires}
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:	python3-oslo-messaging >= 5.17.1
Requires:	python3-oslo-config >= 5.2.0

%description -n python3-%{pypi_name}
k2hr3_osnl is an OpenStack Notification Listener, which listens to 
notifications from OpenStack services. When catching a notification, it 
sends the notification payload to K2HR3, the OpenStack role-based ACL 
system developed by Yahoo Japan Corporation.

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
mkdir -p %{buildroot}%{_sysconfdir}/k2hr3
install -pm 644 etc/k2hr3-osnl.conf %{buildroot}%{_sysconfdir}/k2hr3/k2hr3-osnl.conf
mkdir -p %{buildroot}%{_unitdir}
install -pm 644 k2hr3-osnl.service %{buildroot}%{_unitdir}/k2hr3-osnl.service
rm -rf %{buildroot}/usr/etc/k2hr3/k2hr3-osnl.conf
mkdir -p %{buildroot}%{_mandir}/man1
help2man --no-discard-stderr --version-string=%{version} bin/k2hr3-osnl >%{buildroot}%{_mandir}/man1/k2hr3-osnl.1

%check
%{__python3} -m unittest

%files -n python3-%{pypi_name}
%doc README.rst
%license LICENSE
%{_bindir}/k2hr3-osnl
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/*.egg-info
%{_sysconfdir}/k2hr3
%{_unitdir}/k2hr3-osnl.service
%{_mandir}/man1/k2hr3-osnl.1

%changelog
* Sun Mar  6 2019 Hirotaka Wakabayashi <hiwakaba@yahoo-corp.jp> 0.9.0-1
- Initial Version

