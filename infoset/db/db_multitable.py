"""Module of infoset database functions.

Handles queries that span multiple tables.

"""

# Python standard libraries
import copy
from collections import defaultdict

# PIP libraries
from sqlalchemy import and_

# Infoset libraries
from infoset.utils import general
from infoset.db import db
from infoset.db.db_orm import Datapoint, Device, Agent, DeviceAgent, AgentName


def datapoint_summary_list():
    """Get summary datapoint information as a list of dicts.

    Args:
        None

    Returns:
        return_value: List of dicts. Each dict keyed by table column name

    """
    # Return
    return_value = _datapoint_summary(aslist=True)
    return return_value


def datapoint_summary():
    """Get summary datapoint information as a dict.

    Args:
        None

    Returns:
        return_value: Dict keyed by idx_datapoint.
            Subkeys are by table column name

    """
    # Return
    return_value = _datapoint_summary(aslist=False)
    return return_value


def _datapoint_summary(aslist=False):
    """Get summary datapoint information.

    Args:
        None

    Returns:
        return_value: Dict keyed by idx_datapoint OR list of dicts

    """
    # Initialize key variables
    data = defaultdict(lambda: defaultdict(dict))
    data_list = []
    return_value = None

    # Establish a database session
    database = db.Database()
    session = database.session()

    # Get result of query
    rows = session.query(
        Datapoint.idx_datapoint,
        Datapoint.agent_label,
        Datapoint.agent_source,
        DeviceAgent.idx_deviceagent,
        AgentName.name,
        Agent.id_agent,
        Device.devicename).filter(
            and_(
                Datapoint.idx_deviceagent == DeviceAgent.idx_deviceagent,
                Agent.idx_agent == DeviceAgent.idx_agent,
                Agent.idx_agentname == AgentName.idx_agentname,
                Device.idx_device == DeviceAgent.idx_device)
            )

    # Process query results
    for row in rows:
        idx_datapoint = row.idx_datapoint
        data_dict = {}
        data_dict['agent'] = general.decode(row.name)
        data_dict['agent_label'] = general.decode(row.agent_label)
        data_dict['agent_source'] = general.decode(row.agent_source)
        data_dict['id_agent'] = general.decode(row.id_agent)
        data_dict['devicename'] = general.decode(row.devicename)
        data_dict['idx_deviceagent'] = row.idx_deviceagent

        # Assign values to data structures dependent on 'aslist' value
        if aslist is True:
            data_dict['idx_datapoint'] = idx_datapoint
            data_list.append(data_dict)
        else:
            data[idx_datapoint] = data_dict

    # Return the session to the database pool after processing
    database.close()

    # Assign values to data structures dependent on 'aslist' value
    if aslist is True:
        return_value = copy.deepcopy(data_list)
    else:
        return_value = copy.deepcopy(data)

    # Return
    return return_value
