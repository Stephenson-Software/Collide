"""Reports that Collide was used to the trace service, and nothing else.

What is sent: the program's name (``Collide``) and version with every event -- a
``startup`` event, and an ideas-written event when a session's ideas are saved. Every event also carries a random installation ID
(tag ``install``, see ``installIdFile``) so installations can be counted rather than
events. Nothing about you, the keywords or the ideas.

Reporting is on by default. The first launch writes a ``usage_reporting``
block to ``settings.json`` and prints a one-line notice saying so and how to
turn it off; setting ``enabled`` to ``false`` there does. So do the
``TRACE_USAGE_REPORTING=off`` and ``DO_NOT_TRACK=1`` environment variables,
which every trace client honours and which win over the settings file because
the client checks them first. Every call returns immediately and never raises:
the network happens on a daemon thread owned by the vendored client in
``trace_client.py``. Details: https://danielstephenson.dev/usage-reporting
"""
import atexit
import json
import os
import sys

from trace_client import TraceClient, allows_reporting, environment_opts_out

# @author Daniel McCoy Stephenson
# @since September 24th, 2026

APPLICATION = "Collide"
SETTINGS_SECTION = "usage_reporting"
DEFAULT_ENDPOINT = "https://trace.danielstephenson.dev"
# The program key Collide ships with. Keys identify a program rather than
# guard anything (trace's ADR 0001), so it is kept here in the open.
DEFAULT_KEY = "U5oB2v6sYlgEC9xayQys8irU0lJR6dfawIv3E4SF_DI"
VERSION = "0.1.0"

_HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.normpath(os.path.join(_HERE, "..", "settings.json"))

DETAILS_URL = "https://danielstephenson.dev/usage-reporting"

FIRST_RUN_NOTICE = (
    "Usage reporting is on: Collide sends its name and version at startup and an ideas-written event when a session is saved to "
    "https://trace.danielstephenson.dev, with a random installation ID - nothing about you, the keywords or the ideas. "
    'Turn it off with "usage_reporting": {"enabled": false} in settings.json, or for every '
    "trace-reporting program with the environment variable TRACE_USAGE_REPORTING=off. "
    "Details: " + DETAILS_URL
)

# Shown on the first launch instead when TRACE_USAGE_REPORTING=off or DO_NOT_TRACK=1 is
# already set: the settings block is still written, but saying reporting is on would mislead.
FIRST_RUN_NOTICE_OFF_BY_ENVIRONMENT = "Usage reporting is off (environment). Details: " + DETAILS_URL


def firstRunNotice():
    """The line the first launch prints: FIRST_RUN_NOTICE, unless the environment has opted out."""
    if environment_opts_out():
        return FIRST_RUN_NOTICE_OFF_BY_ENVIRONMENT
    return FIRST_RUN_NOTICE


def defaultSettings():
    """The usage_reporting block written to the settings file on the first launch."""
    return {"enabled": True, "endpoint": DEFAULT_ENDPOINT, "key": DEFAULT_KEY}


def installIdFile():
    """Where this installation's random ID (the tag ``install`` on every event) is kept:
    ``<user data dir>/collide/trace-install-id``, the user data dir being %APPDATA% on Windows,
    ~/Library/Application Support on macOS and $XDG_DATA_HOME (or ~/.local/share) elsewhere.
    The client only reads or creates it when reporting is on; deleting it resets the ID."""
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", "").strip() or os.path.join(home, "AppData", "Roaming")
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", "").strip() or os.path.join(home, ".local", "share")
    return os.path.join(base, APPLICATION.lower(), "trace-install-id")


def _normalise(key):
    """A settings key in lower case with everything but letters and digits dropped, so
    ``usage_reporting``, ``usage-reporting``, ``usageReporting`` and ``UsageReporting`` all
    read ``usagereporting``."""
    return "".join(c for c in str(key).lower() if c.isascii() and c.isalnum())


def hasNearMissOptOut(settings):
    """Whether ``settings`` holds an attempt to turn usage reporting off that is not written
    exactly as ``"usage_reporting": {"enabled": ...}``. Such a setting used to be ignored: the
    default block, ``"enabled": true``, was written next to it and reporting stayed on. An
    operator who wrote any of these did not ask for reporting, so each counts as off:

    * a top-level key that spells "usage reporting" another way (``usage-reporting``,
      ``usageReporting``, ``UsageReporting``, ...) holding a value instead of a block that is
      not clearly on (the client's ``allows_reporting``);
    * inside any such block, a key that spells "enabled" another way (``enable``,
      ``Enabled``, ...) whose value is not clearly on, or one that spells "disabled"
      (``disabled``, ``disable``, ...) whose value is on.
    """
    for key, value in settings.items():
        if "usagereport" not in _normalise(key):
            continue
        if not isinstance(value, dict):
            if not allows_reporting(value):
                return True
            continue
        for child, childValue in value.items():
            if key == SETTINGS_SECTION and child == "enabled":
                continue  # the switch itself, read by buildClient
            name = _normalise(child)
            if "disabl" in name and allows_reporting(childValue):
                return True
            if "enabl" in name and not allows_reporting(childValue):
                return True
    return False


def loadSettings(settingsFile=SETTINGS_FILE, log=print):
    """Read the usage_reporting block from the settings file, writing the default block
    (and printing the one-time notice) when the file does not have one yet.

    Returns the usage_reporting settings, or None if the settings file exists but cannot be
    read, in which case nothing is reported and the file is left alone.
    """
    settings = {}
    if os.path.exists(settingsFile):
        try:
            with open(settingsFile, "r") as f:
                settings = json.load(f)
            if not isinstance(settings, dict):
                raise ValueError("settings file is not a JSON object")
        except (OSError, ValueError) as e:
            log("Could not read %s (%s); usage reporting is off until it is fixed." % (settingsFile, e))
            return None

    section = settings.get(SETTINGS_SECTION)
    # An opt-out written under another spelling (see hasNearMissOptOut) wins over the block.
    nearMissOptOut = hasNearMissOptOut(settings)
    if isinstance(section, dict):
        return dict(section, enabled=False) if nearMissOptOut else section
    if SETTINGS_SECTION in settings:
        # "usage_reporting": false (or "off", null, ...) is a setting, not a missing block:
        # read it as ``enabled`` and leave the file alone rather than replace it with the
        # default block, which would turn reporting back on.
        return {"enabled": section}

    if nearMissOptOut:
        # The block is written with the real switch off, next to the near-miss, so the file
        # says off in the spelling this program reads; no "reporting is on" notice is shown.
        settings[SETTINGS_SECTION] = dict(defaultSettings(), enabled=False)
    else:
        settings[SETTINGS_SECTION] = defaultSettings()
        log(firstRunNotice())
    try:
        with open(settingsFile, "w") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")
    except OSError as e:
        log("Could not write %s (%s); the notice above will be shown again next time." % (settingsFile, e))
    return settings[SETTINGS_SECTION]


def buildClient(section):
    """A TraceClient for the given usage_reporting settings; disabled when they are None.

    ``enabled`` is read through the client's ``allows_reporting``, which fails closed: only
    ``true`` (or "true", "on", "yes", "1") keeps reporting on, so ``"false"``, ``"off"``,
    ``null`` or a typo turn it off; a block with no ``enabled`` at all keeps the default (on).
    Always built through the client's constructor otherwise, which puts
    TRACE_USAGE_REPORTING / DO_NOT_TRACK ahead of ``enabled`` and records why it is off in
    ``disabled_reason``. A missing endpoint or key falls back to the shipped default. Every
    event carries a random installation ID as ``install``: TRACE_INSTALL_ID when set, else the
    one kept in installIdFile(); the client resolves both only after its opt-out checks, so a
    disabled client never creates the file.
    """
    if section is None:
        return TraceClient.disabled()
    try:
        return TraceClient(
            str(section.get("endpoint") or DEFAULT_ENDPOINT),
            APPLICATION,
            VERSION,
            key=str(section.get("key") or DEFAULT_KEY),
            enabled=allows_reporting(section.get("enabled", True)),
            install_id=os.environ.get("TRACE_INSTALL_ID"),
            install_id_file=installIdFile(),
        )
    except Exception:
        return TraceClient.disabled()


def startUsageReporting(settingsFile=SETTINGS_FILE, log=print):
    """Read the settings, build the client and report the startup event.

    Never raises; the client is closed (sending what is queued, bounded by its timeout)
    when the interpreter exits. Returns the client so further events can be reported.
    """
    try:
        client = buildClient(loadSettings(settingsFile, log))
    except Exception:
        return TraceClient.disabled()
    client.report("startup")
    atexit.register(client.close)
    return client
