import enum
import logging
import pathlib
import subprocess
from textwrap import dedent
from time import sleep

from ..executors import Executor
from .image import Image

logger = logging.getLogger(__name__)


class BuilddImageAlias(enum.Enum):
    """Mappings for supported buildd images."""

    XENIAL = 16.04
    BIONIC = 18.04
    FOCAL = 20.04


class BuilddImage(Image):
    """Buildd Image Configurator.

    Args:
        alias: Image alias / version.
        hostname: Hostname to configure.

    Attributes:
        alias: Image alias / version.
        hostname: Hostname to configure.
        revision: Setup compatibility revision.
        version: Image version (e.g. "16.04").
    """

    def __init__(
        self,
        *,
        alias: BuilddImageAlias,
        hostname: str = "craft-buildd-instance",
    ):
        """Initialize buildd image."""
        super().__init__(
            version=str(alias.value),
            revision=0,
        )

        self.alias = alias
        self.hostname = hostname

    def setup(self, *, executor: Executor) -> None:
        """Configure buildd image to minimum baseline.

        Install & wait for ready:
        - hostname
        - networking (ip & dns)
        - apt cache
        - snapd

        Args:
            executor: Executor for target container.
        """
        self._setup_hostname(executor=executor)
        self._setup_wait_for_system_ready(executor=executor)
        self._setup_resolved(executor=executor)
        self._setup_networkd(executor=executor)
        self._setup_wait_for_network(executor=executor)
        self._setup_apt(executor=executor)
        self._setup_snapd(executor=executor)

    def _setup_apt(self, *, executor: Executor) -> None:
        """Configure apt & update cache.

        Args:
            executor: Executor for target container.
        """
        executor.execute_run(command=["apt-get", "update"], check=True)

    def _setup_hostname(self, *, executor: Executor) -> None:
        """Configure hostname, installing /etc/hostname.

        Args:
            executor: Executor for target container.
        """
        executor.create_file(
            destination=pathlib.Path("/etc/hostname"),
            content=self.hostname.encode(),
            file_mode="0644",
        )

    def _setup_networkd(self, *, executor: Executor) -> None:
        """Configure networkd and start it.

        Installs eth0 network configuration using ipv4.

        Args:
            executor: Executor for target container.
        """
        executor.create_file(
            destination=pathlib.Path("/etc/systemd/network/10-eth0.network"),
            content=dedent(
                """
                [Match]
                Name=eth0

                [Network]
                DHCP=ipv4
                LinkLocalAddressing=ipv6

                [DHCP]
                RouteMetric=100
                UseMTU=true
                """
            ).encode(),
            file_mode="0644",
        )

        executor.execute_run(
            command=["systemctl", "enable", "systemd-networkd"], check=True
        )

        executor.execute_run(
            command=["systemctl", "restart", "systemd-networkd"], check=True
        )

    def _setup_resolved(self, *, executor: Executor) -> None:
        """Configure system-resolved to manage resolve.conf.

        Args:
            executor: Executor for target container.
            timeout_secs: Timeout in seconds.
        """
        executor.execute_run(
            command=[
                "ln",
                "-sf",
                "/run/systemd/resolve/resolv.conf",
                "/etc/resolv.conf",
            ],
            check=True,
        )

        executor.execute_run(
            command=["systemctl", "enable", "systemd-resolved"], check=True
        )

        executor.execute_run(
            command=["systemctl", "restart", "systemd-resolved"], check=True
        )

    def _setup_snapd(self, *, executor: Executor) -> None:
        """Install snapd and dependencies and wait until ready.

        Args:
            executor: Executor for target container.
            timeout_secs: Timeout in seconds.
        """
        executor.execute_run(
            command=[
                "apt-get",
                "install",
                "fuse",
                "udev",
                "--yes",
            ],
            check=True,
        )

        executor.execute_run(
            command=["systemctl", "enable", "systemd-udevd"], check=True
        )
        executor.execute_run(
            command=["systemctl", "start", "systemd-udevd"], check=True
        )
        executor.execute_run(
            command=["apt-get", "install", "snapd", "--yes"], check=True
        )
        executor.execute_run(command=["systemctl", "start", "snapd.socket"], check=True)
        executor.execute_run(
            command=["systemctl", "start", "snapd.service"], check=True
        )
        executor.execute_run(
            command=["snap", "wait", "system", "seed.loaded"], check=True
        )

    def _setup_wait_for_network(
        self, *, executor: Executor, timeout_secs: int = 60
    ) -> None:
        """Wait until networking is ready.

        Args:
            executor: Executor for target container.
            timeout_secs: Timeout in seconds.
        """
        logger.info("Waiting for networking to be ready...")
        for i in range(timeout_secs * 2):
            proc = executor.execute_run(
                command=["getent", "hosts", "snapcraft.io"], stdout=subprocess.DEVNULL
            )
            if proc.returncode == 0:
                break

            sleep(0.5)
        else:
            logger.warning("Failed to setup networking.")

    def _setup_wait_for_system_ready(
        self, *, executor: Executor, timeout_secs: int = 60
    ) -> None:
        """Wait until system is ready.

        Args:
            executor: Executor for target container.
            timeout_secs: Timeout in seconds.
        """
        logger.info("Waiting for container to be ready...")
        for i in range(timeout_secs * 2):
            proc = executor.execute_run(
                command=["systemctl", "is-system-running"], stdout=subprocess.PIPE
            )

            running_state = proc.stdout.decode().strip()
            if running_state in ["running", "degraded"]:
                break

            logger.debug(f"systemctl is-system-running: {running_state!r}")
            sleep(0.5)
        else:
            logger.warning(
                f"Systemd failed to reach target before timeout: {proc.stdout}."
            )
