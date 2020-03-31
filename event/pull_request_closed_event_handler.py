from gh import ParseReleaseBranch, AddLabel
from .handler import Handler
from .pull_request_event import GetBaseBranch, GetPullRequest, GetRepo


class PullRequestClosedEventHandler(Handler):
    def __init__(self):
        super().__init__()

    def handles(self, event):
        return (event.type == 'PullRequestEvent'
            and event.payload.get('action') == 'closed')

    def handle(self, g, event):
        pull_request = GetPullRequest(g, event)
        if not pull_request:
            log.warn('Unable to determine pull request for {}'.format(event))
            return

        self.label_release(g, event, pull_request)

    def label_release(self, g, event, pull_request):
        if not pull_request or not pull_request.merged:
            return None

        base_branch = GetBaseBranch(event)
        release_branch = ParseReleaseBranch(base_branch)
        if release_branch != None:
            return self.target_release(g, pull_request, release_branch)

        repo = GetRepo(event)
        branches = g.get_branches(repo)

        parsed = [ ParseReleaseBranch(b.name) for b in branches if ParseReleaseBranch(b.name) is not None ]
        if len(parsed) == 0:
            self.logging.warn('No release branches in {}'.format(repo))
            return None

        parsed.sort()
        release_branch = parsed[-1]
        release_branch[1] = release_branch[1] + 1
        return self.target_release(g, pull_request, release_branch)

    def target_release(self, g, pull_request, release_branch):
        release_name = '.'.join([ str(v) for v in release_branch ])
        label = 'target-release/{}'.format(release_name)
        AddLabel(g, pull_request, label)

        return release_name

PullRequestClosedEventHandler()
