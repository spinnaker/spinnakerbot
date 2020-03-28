#!/usr/bin/env python3

import logging
import gh
import storage
import event
import monitoring 
import policy
from config import GetCtx

def create_client(ctx, storage):
    return gh.Client(ctx.get('github', {}), storage)

def create_storage(ctx):
    return storage.BuildStorage(ctx.get('storage', {}))

def setup_database(ctx):
    monitoring.ConfigureMonitoring(ctx.get('database', {}))

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

def main():
    ctx = GetCtx()

    setup_logging(ctx)
    setup_database(ctx)
    setup_events(ctx)
    setup_policies(ctx)

    storage = create_storage(ctx)
    github_client = create_client(ctx, storage)

    event.ProcessEvents(github_client, storage)
    policy.ApplyPolicies(github_client)

    logging.info('Flushing ops...')
    monitoring.FlushDatabaseWrites(align_points=True)
    logging.info('...done')

if __name__ == '__main__':
    main()
