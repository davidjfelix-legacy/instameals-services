#!/usr/bin/env python
import sys
import uuid
from datetime import datetime
from json import JSONDecodeError
from typing import List, Optional

import rethinkdb as rdb
from raven.contrib.tornado import AsyncSentryClient
from tornado import gen
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.web import Application

from .handlers import (
    AddressHandler,
    AddressesHandler,
    AllergenHandler,
    AllergensHandler,
    APIHandler,
    FacebookAuthHandler,
    GoogleAuthTokenHandler,
    HealthHandler,
    InfoHandler,
    IngredientHandler,
    IngredientsHandler,
    MeByTokenHandler,
    MealHandler,
    MealsHandler,
    MeHandler,
    UserHandler,
    UsersHandler,
)


class FeastedAPIApplication(Application):
    def __init__(self):
        routes = [
            (r'/', APIHandler),
            (r'/addresses', AddressesHandler),
            (r'/addresses/(?P<address_id>[^\/]+)', AddressHandler),
            (r'/allergens', AllergensHandler),
            (r'/allergens/(?P<allergen_id>[^\/]+)', AllergenHandler),
            (r'/auth/google/jwt-auth', GoogleAuthTokenHandler),
            (r'/auth/facebook/token-auth', FacebookAuthHandler),
            (r'/health', HealthHandler),
            (r'/info', InfoHandler),
            (r'/ingredients', IngredientsHandler),
            (r'/ingredients/(?P<ingredient_id>[^\/]+)', IngredientHandler),
            (r'/me', MeHandler),
            (r'/me/by-token', MeByTokenHandler),
            (r'/meals', MealsHandler),
            (r'/meals/(?P<meal_id>[^\/]+)', MealHandler),
            (r'/users', UsersHandler),
            (r'/users/(?P<user_id>[^\/]+)', UserHandler),
        ]
        settings = {
        }
        super().__init__(handlers=routes, **settings)
        self.server_id = uuid.uuid4()
        self.start_time = datetime.utcnow()
        self.certs_uri = "https://www.googleapis.com/oauth2/v1/certs"
        self.sentry_client = AsyncSentryClient(
            'https://1fd6fdf70aef439e9fab3221964f66b0:9e0edcbade1749b68582fdc46b73b6d1@app.getsentry.com/69921'
        )
        self.client_ids = [
            "531566137905-fhljh7kirg7v9kg4019qd6aaob57gd4s.apps.googleusercontent.com",
        ]
        rdb.set_loop_type("tornado")

    @gen.coroutine
    def db_conn(self):
        # Tornado Future returned below
        host = '10.0.0.94'
        if len(sys.argv) > 1 and sys.argv[1] == 'rdb_local':
            host = 'localhost'

        conn = yield rdb.connect(host=host, port=28015, db='feasted')
        return conn

    @gen.coroutine
    def get_google_certs(self) -> Optional[List[str]]:
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(self.certs_uri)
        if response.code == 200:
            try:
                return json_decode(response.body).values()
            except JSONDecodeError:
                return None
        else:
            return None


def main():
    application = FeastedAPIApplication()
    application.listen(5000)
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    IOLoop.current().start()


if __name__ == "__main__":
    main()
