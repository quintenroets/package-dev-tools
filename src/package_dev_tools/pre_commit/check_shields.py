from package_dev_tools.utils.badge import Badge, BadgeUpdater
from package_dev_tools.utils.package import PackageInfo


def check_shields() -> None:
    package_info = PackageInfo()
    python_version = create_python_version_badge(package_info=package_info)
    operating_systems = package_info.supported_operating_systems
    operating_system = "os-" + "%20%7c%20".join(operating_systems)
    badges = (
        Badge("Python version", python_version),
        Badge("Operating system", operating_system),
    )
    for badge in badges:
        BadgeUpdater(badge).run()


def create_python_version_badge(package_info: PackageInfo) -> str:
    minimum_version = package_info.required_python_version
    if "," in package_info.listed_version:  # pragma: nocover
        maximum_version = f"3.{package_info.latest_supported_python_minor}"
        version = minimum_version + "--" + maximum_version
    else:
        version = minimum_version + "+"
    return f"python-{version}"
