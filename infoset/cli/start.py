#!/usr/bin/env python3
"""infoset CLI functions for 'start'.

Functions to start daemons

"""

# Main python libraries
import sys

# Infoset-NG imports
from infoset.utils import general
from infoset.main.agent import Agent, AgentAPI, AgentDaemon
from infoset.constants import (
    API_EXECUTABLE, API_GUNICORN_AGENT, POLLER_EXECUTABLE)


def run(args):
    """Process 'start' command.

    Args:
        args: Argparse arguments

    Returns:
        None

    """
    # Show help if no arguments provided
    if args.qualifier is None:
        general.cli_help()

    # Process 'show api' command
    if args.qualifier == 'api':
        api()
    elif args.qualifier == 'poller':
        poller()

    # Show help if there are no matches
    general.cli_help()


def api():
    """Process 'start api' commands.

    Args:
        None

    Returns:
        None

    """
    # Create agent objects
    agent_gunicorn = Agent(API_GUNICORN_AGENT)
    agent_api = AgentAPI(API_EXECUTABLE, API_GUNICORN_AGENT)

    # Start daemons (API first, Gunicorn second)
    daemon_api = AgentDaemon(agent_api)
    daemon_api.start()
    daemon_gunicorn = AgentDaemon(agent_gunicorn)
    daemon_gunicorn.start()
    # Done
    sys.exit(0)


def poller():
    """Process 'start poller' commands.

    Args:
        None

    Returns:
        None

    """
    # Create agent object
    agent_poller = Agent(POLLER_EXECUTABLE)

    # Start agent
    daemon_poller = AgentDaemon(agent_poller)
    daemon_poller.start()

    # Done
    sys.exit(0)
