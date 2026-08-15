from package_dev_tools.utils.badge import Badge, BadgeUpdater
from package_dev_tools.utils.package import PackageInfo
from package_dev_tools.utils.python_versions import PythonVersions


def check_shields() -> None:
    info = PackageInfo()
    python_versions = describe_python_versions(info.python_versions)
    operating_systems = Badge.separator.join(info.supported_operating_systems)
    badges = (
        Badge("Python version", f"python-{python_versions}"),
        Badge("Operating system", f"os-{operating_systems}"),
    )
    for badge in badges:
        BadgeUpdater(badge).run()


def describe_python_versions(versions: PythonVersions) -> str:
    return (
        Badge.separator.join(versions.supported)
        if versions.has_excluded_minors or versions.maximum == versions.required
        else f"{versions.required}+"
        if versions.maximum is None
        else f"{versions.required}--{versions.maximum}"
    )
