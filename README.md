eCommerce tools
===============

Source code behind http://ecomtools.appspot.com

Provides a nicer API to USPS Webtools (https://www.usps.com/business/webtools.htm) and sales tax lookup in various supported states.

Library
=======
Code in /lib has no dependencies and is tested for use on Python 2.7+

Google App Engine
=================
Code in /gae is for self-hosting an instance of the Google App Engine application. To hit USPS Webtools APIs successfully, you will need to register for a USPS user id at https://secure.shippingapis.com/registration/ and get it approved for production APIs.
