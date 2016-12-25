#!/usr/bin/env python3
"""Infoset general library."""

import os
import time
import subprocess
import locale
import hashlib
import random
import string

# PIP libraries
import yaml

# Infoset libraries
from infoset.utils import log
from infoset.utils import configuration
from infoset import infoset


def root_directory():
    """Getermine the root directory in which infoset is installed.

    Args:
        None

    Returns:
        root_dir: Root directory

    """
    # Get the directory of the infoset library
    infoset_dir = infoset.__path__[0]
    components = infoset_dir.split(os.sep)

    # Determint the directory two levels above
    root_dir = os.sep.join(components[0:-2])

    # Return
    return root_dir


def encode(value):
    """Encode string value to utf-8.

    Args:
        value: String to encode

    Returns:
        result: encoded value

    """
    # Initialize key variables
    result = value

    # Start decode
    if value is not None:
        if isinstance(value, str) is True:
            result = value.encode()

    # Return
    return result


def decode(value):
    """Decode utf-8 value to string.

    Args:
        value: String to decode

    Returns:
        result: decoded value

    """
    # Initialize key variables
    result = value

    # Start decode
    if value is not None:
        if isinstance(value, bytes) is True:
            result = value.decode('utf-8')

    # Return
    return result


def hashstring(stringy, sha=256, utf8=False):
    """Create a UTF encoded SHA hash string.

    Args:
        stringy: String to hash
        length: Length of SHA hash
        utf8: Return utf8 encoded string if true

    Returns:
        result: Result of hash

    """
    # Initialize key variables
    listing = [1, 224, 384, 256, 512]

    # Select SHA type
    if sha in listing:
        index = listing.index(sha)
        if listing[index] == 1:
            hasher = hashlib.sha1()
        elif listing[index] == 224:
            hasher = hashlib.sha224()
        elif listing[index] == 384:
            hasher = hashlib.sha384()
        elif listing[index] == 512:
            hasher = hashlib.sha512()
        else:
            hasher = hashlib.sha256()

    # Encode the string
    hasher.update(bytes(stringy.encode()))
    device_hash = hasher.hexdigest()
    if utf8 is True:
        result = device_hash.encode()
    else:
        result = device_hash

    # Return
    return result


def validate_timestamp(timestamp):
    """Validate timestamp to be a multiple of 'interval' seconds.

    Args:
        timestamp: epoch timestamp in seconds

    Returns:
        valid: True if valid

    """
    # Initialize key variables
    valid = False
    interval = configuration.Config().interval()

    # Process data
    test = (int(timestamp) // interval) * interval
    if test == timestamp:
        valid = True

    # Return
    return valid


def normalized_timestamp(timestamp=None):
    """Normalize timestamp to a multiple of 'interval' seconds.

    Args:
        timestamp: epoch timestamp in seconds

    Returns:
        value: Normalized value

    """
    # Initialize key variables
    interval = configuration.Config().interval()

    # Process data
    if timestamp is None:
        value = (int(time.time()) // interval) * interval
    else:
        value = (int(timestamp) // interval) * interval
    # Return
    return value


def read_yaml_files(directories):
    """Read the contents of all yaml files in a directory.

    Args:
        directories: List of directory names with configuration files

    Returns:
        config_dict: Dict of yaml read

    """
    # Initialize key variables
    yaml_found = False
    yaml_from_file = ''
    all_yaml_read = ''

    # Check each directory in sequence
    for config_directory in directories:
        # Check if config_directory exists
        if os.path.isdir(config_directory) is False:
            log_message = (
                'Configuration directory "%s" '
                'doesn\'t exist!' % config_directory)
            log.log2die(1009, log_message)

        # Cycle through list of files in directory
        for filename in os.listdir(config_directory):
            # Examine all the '.yaml' files in directory
            if filename.endswith('.yaml'):
                # YAML files found
                yaml_found = True

                # Read file and add to string
                file_path = ('%s/%s') % (config_directory, filename)
                try:
                    with open(file_path, 'r') as file_handle:
                        yaml_from_file = file_handle.read()
                except:
                    log_message = (
                        'Error reading file %s. Check permissions, '
                        'existence and file syntax.'
                        '') % (file_path)
                    log.log2die(1065, log_message)

                # Append yaml from file to all yaml previously read
                all_yaml_read = ('%s\n%s') % (all_yaml_read, yaml_from_file)

        # Verify YAML files found in directory
        if yaml_found is False:
            log_message = (
                'No files found in directory "%s" with ".yaml" '
                'extension.') % (config_directory)
            log.log2die(1010, log_message)

    # Return
    config_dict = yaml.load(all_yaml_read)
    return config_dict


def all_same(items):
    """Determine if all items of a list are the same item.

    Args:
        items: List to verify

    Returns:
        result: Result

    """
    # Do test and return
    result = all(item == items[0] for item in items)
    return result


def search_file(filename):
    """Run the cli_string UNIX CLI command and record output.

    Args:
        filename: File to find

    Returns:
        result: Result

    """
    # Initialize key variables
    result = None
    search_path = os.environ['PATH']

    paths = search_path.split(os.pathsep)
    for path in paths:
        if os.path.exists(os.path.join(path, filename)) is True:
            result = os.path.abspath(os.path.join(path, filename))
            break

    # Return
    return result


def randomstring(size=20):
    """Create a random string.

    Args:
        None

    Returns:
        result

    """
    # Return
    result = ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(size))
    return result


def run_script(cli_string, shell=False, die=True):
    """Run the cli_string UNIX CLI command and record output.

    Args:
        cli_string: Command to run on the CLI
        die: Die if command runs with an error

    Returns:
        None

    """
    # Initialize key variables
    encoding = locale.getdefaultlocale()[1]
    header_returncode = ('[Return Code]')
    header_stdout = ('[Output]')
    header_stderr = ('[Error Message]')
    header_bad_cmd = ('[ERROR: Bad Command]')
    log_message = ''

    # Create the subprocess object
    if shell is False:
        do_command_list = list(cli_string.split(' '))
        process = subprocess.Popen(
            do_command_list,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(
            cli_string,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    stdoutdata, stderrdata = process.communicate()
    returncode = process.returncode

    # Crash if the return code is not 0
    if die is True:
        if returncode != 0:
            # Print the Return Code header, Return Code, STDOUT header
            string2print = ('%s %s %s %s') % (
                header_bad_cmd, cli_string,
                header_returncode, returncode)
            log_message = ('%s%s') % (log_message, string2print)

            # Print the STDERR
            string2print = ('%s') % (header_stderr)
            log_message = ('%s %s') % (log_message, string2print)
            for line in stderrdata.decode(encoding).split('\n'):
                string2print = ('%s') % (line)
                log_message = ('%s %s') % (log_message, string2print)

            # Print the STDOUT
            string2print = ('%s') % (header_stdout)
            log_message = ('%s %s') % (log_message, string2print)
            for line in stdoutdata.decode(encoding).split('\n'):
                string2print = ('%s') % (line)
                log_message = ('%s %s') % (log_message, string2print)

            # All done
            log.log2die(1074, log_message)

    # Return
    return stdoutdata


def delete_files(directory, extension='.yaml'):
    """Delete all files of a specfic extension in a directory.

    Args:
        directory: Directory name
        extension: File extension

    Returns:
        None

    """
    # Determine whether directory is valid
    if os.path.isdir(directory) is False:
        log_message = ('Directory %s does not exist') % (directory)
        log.log2die_safe(2000, log_message)

    # Get list of files
    filelist = [
        next_file for next_file in os.listdir(
            directory) if next_file.endswith(extension)]

    # Delete files
    for delete_file in filelist:
        delete_path = ('%s/%s') % (directory, delete_file)
        os.remove(delete_path)


def delete_yaml_files(directory):
    """Delete all yaml files in a directory.

    Args:
        directory: Directory name

    Returns:
        None

    """
    # Delete files
    delete_files(directory, extension='.yaml')
