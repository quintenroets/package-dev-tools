from dev_tools.actions.substitute_template_name import Project


def test_naming_conversions() -> None:
    project = Project("python-project-template")
    assert project.package_slug == "python-project-template"
    assert project.package_name == "python_project_template"
    assert project.name == "Python Project Template"
