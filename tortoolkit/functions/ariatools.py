# -*- coding: utf-8 -*-
# (c) YashDK [yash-dk@github]
# (c) modified by AmirulAndalib [amirulandalib@github]

import asyncio
import logging
import os
from functools import partial

import aria2p
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from ..core.getVars import get_val
from ..core.status.status import ARTask

# referenced from public leech
# pylint: disable=no-value-for-parameter
torlog = logging.getLogger(__name__)
aloop = asyncio.get_event_loop()


async def aria_start():
    aria2_daemon_start_cmd = []
    # start the daemon, aria2c command

    aria2_daemon_start_cmd.append("aria2c")
    aria2_daemon_start_cmd.append("--daemon=true")
    aria2_daemon_start_cmd.append("--enable-rpc")
    aria2_daemon_start_cmd.append("--rpc-listen-all=true")
    aria2_daemon_start_cmd.append(f"--rpc-listen-port=8100")
    aria2_daemon_start_cmd.append("--rpc-max-request-size=1024M")

    aria2_daemon_start_cmd.append("--conf-path=/torapp/aria2.conf")

    #
    torlog.debug(aria2_daemon_start_cmd)
    #
    process = await asyncio.create_subprocess_exec(
        *aria2_daemon_start_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    torlog.debug(stdout)
    torlog.debug(stderr)
    arcli = await aloop.run_in_executor(
        None, partial(aria2p.Client, host="http://localhost", port=8100, secret="")
    )
    aria2 = await aloop.run_in_executor(None, aria2p.API, arcli)

    return aria2


async def add_magnet(aria_instance, magnetic_link, c_file_name):
    try:
        download = await aloop.run_in_executor(
            None, aria_instance.add_magnet, magnetic_link
        )
    except Exception as e:
        return (
            False,
            "**𝙵𝙰𝙸𝙻𝙴𝙳** \n" + str(e) + " \n𝙿𝚕𝚎𝚊𝚜𝚎 𝚍𝚘 𝚗𝚘𝚝 𝚜𝚎𝚗𝚍 𝚂𝙻𝙾𝚆 𝚕𝚒𝚗𝚔𝚜. 𝚁𝚎𝚊𝚍 /help",
        )
    else:
        return True, "" + download.gid + ""


async def add_torrent(aria_instance, torrent_file_path):
    if torrent_file_path is None:
        return (
            False,
            "**𝙵𝙰𝙸𝙻𝙴𝙳** \n\n𝚜𝚘𝚖𝚎𝚝𝚑𝚒𝚗𝚐 𝚠𝚛𝚘𝚗𝚐𝚒𝚗𝚐𝚜 𝚠𝚑𝚎𝚗 𝚝𝚛𝚢𝚒𝚗𝚐 𝚝𝚘 𝚊𝚍𝚍 <u>𝚃𝙾𝚁𝚁𝙴𝙽𝚃</u> 𝚏𝚒𝚕𝚎",
        )
    if os.path.exists(torrent_file_path):
        # Add Torrent Into Queue
        try:

            download = await aloop.run_in_executor(
                None,
                partial(
                    aria_instance.add_torrent,
                    torrent_file_path,
                    uris=None,
                    options=None,
                    position=None,
                ),
            )

        except Exception as e:
            return (
                False,
                "**𝙵𝙰𝙸𝙻𝙴𝙳** \n"
                + str(e)
                + "𝙿𝚕𝚎𝚊𝚜𝚎 𝚍𝚘 𝚗𝚘𝚝 𝚜𝚎𝚗𝚍 𝚂𝙻𝙾𝚆 𝚕𝚒𝚗𝚔𝚜. 𝚁𝚎𝚊𝚍 /help",
            )
        else:
            return True, "" + download.gid + ""
    else:
        return (
            False,
            "**𝙵𝙰𝙸𝙻𝙴𝙳** \n"
            + str(e)
            + " \n𝙿𝚕𝚎𝚊𝚜𝚎 𝚝𝚛𝚢 𝚘𝚝𝚑𝚎𝚛 𝚜𝚘𝚞𝚛𝚌𝚎𝚜 𝚝𝚘 𝚐𝚎𝚝 𝚠𝚘𝚛𝚔𝚊𝚋𝚕𝚎 𝚕𝚒𝚗𝚔",
        )


async def add_url(aria_instance, text_url, c_file_name):
    uris = [text_url]
    # Add URL Into Queue
    try:

        download = await aloop.run_in_executor(None, aria_instance.add_uris, uris)

    except Exception as e:
        return (
            False,
            "**𝙵𝙰𝙸𝙻𝙴𝙳** \n" + str(e) + " \n𝙿𝚕𝚎𝚊𝚜𝚎 𝚍𝚘 𝚗𝚘𝚝 𝚜𝚎𝚗𝚍 𝚂𝙻𝙾𝚆 𝚕𝚒𝚗𝚔𝚜. 𝚁𝚎𝚊𝚍 /help",
        )
    else:
        return True, "" + download.gid + ""


async def check_metadata(aria2, gid):
    file = await aloop.run_in_executor(None, aria2.get_download, gid)
    torlog.info(file)
    if not file.followed_by_ids:
        return None
    new_gid = file.followed_by_ids[0]
    torlog.info("Changing GID " + gid + " to " + new_gid)
    return new_gid


async def aria_dl(incoming_link, c_file_name, sent_message_to_update_tg_p, user_msg):
    aria_instance = await aria_start()

    ar_task = ARTask(None, sent_message_to_update_tg_p, aria_instance, None)
    await ar_task.set_original_mess()

    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = await add_magnet(
            aria_instance, incoming_link, c_file_name
        )
    elif incoming_link.lower().endswith(".torrent"):
        # sagtus, err_message = await add_torrent(aria_instance, incoming_link)
        # sagtus, err_message = await add_url(aria_instance, incoming_link, c_file_name)
        await ar_task.set_inactive("𝙲𝚊𝚗'𝚝 𝚍𝚘𝚠𝚗𝚕𝚘𝚊𝚍 𝚝𝚑𝚒𝚜 .𝚝𝚘𝚛𝚛𝚎𝚗𝚝 𝚏𝚒𝚕𝚎")
        return False, ar_task
    else:
        sagtus, err_message = await add_url(aria_instance, incoming_link, c_file_name)
    if not sagtus:
        await ar_task.set_inactive(err_message)
        return sagtus, ar_task

    torlog.info(err_message)

    await ar_task.set_gid(err_message)

    op = await check_progress_for_dl(
        aria_instance,
        err_message,
        sent_message_to_update_tg_p,
        None,
        ar_task,
        user_msg=user_msg,
    )
    if incoming_link.startswith("magnet:"):
        #
        err_message = await check_metadata(aria_instance, err_message)
        #
        await asyncio.sleep(1)
        if err_message is not None:
            op = await check_progress_for_dl(
                aria_instance,
                err_message,
                sent_message_to_update_tg_p,
                None,
                ar_task,
                user_msg=user_msg,
            )
        else:
            await ar_task.set_inactive("𝙲𝚊𝚗'𝚝 𝚐𝚎𝚝 𝚖𝚎𝚝𝚊𝚍𝚊𝚝𝚊.\n")
            return False, ar_task
    await asyncio.sleep(1)

    if op is None:
        await ar_task.set_inactive(
            "𝙺𝚗𝚘𝚠𝚗 𝚎𝚛𝚛𝚘𝚛. 𝙽𝚘𝚝𝚑𝚒𝚗𝚐 𝚠𝚛𝚘𝚗𝚐 𝚑𝚎𝚛𝚎. 𝚈𝚘𝚞 𝚍𝚒𝚍𝚗'𝚝 𝚏𝚘𝚕𝚕𝚘𝚠 𝚒𝚗𝚜𝚝𝚛𝚞𝚌𝚝𝚒𝚘𝚗𝚜."
        )
        return False, ar_task
    else:
        statusr, stmsg = op
        if statusr:
            file = await aloop.run_in_executor(
                None, aria_instance.get_download, err_message
            )
            to_upload_file = file.name
            await ar_task.set_path(to_upload_file)
            await ar_task.set_done()
            return True, ar_task
        else:
            await ar_task.set_inactive(stmsg)
            return False, ar_task


async def check_progress_for_dl(
    aria2, gid, event, previous_message, task, rdepth=0, user_msg=None
):
    try:
        file = await aloop.run_in_executor(None, aria2.get_download, gid)
        complete = file.is_complete
        if not complete:
            if not file.error_message:
                msg = ""
                # REMOVED HEROKU BLOCK

                await task.refresh_info(file)
                await task.update_message()

            else:
                msg = file.error_message
                await event.edit(f"`{msg}`", parse_mode="html", buttons=None)
                torlog.error(f"The aria download failed due to this reason:- {msg}")
                return False, f"The aria download failed due to this reason:- {msg}"
            await asyncio.sleep(get_val("EDIT_SLEEP_SECS"))

            # TODO idk not intrested in using recursion here
            return await check_progress_for_dl(
                aria2, gid, event, previous_message, task, user_msg=user_msg
            )
        else:
            await event.remove(
                f"📥**__ᴅᴏᴡɴʟᴏᴀᴅ ᴄᴏᴍᴘʟᴇᴛᴇ:__** \n\n**🗂ꜰɪʟᴇ ɴᴀᴍᴇ:** {file.name}\n\n**💽ꜰɪʟᴇ ꜱɪᴢᴇ:** {file.total_length_string()}",
                buttons=None,
            )
            return True, "**<i>🤩ᴅᴏᴡɴʟᴏᴀᴅ ᴄᴏᴍᴘʟᴇᴛᴇ!</i>**"
    except aria2p.client.ClientException as e:
        if " not found" in str(e) or "'file'" in str(e):
            fname = "N/A"
            try:
                fname = file.name
            except:
                pass
            task.cancel = True
            await task.set_inactive()
            return False, f"The Download was canceled. {fname}"
        else:
            torlog.warning("Errored due to ta client error.")
    except MessageNotModifiedError:
        pass
    except RecursionError:
        file.remove(force=True)
        return False, "The link is basically dead."
    except Exception as e:
        torlog.info(str(e))
        if " not found" in str(e) or "'file'" in str(e):
            return False, "The Download was canceled."
        else:
            torlog.warning(str(e))
            return False, f"Error: {str(e)}"


async def remove_dl(gid):
    aria2 = await aria_start()
    try:
        downloads = await aloop.run_in_executor(None, aria2.get_download, gid)
        downloads.remove(force=True, files=True)
    except:
        torlog.exception("exc")
