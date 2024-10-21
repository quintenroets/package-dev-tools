from package_dev_tools.utils.badge import Badge, BadgeUpdater
from package_dev_tools.utils.package import PackageInfo


def check_shields() -> None:
    package_info = PackageInfo()
    versions = package_info.listed_version.replace("<=", "").split(", <")
    python_version = "--".join(versions)
    python_version_badge = f"python-{python_version}+"
    operating_systems = package_info.supported_operating_systems
    operating_system = "os-" + "%20%7c%20".join(operating_systems)
    badges = (
        Badge("Python version", python_version_badge),
        Badge("Operating system", operating_system),
    )
    for badge in badges:
        BadgeUpdater(badge).run()
