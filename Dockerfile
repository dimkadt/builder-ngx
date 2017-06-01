FROM devbeta/balancer_layer




RUN yum install -y rpm-build gd gd-devel libtool libxslt-devel httpd-devel perl-Exporter libcurl-devel libxml2-devel pam-devel \
	pcre-devel zlib-devel openssl-devel GeoIP-devel lua lua-devel yajl yajl-devel ssdeep ssdeep-devel perl-ExtUtils-Embed make

ENV NGINX_VERSION=1.11.13
ENV MODSECURITY_VERSION=2.9.1


COPY extensions.lst /tmp/extensions.lst

RUN mkdir -p /root/rpmbuild/{SOURCES,SPECS}/
ADD SOURCES/ /root/rpmbuild/SOURCES/

COPY nginx-${NGINX_VERSION}.spec /root/rpmbuild/SPECS/

RUN cd /root/rpmbuild/SOURCES ; ls ; /bin/bash /tmp/extensions.lst
RUN cd /root/rpmbuild/SPECS ; ls ; rpmbuild -ba nginx-${NGINX_VERSION}.spec
