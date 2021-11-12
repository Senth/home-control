from time import time
from typing import Any, Dict, Union

from pyunifi.controller import Controller
from tealprint import TealPrint

from ...config import config
from .guest_of import GuestOf


class _UserGroup:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.last_active_time: float = 0
        self.is_home: bool = False
        self.was_home: bool = False


class UnifiApi:
    def __init__(self) -> None:
        self._controller: Controller
        self._clients: Dict[str, Any] = {}
        self._usergroups: Dict[str, _UserGroup] = {}

    def update(self) -> None:
        try:
            if getattr(self, "_controller", None) is None:
                self._init_controller()

            self._update_user_groups()
            self._update_clients()
            self._update_last_active()
        except:
            TealPrint.error("❗ Something went wrong connecting to UNIFI", print_exception=True)

    def _init_controller(self) -> None:
        self._controller = Controller(
            config.unifi.host,
            config.unifi.username,
            config.unifi.password,
            port=config.unifi.port,
            site_id=config.unifi.site_id,
            ssl_verify=True,
        )

    def _update_user_groups(self) -> None:
        TealPrint.debug("Getting UNIFI user groups")
        for group in self._controller.get_user_groups():
            id = str(group["_id"])
            name = str(group["name"])

            # Create new
            if id not in self._usergroups:
                self._usergroups[id] = _UserGroup(id, name)
            # Update existing
            else:
                self._usergroups[id].name = name

    def _update_clients(self) -> None:
        TealPrint.debug("Getting UNIFI clients")
        for client in self._controller.get_clients():
            self._clients[client["mac"]] = client

    def _update_last_active(self) -> None:
        TealPrint.debug("Updating last active time")
        for client in self._clients.values():
            if "usergroup_id" in client:
                group_id = client["usergroup_id"]

            if not group_id:
                group_id = self._get_default_group().id

            group = self._usergroups[group_id]
            group.was_home = group.is_home
            group.last_active_time = time()

        # Log if Home/Away was changed
        for group in self._usergroups.values():
            group.was_home = group.is_home
            group.is_home = UnifiApi._calculate_is_home(group)

            if group.was_home != group.is_home:
                state_msg = "home" if group.is_home else "away"
                TealPrint.info(f"👨‍👨‍👧‍👦 Usergroup {group.name} is {state_msg}")

    def _get_default_group(self) -> _UserGroup:
        for group in self._usergroups.values():
            if group.name == GuestOf.both.value:
                return group
        raise Exception("No default usergroup found")

    def get_client(self, mac_address: str) -> Union[Any, None]:
        """Tries to find the client with the specified mac address. Returns None if it hasn't been active yet"""
        if mac_address in self._clients:
            return self._clients[mac_address]

    def is_guest_active(self, *guest_of_list: GuestOf) -> bool:
        """Checks if a guest is active on the network

        Args:
            guest_of_list (GuestOf): the guest group to check. If empty, it will check all guest groups.
        """
        if len(guest_of_list) == 0:
            return self._is_any_guest_active()

        for guest_of in guest_of_list:
            usergroup = self._get_user_group(guest_of)
            if usergroup and usergroup.is_home:
                return True

        return False

    def _is_any_guest_active(self) -> bool:
        for guest_of in GuestOf:
            active = self.is_guest_active(guest_of)
            if active:
                return True
        return False

    def _get_user_group(self, friend_of: GuestOf) -> Union[_UserGroup, None]:
        for usergroup in self._usergroups.values():
            if usergroup.name == friend_of.value:
                return usergroup

    @staticmethod
    def _calculate_is_home(usergroup: _UserGroup) -> bool:
        now = time()
        elapsed_time = now - usergroup.last_active_time
        return elapsed_time <= config.unifi.guest_inactive_time
