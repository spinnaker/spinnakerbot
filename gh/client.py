#!/usr/bin/env python3

import heapq
import logging
import os

import github


class Client(object):
    def __init__(self, config, storage):
        self.token = self.get_token(config)
        self.username = self.get_username(config)
        self.g = github.Github(self.token)
        self.storage = storage
        self._repos = config['repos']
        self._repo_objects = dict()
        self.logging = logging.getLogger('github_client_wrapper')

        # Kludge accessing a private property to support ETag for certain requests, to avoid GitHub's rate limiter
        # First, fetch rate_limit to initialize the Requester connection
        self.rate_limit()
        requester = self.g._Github__requester
        real_connection = requester._Requester__connection
        # Replace the connection with one that manages ETag caching headers
        requester._Requester__connection = ETagSupport(real_connection, storage)

    def get_username(self, config):
        return config.get('username', 'spinnakerbot')

    def get_token(self, config):
        token_path = config.get('token_path')
        if token_path is None:
            return config.get('token')

        with open(os.path.expanduser(token_path), 'r') as f:
            return f.read().strip()

    def rate_limit(self):
        ret = self.g.get_rate_limit()
        return ret

    def get_label(self, repo, name, create=True):
        repo = self.get_repo(repo)
        label = None
        try:
            label = repo.get_label(name)
        except:
            pass

        if label is None and create:
            label = repo.create_label(name, '000000')

        return label

    def get_repo(self, r):
        if self._repo_objects.get(r) is None:
            self._repo_objects[r] = self.g.get_repo(r)
        return self._repo_objects[r]

    def repos(self):
        for r in self._repos:
            yield self.get_repo(r)

    def pull_requests(self):
        for r in self._repos:
            pulls = 0
            self.logging.info('Reading pull requests from {}'.format(r))
            for i in self.get_repo(r).get_pulls():
                pulls += 1
                yield i

    def issues(self):
        for r in self._repos:
            issues = 0
            self.logging.info('Reading issues from {}'.format(r))
            for i in self.get_repo(r).get_issues():
                issues += 1
                yield i

    def events_since(self, date):
        return heapq.merge(
                *[ reversed(list(self._events_since_repo_iter(date, r))) for r in self._repos ],
                key=lambda e: e.created_at
        )

    def _events_since_repo_iter(self, date, repo):
        events = 0
        self.logging.info('Reading events from {}'.format(repo))
        for e in self.get_repo(repo).get_events():
            if e.created_at <= date:
                break
            else:
                events += 1
                yield e

    def get_branches(self, repo):
        return self.get_repo(repo).get_branches()

    def get_pull_request(self, repo, num):
        return self.get_repo(repo).get_pull(num)

    def get_issue(self, repo, num):
        return self.get_repo(repo).get_issue(num)


class ETagSupport:
    def __init__(self, real_connection, storage):
        self.real_connection = real_connection
        self.storage = storage
        self.logging = logging.getLogger('github_connection')

    def can_use_etag(self, url):
        return url.endswith('/events')

    def request(self, verb, url, input, headers):
        if self.can_use_etag(url):
            previous_etag = self.storage.load("ETag:%s" % url)
            self.logging.info("---> %s %s (ETag: %s)" % (verb, url, previous_etag))
            if previous_etag is not None:
                headers['If-None-Match'] = previous_etag
        else:
            self.logging.info("---> %s %s (ETag: NotSupportedForUrl)" % (verb, url))

        return self.real_connection.request(verb, url, input, headers)

    def getresponse(self):
        url = self.real_connection.url
        response = self.real_connection.getresponse()
        status = response.status
        etag = response.headers.get('etag')
        if self.can_use_etag(url) and etag is not None:
            self.storage.store("ETag:%s" % url, etag)
            self.logging.info("<--- %s (ETag: %s)" % (status, etag))
        else:
            self.logging.info("<--- %s" % status)
        return response

    def close(self):
        return
