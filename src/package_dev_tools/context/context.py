from package_utils.context import Context

from package_dev_tools.models import Config, Options, Secrets

context = Context(Options, Config, Secrets)
