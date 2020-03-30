from gh import ObjectType, PullRequestRepo
from datetime import datetime
from .policy import Policy

class LogPullRequestPolicy(Policy):
    def __init__(self):
        super().__init__()

    def applies(self, o):
        return ObjectType(o) == 'pull_request'

    def apply(self, g, o):
        days_since_created = None
        days_since_updated = None
        now = datetime.now()
        if o.created_at is not None:
            days_since_created = (now - o.created_at).days
        
        if o.updated_at is not None:
            days_since_updated = (now - o.updated_at).days

        repo = PullRequestRepo(o)

        self.monitoring_db.write('pull_request', { 
            'days_since_created': days_since_created,
            'days_since_updated': days_since_updated,
            'count': 1
        }, tags={ 
            'repo': repo, 
            'user': o.user.login,
            'state': o.state
        })

LogPullRequestPolicy()
