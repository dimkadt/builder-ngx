%define nginx_name      nginx
%define nginx_user      nginx
%define nginx_group     %{nginx_user}
%define nginx_home      %{_localstatedir}/lib/nginx
%define nginx_home_tmp  %{nginx_home}/tmp
%define nginx_logdir    %{_localstatedir}/log/nginx
%define nginx_confdir   %{_sysconfdir}/nginx
%define nginx_datadir   %{_datadir}/nginx
%define nginx_webroot   %{nginx_datadir}/html
%define _rpmfilename %%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm
%define modsecurity_apache 2.9.1
Name:           nginx-app
Version:        1.11.13
Release:        6%{?dist}
Summary:        Robust, small and high performance http and reverse proxy server
Group:          System Environment/Daemons

License:        BSD
URL:            http://nginx.net/
BuildRoot:      %{_tmppath}/%{nginx_name}-%{version}-%{release}-root-%(%{__id_u} -n)
#BuildRoot:      %{_tmppath}/nginx-%{version}-%{release}-root-%(%{__id_u} -n)
#%define buildroot      %{_buildrootdir}/%{nginx_name}-%{version}-%{release}.%{_arch}

BuildRequires:      gd,gd-devel,libtool,libxslt-devel,httpd-devel,perl-Exporter,libcurl-devel,libxml2-devel,pam-devel,pcre-devel,zlib-devel,openssl-devel,perl(ExtUtils::Embed),GeoIP-devel,lua,lua-devel,yajl,yajl-devel,ssdeep,ssdeep-devel
Requires:           pcre,zlib,openssl
Requires:           GeoIP
Requires:           perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires(pre):      shadow-utils
Requires(post):     chkconfig
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts

Source0:        http://nginx.org/download/nginx-1.11.13.tar.gz
#Source0:        http://nginx.org/download/nginx-1.12.0.tar.gz
Source1:        %{nginx_name}.init
Source2:        %{nginx_name}.logrotate
Source3:        virtual.conf
Source4:        ssl.conf
Source5:        modsecurity-%{modsecurity_apache}.tar.gz
Source7:        %{nginx_name}.sysconfig
#Source21:       GeoIPCountryCSV.zip
Source23:	GeoLiteCity.dat
Source100:      index.html
Source103:      50x.html
Source104:      404.html
Source200:      nginx.pam
Source300:      nginx-sticky-module-ng.zip
#Source301:	nginx_tcp_proxy_module.zip
Source302:	nginx-dav-ext-module.zip
#%define 	headers-more-nginx-module 0.25
Source310:	ext-headers-more-nginx-module-master.zip
Source320:	naxsi.zip
Source321:	nx_util.conf
Source333:      nginx_upstream_check_module.zip
Source555:	njs.zip
#Patch0:         nginx-auto-cc-gcc.patch
##Patch1:         nginx-config.patch
#Patch0:		tcp.1.11.13.patch
#Patch1:		patch-tcp-status.patch

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev.

Following third party modules added:
* nginx-upstream-fair
* mod_zip
* ngx_http_auth_pam_module


%prep
%setup -n nginx-%{version}
###%patch0 -p0
##%patch1 -p0
%{__tar} zxf %{SOURCE5}
/usr/bin/unzip %{SOURCE300}
#/usr/bin/unzip %{SOURCE301}
/usr/bin/unzip %{SOURCE302}
/usr/bin/unzip %{SOURCE310}
/usr/bin/unzip %{SOURCE320}
/usr/bin/unzip %{SOURCE333}
/usr/bin/unzip %{SOURCE555}
#%setup -T -D -a 21
#%patch0 -p1
#%patch1 -p1

cd %{_builddir}/%{nginx_name}-%{version}/modsecurity-%{modsecurity_apache}/
patch -p1 <  %{_sourcedir}/modsecurity-p1.patch
./autogen.sh
./configure --enable-standalone-module
make

cd %{_builddir}/%{nginx_name}-%{version}
#patch -p1 <  %{_builddir}/%{nginx_name}-%{version}/nginx_tcp_proxy_module-master/tcp_1_8.patch
%build
%define debug_package %{nil}

# Convert GeoIP
#perl contrib/geo2nginx.pl < GeoIPCountryWhois.csv > geo.data

# Rename dir
#mv masterzen-nginx-upload-progress-module-3d8e105 nginx-upload-progress-module

# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.  The configure script(s) have been patched (Patch1 and
# Patch2) in order to support installing into a build environment.
export DESTDIR=%{buildroot}
./configure \
    --add-module=%{_builddir}/%{nginx_name}-%{version}/naxsi-master/naxsi_src \
    --user=%{nginx_user} \
    --group=%{nginx_group} \
    --prefix=%{nginx_datadir} \
    --sbin-path=%{_sbindir}/%{nginx_name} \
    --conf-path=%{nginx_confdir}/%{nginx_name}.conf \
    --error-log-path=%{nginx_logdir}/error.log \
    --http-log-path=%{nginx_logdir}/access.log \
    --http-client-body-temp-path=%{nginx_home_tmp}/client_body \
    --http-proxy-temp-path=%{nginx_home_tmp}/proxy \
    --http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
    --http-uwsgi-temp-path=%{nginx_home_tmp}/uwsgi \
    --http-scgi-temp-path=%{nginx_home_tmp}/scgi \
    --pid-path=%{_localstatedir}/run/%{nginx_name}.pid \
    --lock-path=%{_localstatedir}/lock/subsys/%{nginx_name} \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_flv_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_gzip_static_module \
    --with-http_v2_module \
    --with-http_slice_module \
    --add-module=%{_builddir}/%{nginx_name}-%{version}/nginx-goodies-nginx-sticky-module-ng-08a395c66e42 \
    --add-module=%{_builddir}/%{nginx_name}-%{version}/nginx-dav-ext-module-master \
    --add-module=%{_builddir}/%{nginx_name}-%{version}/headers-more-nginx-module-master \
    --add-module=%{_builddir}/%{nginx_name}-%{version}/nginx_upstream_check_module-master \
    --add-module=%{_builddir}/%{nginx_name}-%{version}/modsecurity-%{modsecurity_apache}/nginx/modsecurity/ \
    --with-file-aio \
    --with-http_addition_module \
    --with-http_mp4_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-http_geoip_module=dynamic \
    --with-http_image_filter_module=dynamic \
    --with-http_xslt_module=dynamic \
    --with-mail=dynamic \
    --add-dynamic-module=%{_builddir}/%{nginx_name}-%{version}/njs-master/nginx
make
#    --with-ipv6 \
#    --add-module=%{_builddir}/%{nginx_name}-%{version}/nginx_tcp_proxy_module-master \

#cd naxsi-master/nxapi/
#python setup.py build
#python setup.py install --root %{buildroot} --install-data /usr/local
#%{__install} -p -D -m 0644 %{SOURCE321} %{buildroot}/usr/local/etc/


#mv nginx-upstream-fair/README nginx-upstream-fair/README.nginx-upstream-fair

#mv nginx_upload_module-2.2.0/Changelog nginx_upload_module-2.2.0/Changelog.nginx_upload_module
#mv nginx_upload_module-2.2.0/example.php nginx_upload_module-2.2.0/example.php.nginx_upload_module
#mv nginx_upload_module-2.2.0/nginx.conf nginx_upload_module-2.2.0/nginx.conf.nginx_upload_module
#mv nginx_upload_module-2.2.0/upload.html nginx_upload_module-2.2.0/upload.html.nginx_upload_module

#mv mod_zip-1.1.6/CHANGES mod_zip-1.1.6/CHANGES.mod_zip
#mv mod_zip-1.1.6/README mod_zip-1.1.6/README.mod_zip
#mv mod_zip-1.1.6/t/nginx.conf mod_zip-1.1.6/t/nginx.conf.mod_zip

#mv nginx-upload-progress-module/CHANGES nginx-upload-progress-module/CHANGES.nginx_uploadprogress_module
#mv nginx-upload-progress-module/README nginx-upload-progress-module/README.nginx_uploadprogress_module

#mv ngx_http_auth_pam_module-1.2/ChangeLog ngx_http_auth_pam_module-1.2/ChangeLog.ngx_http_auth_pam_module-1.2
#mv ngx_http_auth_pam_module-1.2/README ngx_http_auth_pam_module-1.2/README.ngx_http_auth_pam_module-1.2


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor
find %{buildroot} -type f -name .packlist -exec rm -f {} \;
#find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
find %{buildroot} -type f -exec chmod 0644 {} \;
find %{buildroot} -type f -name '*.so' -exec chmod 0755 {} \;
chmod 0755 %{buildroot}%{_sbindir}/nginx
%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{nginx_name}
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{nginx_name}
%{__install} -p -D -m 0644 %{SOURCE7} %{buildroot}%{_sysconfdir}/sysconfig/%{nginx_name}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
#%{__install} -p -D -m 0644 geo.data %{buildroot}%{nginx_confdir}/conf.d/geo.data
%{__install} -p -D -m 0644 %{SOURCE23} %{buildroot}%{nginx_confdir}/conf.d/GeoLiteCity.dat
%{__install} -p -m 0644 %{SOURCE3} %{SOURCE4} %{buildroot}%{nginx_confdir}/conf.d
%{__install} -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_logdir}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_webroot}
%{__install} -p -m 0644 %{SOURCE100} %{SOURCE103} %{SOURCE104} %{buildroot}%{nginx_webroot}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/pam.d/
%{__install} -p -m 0644 %{SOURCE200} %{buildroot}%{_sysconfdir}/pam.d/%{nginx_name}
%{__install} -p -m 0644 %{_builddir}/%{nginx_name}-%{version}/naxsi-master/naxsi_config/naxsi_core.rules %{buildroot}%{nginx_confdir}/conf.d/naxsi_core.rules

strip %{buildroot}%{_sbindir}/nginx %{buildroot}/usr/share/nginx/modules/*
# convert to UTF-8 all files that give warnings.
for textfile in CHANGES
do
    mv $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    rm -f $textfile.old
done

cd naxsi-master/nxapi/
python setup.py build
python setup.py install --root %{buildroot} --install-data /usr/local
%{__install} -p -D -m 0644 %{SOURCE321} %{buildroot}/usr/local/etc/
#%{__install} -p -m 0755 %{buildroot}/usr/bin/nxtool.py

%clean
rm -rf %{buildroot}

%pre
%{_sbindir}/useradd -c "Nginx user" -s /bin/false -r -d %{nginx_home} %{nginx_user} 2>/dev/null || :

%post
if [ $# -eq 0 ]
then
    exit
fi

if [ $1 = 1 ]; then
/sbin/chkconfig --add %{nginx_name}
fi
if [ $1 = 2 ]; then
/sbin/service %{nginx_name} upgrade
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service %{nginx_name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{nginx_name}
fi


%files
%defattr(-,root,root,-)
%doc LICENSE CHANGES README

%{nginx_datadir}/
%{_sbindir}/%{nginx_name}
%{_initrddir}/%{nginx_name}
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%config(noreplace) %{nginx_confdir}/conf.d/*
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/%{nginx_name}.conf.default
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/%{nginx_name}.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{_sysconfdir}/logrotate.d/%{nginx_name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{nginx_name}
%config(noreplace) %{_sysconfdir}/pam.d/%{nginx_name}
#%config(noreplace) /usr/lib/python2.7/site-packages/nxapi/*
%config(noreplace) /usr/lib/python2.7/site-packages/*
%config(noreplace) /usr/local/etc/*
%config(noreplace) /usr/bin/nxtool.py
%config(noreplace) /usr/local/nxapi/*
#%config(noreplace) /usr/local/nxapi/tpl/ARGS/*
#%config(noreplace) /usr/local/nxapi/tpl/BODY/*
#%config(noreplace) /usr/local/nxapi/tpl/HEADERS/*
#%config(noreplace) /usr/local/nxapi/tpl/URI/*

#%dir %{perl_vendorarch}/auto/%{nginx_name}
#%{perl_vendorarch}/%{nginx_name}.pm
#%{perl_vendorarch}/auto/%{nginx_name}/%{nginx_name}.so
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_logdir}

#dir /usr/bin/*
#%dir /usr/lib/python2.7/site-packages/nx_lib/*
#%dir /usr/lib/python2.7/site-packages/*
#%config(noreplace) /usr/local/etc/nx_util.conf
#%dir /usr/local/nx_datas/*
#%{_mandir}/man1/*
#%attr(-,%{nginx_user},%{nginx_group}) /usr/local/etc/nx_util.conf

%changelog
* Fri Apr 11 2014 dimka
- add naxsi configs


