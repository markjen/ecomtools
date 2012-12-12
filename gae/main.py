import webapp2

from webapp2_extras import routes

import handler


app = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/', handler.IndexHandler, 'index'),
        webapp2.Route(r'/register', handler.RegisterHandler, 'register'),
        webapp2.Route(r'/api/tax/lookup', handler.TaxLookupHandler, 'tax-lookup'),
        routes.PathPrefixRoute(
            r'/api/usps',
            routes.NamePrefixRoute(
                'usps-',
                [
                    webapp2.Route('/track', handler.UspsTrackHandler, 'track'),
                    webapp2.Route('/verify', handler.UspsVerifyHandler, 'verify'),
                ]).get_routes()
        ),
    ],
    debug=True)
