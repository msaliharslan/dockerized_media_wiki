FROM alpine:3.15

# Install the packages
RUN apk add --no-cache \
    php7 \
    php7-pecl-apcu \
    php7-intl \
    php7-mbstring \
    php7-xml \
    php7-xmlreader \
    php7-xmlwriter \
    php7-xmlrpc \
    php7-mysqli \
    php7-mysqlnd \
    php7-calendar \
    php7-curl \
    php7-apache2 \
    php7-json \
    php7-fileinfo \
    php7-iconv \
    php7-ctype \
    php7-session \
    php7-dom \
    imagemagick \
    libgd \
    texlive \
    postfix \
    openrc \
    apache2 \
    diffutils \
    git
    
# Get MediaWiki
RUN cd /var/www/localhost/htdocs && \
    wget https://releases.wikimedia.org/mediawiki/1.37/mediawiki-1.37.2.tar.gz && \
    tar -xzf mediawiki-1.37.2.tar.gz && \
    mv mediawiki-1.37.2 w && \
    rm mediawiki-1.37.2.tar.gz && \
    chown -R -h apache w && \
    chgrp -R -h apache w

# Create a directory for temporary files
# RUN mkdir -p /tmp/mediawiki && \
#     chown -R apache /tmp/mediawiki && \
#     chgrp -R apache /tmp/mediawiki && \
#     sed -i '/;upload_tmp_dir =/c\upload_tmp_dir = /tmp/mediawiki' /etc/php7/php.ini

# Copy Configuration Files
COPY wiki.conf /etc/apache2/conf.d 
# COPY LocalSettings.php /var/www/localhost/htdocs/w/

# Start web server
CMD [ "httpd", "-D", "FOREGROUND" ]