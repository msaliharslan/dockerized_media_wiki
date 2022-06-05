#!/bin/sh

cd /var/www/mediawiki/w

COMPOSER=composer.local.json 
composer require --no-update mediawiki/semantic-media-wiki
composer update --no-dev --prefer-source

php maintenance/update.php

echo "#Semantic MediaWiki" >> /var/www/mediawiki/w/LocalSettings.php
echo "wfLoadExtension( 'SemanticMediaWiki' );" >> /var/www/mediawiki/w/LocalSettings.php
echo "enableSemantics( 'http://localhost' );"  >> /var/www/mediawiki/w/LocalSettings.php