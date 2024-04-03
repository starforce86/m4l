from os import getenv
from tendenci.settings import *
from dotenv import load_dotenv

load_dotenv()

# Configure your site-specific settings here to override the defaults configured
# by Tendenci and Django.
#
# See https://github.com/tendenci/tendenci/blob/master/tendenci/settings.py for
# Tendenci defaults.  See https://docs.djangoproject.com/en/1.11/ref/settings/
# for Django defaults.
#
# To override part of a data structure configured by Tendenci without replacing
# the entire data structure, you can use something like:
# Add a list item: INSTALLED_APPS += ['example_app']
# Remove a list item: INSTALLED_APPS.remove('some_app')
# Remove a hash key: LOGGING['handlers']['mail_admins'].pop('class', None)


# ---------------------------------------------------------------------------- #
# Debug Setting
# ---------------------------------------------------------------------------- #

# To enable verbose error pages, debug logging, and other features that are
# useful for development/testing but should not be enabled on live sites,
# uncomment this setting.
DEBUG = bool(getenv('DJANGO_DEBUG'))


if DEBUG:
    disable_template_cache()


# ---------------------------------------------------------------------------- #
# Misc Site-Specific Settings
# ---------------------------------------------------------------------------- #

# Any site-specific settings that do not fit in the sections below can go here.


# ---------------------------------------------------------------------------- #
# Required Settings
# ---------------------------------------------------------------------------- #

# These must be set to two different random strings, at least 50 characters in
# length, that are unique to this site.  Django will refuse to start if these
# are not configured.
# The security of the site relies on these being appropriately random, so use a
# good random number generator.  Good random strings are conveniently available
# at https://www.grc.com/passwords.htm (Use the
# "63 random alpha-numeric characters" string, and refresh the page to get an
# additional string.)
SECRET_KEY = getenv('SECRET_KEY', '').strip('\'')
SITE_SETTINGS_KEY = getenv('SITE_SETTINGS_KEY', '').strip('\'')

RECAPTCHA_VERIFY_REQUEST_TIMEOUT = 30

RECAPTCHA_PUBLIC_KEY = getenv('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = getenv('RECAPTCHA_PRIVATE_KEY', '')
USE_RECAPTCHA_V3 = True

# This must be set to a list of fully qualified domain names that are valid for
# this site.  Connections which request any other name will be rejected.
# To prevent HTTP Host header attacks, this list must be limited to names that
# are actually hosted on this server.
# If this server uses a wildcard DNS record then you can prefix the domain
# listed here with a '.' to match all subdomains ('.example.com').
ALLOWED_HOSTS = [
    host.strip() for host in getenv(
        'ALLOWED_HOSTS',
        'momsforliberty.org, www.momsforliberty.org'
    ).split(',')
]
if DEBUG:
    ALLOWED_HOSTS += ['localhost', '127.0.0.1', '[::1]']

# Tendenci uses the following PostgreSQL database connection settings by
# default.  Uncomment and configure settings here to override the defaults.
DATABASES['default']['HOST'] = getenv('DATABASE_HOST')
DATABASES['default']['PORT'] = int(getenv("DATABASE_PORT") or "5432")
DATABASES['default']['USER'] = getenv('DATABASE_USERNAME')
DATABASES['default']['PASSWORD'] = getenv('DATABASE_PASSWORD', '').strip('\'')
DATABASES['default']['NAME'] = getenv('DATABASE_NAME')

# This must be set to the time zone used by PostgreSQL, which defaults to the
# system time zone configured in /etc/timezone.
# To change the PostgreSQL time zone without changing the system time zone:
# sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'US/Eastern';"
# A list of time zone names can be found at
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'US/Central'


# ---------------------------------------------------------------------------- #
# HTTPS and Session Settings
# ---------------------------------------------------------------------------- #

# Uncomment if this site supports HTTPS.
# This will cause the login page and other sensitive pages to require HTTPS.
#SSL_ENABLED = True

# Uncomment if using NGINX.
# This will allow Tendenci to properly detect HTTP vs HTTPS client connections
# when using NGINX.  DO NOT use this if Tendenci is not behind NGINX, as that
# will open a security hole.
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Uncomment these if NGINX is configured to redirect all HTTP connections to
# HTTPS.  This is strongly recommended for live sites.
#SESSION_COOKIE_SECURE = True  # Send Session Cookie over HTTPS only
#CSRF_COOKIE_SECURE = True  # Send CSRF Cookie over HTTPS only

# Depending on configuration, logged in users may either be logged out when the
# user closes their browser, or may remain logged in after the user closes and
# reopens their browser.
# For logins through /admin/login/, SESSION_EXPIRE_AT_BROWSER_CLOSE controls
# this behavior.  (Default is False)
# For logins through /accounts/login/, the "Hide Remember Me" and
# "Remember Me Checked" settings in the "Users" app in Tendenci control this
# behavior, overriding SESSION_EXPIRE_AT_BROWSER_CLOSE.
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Independently of the above behavior, users will also be logged out by both the
# server and their own browser if they do not visit the site for more than
# SESSION_COOKIE_AGE seconds.  However, each page load will reset this counter,
# allowing the user to remain logged in indefinitely as long as they continue to
# visit the site regularly.  (Default is 2 weeks)
#SESSION_COOKIE_AGE = 60*60*24*7*2


# ---------------------------------------------------------------------------- #
# EMail Settings
# ---------------------------------------------------------------------------- #

# Tendenci EMail is disabled by default.

# If EMail is enabled below, these must be uncommented and set to an appropriate
# "From" address.
DEFAULT_FROM_EMAIL = 'noreply@momsforliberty.org'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# If EMail is enabled, optionally uncomment and configure this to send an alert
# email to the specified addresses any time Python, Django, or Tendenci
# encounter an error.  This also enables some other non-error Tendenci email
# notifications.
ADMINS = [
    (
        getenv("NOTIFY_ADMIN_NAME", "Fabius Engineering"),
        getenv("NOTIFY_ADMIN_EMAIL", "engineering@fabiuslabs.com")
    )
]
# To disable error emails and send only non-error Tendenci email notifications:
#disable_admin_emails()

# To send EMail via an SMTP server:
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_USE_TLS = False
#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 25
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''

# To send EMail via Amazon SES:
#EMAIL_BACKEND = "django_ses.SESBackend"
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

# To send email via mailgun
EMAIL_BACKEND = getenv('MAIL_BACKEND')
EMAIL_USE_TLS = bool(getenv('MAIL_USE_TLS'))
EMAIL_HOST = getenv('MAIL_HOST')
EMAIL_PORT = getenv('MAIL_PORT')
EMAIL_HOST_USER = getenv('MAIL_USER')
EMAIL_HOST_PASSWORD = getenv('MAIL_PASSWORD', '').strip('\'')

# To send newsletters via an SMTP server (example: mailgun):
NEWSLETTER_EMAIL_HOST = getenv('MAIL_HOST')
NEWSLETTER_EMAIL_PORT = getenv('MAIL_PORT')
NEWSLETTER_EMAIL_HOST_USER = getenv('MAIL_USER')
NEWSLETTER_EMAIL_HOST_PASSWORD = getenv('MAIL_PASSWORD', '').strip('\'')


# For development/testing:
# Try https://github.com/Nilhcem/FakeSMTP and use the SMTP configuration above,
# or try https://github.com/PaulSD/django_log_email and use the following
# configuration.
#EMAIL_BACKEND = 'django_log_email.backends.EmailBackend'
#EMAIL_LOG_FILE = '/var/log/tendenci/email.log'
# When using django_log_email, you can leave this setting commented to discard
# email after logging, or uncomment it to both log and send email.
#EMAIL_LOG_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# When using django_log_email, you can uncomment this setting to send error
# alert emails without logging.
#LOGGING['handlers']['mail_admins']['email_backend'] = 'django.core.mail.backends.smtp.EmailBackend'


# ---------------------------------------------------------------------------- #
# Payment Gateway Settings
# ---------------------------------------------------------------------------- #

#MERCHANT_LOGIN = ''
#MERCHANT_TXN_KEY = ''

# Authorize.Net
#AUTHNET_POST_URL = 'https://secure2.authorize.net/gateway/transact.dll'
#AUTHNET_MD5_HASH_VALUE = ''

#AUTHNET_CIM_API_TEST_URL = 'https://apitest.authorize.net/xml/v1/request.api'
#AUTHNET_CIM_API_URL = 'https://api2.authorize.net/xml/v1/request.api'

# FirstData
#FIRSTDATA_POST_URL = 'https://secure.linkpt.net/lpcentral/servlet/lppay'

# FirstData E4
#FIRSTDATAE4_POST_URL = 'https://checkout.globalgatewaye4.firstdata.com/payment'
#FIRSTDATAE4_POST_URL = 'https://globalgatewaye4.firstdata.com/pay'
#FIRSTDATA_RESPONSE_KEY = ''
#FIRSTDATA_USE_RELAY_RESPONSE = False

# PayPal PayFlow Link
#PAYFLOWLINK_PARTNER = ''
#PAYPAL_MERCHANT_LOGIN = ''
#PAYFLOWLINK_POST_URL = 'https://payflowlink.paypal.com'

# PayPal
#PAYPAL_POST_URL = 'https://www.paypal.com/cgi-bin/webscr'
#PAYPAL_POST_URL = PAYPAL_SANDBOX_POST_URL
PAYPAL_MERCHANT_LOGIN= getenv('PAYPAL_MERCHANT_LOGIN')
MERCHANT_TXN_KEY = getenv('MERCHANT_TXN_KEY')

# Stripe
STRIPE_SECRET_KEY = getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = getenv('STRIPE_PUBLISHABLE_KEY')

# ---------------------------------------------------------------------------- #
# Cache Settings
# ---------------------------------------------------------------------------- #

# If pylibmc is installed then Tendenci will attempt to connect to memcached on
# localhost.  If pylibmc and/or memcached is not installed then caching will be
# disabled.

# If multiple Tendenci sites share the same memcached, uncomment and configure
# the following settings with a value that is unique to this site.  This is used
# to prevent cache collisions between sites.
#SITE_CACHE_KEY = 'tendenci'
#CACHE_PRE_KEY = SITE_CACHE_KEY

# To change the memcached host/port:
CACHES['default']['LOCATION'] = ':'.join([
    getenv('MEMCACHED_HOST', '127.0.0.1'),
    getenv('MEMCACHED_PORT', '11211')
])

# To change the cache timeout:
# (Default is 30 days)
#CACHES['default']['TIMEOUT'] = 60*60*24*30
# Specify your caches backend here if you don't have memcached installed.
if DEBUG:
    CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

# ---------------------------------------------------------------------------- #
# Amazon S3 Storage Settings
# ---------------------------------------------------------------------------- #

#AWS_LOCATION = ''    # This is usually your site name
#AWS_ACCESS_KEY_ID = ''
#AWS_SECRET_ACCESS_KEY = ''
#AWS_STORAGE_BUCKET_NAME = ''
#USE_S3_STORAGE = all([
#    AWS_LOCATION,
#    AWS_ACCESS_KEY_ID,
#    AWS_SECRET_ACCESS_KEY,
#    AWS_STORAGE_BUCKET_NAME
#])


# ---------------------------------------------------------------------------- #
# Celery Settings
# ---------------------------------------------------------------------------- #

# Uncomment this setting if you are running the Celery Task System.
#CELERY_IS_ACTIVE = True


# ---------------------------------------------------------------------------- #
# Custom Application Settings
# ---------------------------------------------------------------------------- #

# To add an app to INSTALLED_APPS:
#INSTALLED_APPS += ['example_app']

# To remove a default app from INSTALLED_APPS:
#INSTALLED_APPS.remove('some_app')
# Or:
#remove_apps = ['app1', 'app2']
#for app in remove_apps:
#    INSTALLED_APPS.remove(app)

# To enable custom URL patterns to be configured in urls.py:
ROOT_URLCONF = 'conf.urls'

# To enable the Tendenci helpdesk app, uncomment this setting, uncomment
# ROOT_URLCONF above, and uncomment the helpdesk urlpattern in urls.py
#INSTALLED_APPS += ['markdown_deux', 'bootstrapform', 'tendenci.apps.helpdesk']


# ---------------------------------------------------------------------------- #
# Logging Settings
# ---------------------------------------------------------------------------- #

# By default, Tendenci logs all INFO and greater log messages to
# /var/log/tendenci/app.log
#
# When DEBUG is True, Tendenci logs DEBUG and greater log messages to
# /var/log/mysite/debug.log (in addition to logging INFO and greater log
# messages to /var/log/mysite/app.log)

# To change the log file names:
set_app_log_filename(getenv('APP_LOG_FILE'))
set_debug_log_filename(getenv('DEBUG_LOG_FILE'))

# To change the log level for the app.log file:
# (Valid levels are: 'DEBUG' 'INFO' 'WARNING' 'ERROR' 'CRITICAL')
#set_app_log_level('INFO')

# To disable logging:
disable_app_log()
disable_debug_log()

# To disable debug.log and write DEBUG messages to app.log when DEBUG is True:
#disable_debug_log()
#if DEBUG: set_app_log_level('DEBUG')

# To log to the console in addition to the log files (or instead of the log
# files if they are disabled above):
enable_console_log()
# To change the console log level:
#set_console_log_level('INFO')

# For more advanced configuration, you can modify the default LOGGING data
# structure, which is configured in
# https://github.com/tendenci/tendenci/blob/master/tendenci/settings.py
# For example:
#LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
#LOGGING['loggers']['py.warnings'].pop('filters', None)

# To use Sentry (https://docs.sentry.io/):
#SENTRY_DSN = ''
#INSTALLED_APPS += ['raven.contrib.django.raven_compat']
#RAVEN_CONFIG = {'dsn': SENTRY_DSN}


# ---------------------------------------------------------------------------- #
# Additional Debugging Settings
# ---------------------------------------------------------------------------- #

# Uncomment and configure these settings to enable some additional debugging
# capabilities for clients connecting from one of the specified IPs.
# These debugging capabilities may expose internal/private data, so be careful
# to restrict this appropriately.
# Note that if you are running NGINX, all clients appear to be connecting from
# 127.0.0.1, so this example configuration will give all clients access to these
# debugging capabilities.
#if DEBUG:
#    INTERNAL_IPS = ['127.0.0.1', '::1']

# Uncomment this setting to enable the Django Debug Toolbar for profiling
# (measuring CPU/SQL/cache/etc timing).  Only clients matching INTERNAL_IPS
# above will be able to use the toolbar.
# This toolbar may expose internal/private data, and it will slow down your site
# significantly, so use this with caution.
DEBUG_TOOLBAR_ENABLED = bool(getenv('DEBUG_TOOLBAR_ENABLED'))
PERMISSION_TRACER_ENABLED = bool(getenv('PERMISSION_TRACER_ENABLED'))


# ---------------------------------------------------------------------------- #
# These lines must remain at the end of this file
# ---------------------------------------------------------------------------- #
from tendenci.apps.registry.utils import update_addons  # noqa: E402
INSTALLED_APPS = update_addons(INSTALLED_APPS, SITE_ADDONS_PATH)

if PERMISSION_TRACER_ENABLED:
    MIDDLEWARE += ['tendenci.debug.perm_tracer.PermTracerMiddleware']
