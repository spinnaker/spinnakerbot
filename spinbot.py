#!/usr/bin/env python3

import event
import gh
import http
import logging
import os
import policy
import storage
import sys
import time

from config import GetCtx
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO


class SimpleServer(HTTPServer):
    def __init__(self, server_address, handler):
        super().__init__(server_address, handler)
        self.ctx = GetCtx()
        setup_logging(self.ctx)
        setup_events(self.ctx)
        setup_policies(self.ctx)

        self.storage = create_storage(self.ctx)
        self.github_client = create_client(self.ctx, self.storage)


class SimpleHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        b = bytes("working!", "UTF-8")
        self.wfile.write(b)

    def do_POST(self):
        try:
            event.ProcessEvents(self.server.github_client, self.server.storage)
            policy.ApplyPolicies(self.server.github_client)
            logging.info('...done')
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes("done!", "UTF-8"))
        except:
            e = sys.exc_info()[0]
            logging.error(e)
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes("something went wrong", "UTF-8"))


def create_client(ctx, storage):
    return gh.Client(ctx.get('github', {}), storage)


def create_storage(ctx):
    return storage.BuildStorage(ctx.get('storage', {}))


def setup_logging(ctx):
    lctx = ctx.get('logging', {})
    level = lctx.get('level', 'INFO')

    logging.basicConfig(
        format='%(asctime)-15s %(name)-12s %(levelname)-8s: %(message)s',
        level=level
    )


def setup_events(ctx):
    event.ConfigureHandlers(ctx.get('event', {}))


def setup_policies(ctx):
    policy.ConfigurePolicies(ctx.get('policy', {}))


if __name__ == '__main__':
    port = os.environ.get('PORT', "8080")
    port = int(port)

    httpd = SimpleServer(('', port), SimpleHandler)
    print(time.asctime(), "Server Starts - %s:%s" % ('', port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % ("", port))
