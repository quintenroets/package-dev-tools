from package_dev_tools.utils.badge import Badge, BadgeUpdater
from package_dev_tools.utils.package import PackageInfo


def check_shields() -> None:
    package_info = PackageInfo()
    python_version = f"python-{package_info.required_python_version}+"
    operating_systems = package_info.supported_operating_systems
    operating_system = "os-" + "%20%7c%20".join(operating_systems)
    badges = (
        Badge("Python version", python_version),
        Badge("Operating system", operating_system),
    )
    for badge in badges:
        BadgeUpdater(badge).run()
