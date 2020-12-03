# `spinbot`

A GitHub bot for managing Spinnaker's repos.

## Config

The production config is checked in as `config/config.yaml`.

Certain properties are exposed using command-line flags, such as
`--events.enabled=False`. These are parsed/delimited by `.` and merged with the
contents of `~/.spinbot/config`.

## Running for development

You will need the following:

* [python3](https://www.python.org/download/releases/3.0/)
* [pip](https://pypi.org/project/pip/#description)
* [make](https://www.gnu.org/software/make/) -- largely optional, you can read
  the `Makefile` in this repo to see what it executes (it's just a few, small
  commands).

1. Install the necessary packages:

  ```bash
  make init
  ```

2. Edit the config file to tell the bot to use local storage:

   ```
   storage:
     local:
     path: ~/.spinbot/cache
   ```

   Then create that file: `mkdir ~/.spinbot && touch ~/.spinbot/cache`

3. Create a github token and add it to the config:

   ```
   github:
     token_path: ~/.spinbot/github_token
   ```

4. Run `./spinbot.py`. It will start up a web server. Trigger a run by
   sending a `POST` request:
   
   `$ curl -X POST http://localhost:8080 -o /dev/null` 

If you want to build the Docker container, either rely on the `Dockerfile` in
the root of the repository, or run:

```bash
make docker
```

This assumes you have build access in the `spinnaker-community` GCP project
-- you can edit `PROJECT` variable in the `Makefile` to change this.

## Deploying to Production

Upon merge, a build will be triggered in the [`spinnaker-community` Google Cloud
Build project](https://console.cloud.google.com/cloud-build?project=spinnaker-community).
This build will deploy the latest version to production.

It runs as a [Google Cloud Run service](https://pantheon.corp.google.com/run/detail/us-central1/spinbot/revisions?project=spinnaker-community). 

## How it works

To help manage the Spinnaker GitHub repos, the bot is does two things:

1. Handle [events](https://developer.github.com/v3/activity/events/) as
   they arrive in the repositories you've configured.

   The bot applies each listed event handler in `event.handlers` to every event
   it sees since the last time it ran. It keeps track of this by writing the
   timestamp of the newest event it processed into either local storage, or GCS
   (depends on the `storage` configuration).

2. Apply policies to [issues](https://developer.github.com/v3/issues/), [pull
   requests](https://developer.github.com/v3/pulls/), and maybe more in the
   future.

   The bot pulls every issue/pull request from each repository, and applies
   each `policy.policies` to it. This is quite a bit more expensive (in API
   calls) and ideally shouldn't be done with every run.

> The reason for handling these two things separately is that old issues/pull
> requests don't generate events, but need attention.

### Writing a new event handler

To create a new event handler, create a file: `events/my_event_handler.py`:

```python
from .handler import Handler

# !IMPORTANT! The class name must match the "snake_case" of the filename. This
#             is how the handler is automatically configured & registered when
#             entered in ~/.spinbot/config
class MyEventHandler(Handler):
    def __init__(self):
        super().__init__()
        # Calling that init function gives you the following:
        # * self.config (comes from the per-event-handler config in
        #   events.handler.*.config)
        # * self.logging (a logger just for this class)

    def handles(self, event):
        # return True i.f.f. the input event can be handled by this handler

    def handle(self, gh, event):
        # gh is client under ./gh/client.py -- it's meant to wrap API calls
        # event is the event to process

# !IMPORTANT! Call your constructur here
MyEventHandler()
```

And configure it using:

```yaml
...
event:
  handlers:
  - name: my_event_handler
    config:
      custom: 'value'
...
```

### Writing a new policy

To create a new policy, create a file: `policy/my_policy.py`:

```python
from .policy import Policy

# !IMPORTANT! The class name must match the "snake_case" of the filename. This
#             is how the policy is automatically configured & registered when
#             entered in ~/.spinbot/config
class MyPolicy(Policy):
    def __init__(self):
        super().__init__()
        # Calling that init function gives you the following:
        # * self.config (comes from the per-policy config in
        #   policy.policies.*.config)
        # * self.logging (a logger just for this class)

    def applies(self, object):
        # return True i.f.f. the input object applies to this policy

    def apply(self, gh, object):
        # gh is client under ./gh/client.py -- it's meant to wrap API calls
        # object is the resource to process

# !IMPORTANT! Call your constructur here
MyPolicy()
```

And configure it using:

```yaml
...
policy:
  policies:
  - name: my_policy
    config:
      custom: 'value'
...
```
