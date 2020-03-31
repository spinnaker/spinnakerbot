import logging
import traceback

import github

import policy
from .policy_registry import GetConfig


def ApplyPolicies(g):
    config = GetConfig()
    enabled = config.get('enabled', True)
    if enabled is not None and not enabled:
        return

    logging.info('Processing issues, repos')
    for i in g.issues():
        for p in policy.Policies():
            if p.applies(i):
                err = None
                try:
                    p.apply(g, i)
                except Exception as _err:
                    logging.warning('Failure applying {} to {} due to {}: {}'.format(
                            p, i, _err, traceback.format_exc()
                    ))
                    err = _err

                if err is not None and isinstance(err, github.GithubException):
                  if err.status == 403:
                    # we triggered abuse protection, time to shutdown
                    logging.warning('Abuse protection triggered. Shutting down early.')
                    return

