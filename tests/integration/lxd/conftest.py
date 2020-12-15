import pathlib
import random
import string
import subprocess
import time

import pytest

from craft_providers.lxd import LXC
from craft_providers.lxd.lxc import purge_project


def run(cmd, **kwargs):
    return subprocess.run(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True, **kwargs
    )


@pytest.fixture()
def lxd():
    lxc_path = pathlib.Path("/snap/bin/lxc")
    if lxc_path.exists():
        already_installed = True
    else:
        already_installed = False
        run(["sudo", "snap", "install", "lxd"])

    yield lxc_path

    if not already_installed:
        run(["sudo", "snap", "remove", "lxd"])


@pytest.fixture()
def lxc(lxd):
    yield LXC()


@pytest.fixture()
def project(lxc):
    project = "ptest-" + "".join(random.choices(string.ascii_uppercase, k=8))
    lxc.project_create(project=project)

    default_cfg = lxc.profile_show(profile="default", project="default")
    lxc.profile_edit(profile="default", project=project, config=default_cfg)

    projects = lxc.project_list()
    assert project in projects

    instances = lxc.list(project=project)
    assert instances == []

    yield project

    purge_project(lxc=lxc, project=project)


@pytest.fixture()
def instance_name():
    return "itest-" + "".join(random.choices(string.ascii_uppercase, k=8))


@pytest.fixture()
def instance(instance_launcher, instance_name):
    instance_launcher(
        config_keys=dict(),
        instance=instance_name,
        image_remote="ubuntu",
        image="16.04",
        project=project,
        ephemeral=False,
    )

    return instance_name


@pytest.fixture()
def instance_launcher(lxc, project, instance_name):
    def launch(
        config_keys=None,
        instance_name=instance_name,
        image_remote="ubuntu",
        image="16.04",
        project=project,
        ephemeral=False,
    ) -> str:
        lxc.launch(
            config_keys=dict(),
            instance=instance_name,
            image_remote="ubuntu",
            image="16.04",
            project=project,
            ephemeral=False,
        )

        # Make sure container is ready
        for i in range(0, 60):
            proc = lxc.exec(
                project=project,
                instance=instance_name,
                command=["systemctl", "is-system-running"],
                stdout=subprocess.PIPE,
            )

            running_state = proc.stdout.decode().strip()
            if running_state in ["running", "degraded"]:
                break
            time.sleep(0.5)

        return instance_name

    yield launch


@pytest.fixture()
def ephemeral_instance(lxc, project):
    instance = "itest-" + "".join(random.choices(string.ascii_uppercase, k=8))
    lxc.launch(
        config_keys=dict(),
        instance=instance,
        image_remote="ubuntu",
        image="16.04",
        project=project,
        ephemeral=True,
    )

    return instance
