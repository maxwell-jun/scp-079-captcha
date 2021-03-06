# SCP-079-CAPTCHA - Provide challenges for new joined members
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-CAPTCHA.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Optional

from pyrogram import Client, Message

from .. import glovar
from .etc import code, lang, thread
from .file import save
from .telegram import delete_messages, get_messages, leave_chat

# Enable logging
logger = logging.getLogger(__name__)


def delete_hint(client: Client) -> bool:
    # Delete hint messages
    try:
        # Get the wait group list
        wait_group_list = {gid for uid in list(glovar.user_ids) for gid in list(glovar.user_ids[uid]["wait"])}

        # Proceed
        for gid in list(glovar.message_ids):
            # Regular hint
            mid = glovar.message_ids[gid]["hint"]
            if mid and gid not in wait_group_list:
                glovar.message_ids[gid]["hint"] = 0
                delete_message(client, gid, mid)

            # Flood static hint
            mids = glovar.message_ids[gid]["flood"]
            if mids and gid not in wait_group_list:
                glovar.message_ids[gid]["flood"] = set()
                thread(delete_messages, (client, gid, mids))

        # Save the data
        save("message_ids")

        return True
    except Exception as e:
        logger.warning(f"Delete hint error: {e}", exc_info=True)

    return False


def delete_message(client: Client, gid: int, mid: int) -> bool:
    # Delete a single message
    try:
        if not gid or not mid:
            return True

        mids = [mid]
        thread(delete_messages, (client, gid, mids))

        return True
    except Exception as e:
        logger.warning(f"Delete message error: {e}", exc_info=True)

    return False


def get_config_text(config: dict) -> str:
    # Get config text
    result = ""
    try:
        # Basic
        default_text = (lambda x: lang("default") if x else lang("custom"))(config.get("default"))
        delete_text = (lambda x: lang("enabled") if x else lang("disabled"))(config.get("delete"))
        restrict_text = (lambda x: lang("enabled") if x else lang("disabled"))(config.get("restrict"))
        result += (f"{lang('config')}{lang('colon')}{code(default_text)}\n"
                   f"{lang('delete')}{lang('colon')}{code(delete_text)}\n"
                   f"{lang('restrict')}{lang('colon')}{code(restrict_text)}\n")

        # Others
        for the_type in ["ban", "forgive", "hint", "pass", "manual"]:
            the_text = (lambda x: lang("enabled") if x else lang("disabled"))(config.get(the_type))
            result += f"{lang(the_type)}{lang('colon')}{code(the_text)}\n"
    except Exception as e:
        logger.warning(f"Get config text error: {e}", exc_info=True)

    return result


def get_message(client: Client, gid: int, mid: int) -> Optional[Message]:
    # Get a single message
    result = None
    try:
        mids = [mid]
        result = get_messages(client, gid, mids)
        if result:
            result = result[0]
    except Exception as e:
        logger.warning(f"Get message error: {e}", exc_info=True)

    return result


def leave_group(client: Client, gid: int) -> bool:
    # Leave a group, clear it's data
    try:
        glovar.left_group_ids.add(gid)
        save("left_group_ids")
        thread(leave_chat, (client, gid))

        glovar.admin_ids.pop(gid, set())
        save("admin_ids")

        glovar.message_ids.pop(gid, {})
        save("message_ids")

        glovar.configs.pop(gid, {})
        save("configs")

        return True
    except Exception as e:
        logger.warning(f"Leave group error: {e}", exc_info=True)

    return False
