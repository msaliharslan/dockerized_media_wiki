FROM alpine:3.15

# Install required packages
RUN apk add --no-cache \
    php7 \
    php7-pecl-apcu \
    php7-intl \
    php7-mbstring \
    php7-xml \
    php7-xmlreader \
    php7-xmlwriter \
    php7-xmlrpc \
    php7-simplexml \
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
    php7-phar \
    php7-tokenizer \
    imagemagick \
    libgd \
    texlive \
    postfix \
    openrc \
    apache2 \
    diffutils \
    git

# Install Composer
COPY scripts/install_composer.sh /tmp/install_composer.sh
RUN /tmp/install_composer.sh

# Get MediaWiki
RUN mkdir -p /var/www/mediawiki && \
    cd /var/www/mediawiki && \
    wget https://releases.wikimedia.org/mediawiki/1.38/mediawiki-1.38.0.tar.gz && \
    tar -xzf mediawiki-1.38.0.tar.gz && \
    mv mediawiki-1.38.0 w && \
    rm mediawiki-1.38.0.tar.gz && \
    chown -R -h apache w && \
    chgrp -R -h apache w

# Copy Configuration Files
COPY /configs/wiki.conf /etc/apache2/conf.d

# Change document root of apache server
RUN sed -i 's/\/var\/www\/localhost\/htdocs/\/var\/www\/mediawiki/g' /etc/apache2/httpd.conf

# Start web server
CMD [ "httpd", "-D", "FOREGROUND" ]