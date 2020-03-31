def GetIssue(g, event):
    url = event.payload.get('issue', {}).get('url')
    if not url:
        return None

    repo = '/'.join(url.split('/')[-4:-2])
    number = int(url.split('/')[-1])

    if repo is None or number is None:
        return None

    return g.get_issue(repo, number)

def GetRepo(g, event):
    url = event.payload.get('issue', {}).get('url')
    if not url:
        return None

    repo = '/'.join(url.split('/')[-4:-2])
    return g.get_repo(repo)

