from .command import GetCommands
from .handler import Handler
from .pull_request_event import GetPullRequest, GetRepo

invalid_command_format = ("You must specify exactly 1 release to cherry-pick " +
        "this commit into. For example:\n\n" +
        "> @spinnakerbot cherry-pick 1.10")

not_merged = "Only merged PRs can be cherry picked into a release branch"

class PullRequestCherryPickEventHandler(Handler):
    def __init__(self):
        super().__init__()
        self.omit_repos = self.config.get('omit_repos', [])

    def handles(self, event):
        return (event.type == 'IssueCommentEvent'
            and (event.payload.get('action') == 'created'
                or event.payload.get('action') == 'edited'))

    def handle(self, g, event):
        # avoid fetching until needed
        pull_request = None
        repo = GetRepo(event)
        if repo in self.omit_repos:
            self.logging.info('Skipping {} because it\'s in omitted repo {}'.format(event, repo))
            return

        for command in GetCommands(event.payload.get('comment', {}).get('body')):
            if command[0] in ['cherry-pick', ':cherries::pick:', 'backport']:
                if len(command) != 2:
                    pull_request.create_issue_comment(invalid_command_format)
                    return
                release = command[1]
                if pull_request is None:
                    pull_request = GetPullRequest(g, event)
                self.do_cherry_pick(pull_request, release)

    def do_cherry_pick(self, pull_request, release):
        if not pull_request.is_merged:
            pull_request.create_issue_comment(not_merged)

        deprecation_message = (
            "Support for automating cherry picks is being removed from spinnakerbot "
            "in favor of the mergify backport command. To help with the transition, "
            "I'll run the required command for you now, but in the future please "
            "run the mergify command directly."
        )
        mergify_command = "@Mergifyio backport release-{}.x".format(release)
        pull_request.create_issue_comment(deprecation_message)
        pull_request.create_issue_comment(mergify_command)

PullRequestCherryPickEventHandler()
