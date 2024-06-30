from package_utils.context.entry_point import create_entry_point

from package_dev_tools import main
from package_dev_tools.context import context

entry_point = create_entry_point(main, context)
