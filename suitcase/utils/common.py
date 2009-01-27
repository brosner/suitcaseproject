"""Suitcase General utils"""

import os
import sys
import commands

from suitcase.exceptions import SuitcaseImportError, SuitcaseCommandError
from suitcase.utils.fakeroot import Fakeroot
from suitcase.utils.terminal import TerminalController

def get_user_input(prompt, answers, default=None):
    """Wrapper to prompting for user input with optional default

    answers should be a list of acceptable answers
    """

    if default and default not in answers:
        raise ValueError("default should be a value in the answers list!")

    prompt = '%s (%s): ' % (prompt, ", ".join(answers), )
    if default:
        prompt = "%s [%s]: " % (prompt[:-2], default)

    answer = None
    while answer not in answers:
        try:
            answer = raw_input(prompt)
        except KeyboardInterrupt:
            print
            sys.exit(100)

        # user hit enter to accept default
        answer = (answer == '') and default or answer

    return answer


def dynamic_import(module_string):
    """Runs a dynamic module import based on the string passed in

    """
    try:
        package = __import__(module_string)
        if package.__name__ != module_string:
            package = sys.modules[module_string]
        return package
    except ImportError, error:
        raise SuitcaseImportError(
            "Required module '%s' cannot be imported!:\n%s" % ( 
                module_string, 
                error
            )
        )


def run_command(command):
    """Wraps running a command and raises an error if the cmd can't be found

    Bash returns exit code of 127 if a command isn't found and > 0  if the
    command has an error

    """
    result = commands.getstatusoutput(command)
    if result[0] == 127:
        command = command.split()[0]
        raise SuitcaseCommandError(result, "%s not found" % command)
    if result[0] > 0:
        raise SuitcaseCommandError(result, "An error occurred: %s" % result[1])

    return result


def get_dynamic_class_instance(class_string, class_name,  *args, **kwargs):
    """Imports the class and returns an instance"""

    try:
        dynamic_class = dynamic_import(class_string)
        return getattr(dynamic_class, class_name)(*args, **kwargs)
    except AttributeError:
        raise SuitcaseImportError("Cannot find class. Expected class name "\
            "in the '%s' module is '%s'" % (class_string, class_name))


def relative_import(path, module_namespace):
    """Imports arbitrary paths as module_namespace
    
    In essence what this is actually doing is aliasing an namespace. It imports
    the specific path and then adds that to sys.modules.

    """

    if "." in module_namespace:
        raise SuitcaseImportError("Cannot import a directory into a multi "\
            "part namespace - sorry")

    cur_dir = os.getcwd()
    os.chdir(os.path.join(path, "../"))
    sys.path.insert(0, os.getcwd())
    sys.modules[module_namespace] = __import__(os.path.split(path)[1])
    del sys.path[0]
    os.chdir(cur_dir)
    return sys.modules[module_namespace]
    


def remove_leading_slash(string):
    """remove leading slash"""

    string = string.strip()

    if string.startswith("/"):
        return string[1:]
    else:
        return string

def add_trailing_slash(path):

    """Adds a slash to path"""

    return (not path.endswith('/')) and "%s/" % path or path

def run_fakeroot(args):
    """run fakeroot"""
    cache_filename = Fakeroot().cache_filename
    fakeroot_command = ("fakeroot -i %s -s %s %s" % (
        cache_filename,
        cache_filename,
        args
    ))
    run_command(fakeroot_command)

def clean_fakeroot():
    """Clean up fakeroot cache"""
    filename = Fakeroot().cache_filename
    if os.path.exists(filename):
        run_command("rm %s" % filename)
    del Fakeroot().cache_filename
    
def merge(*args):
    """Merges lists"""
    
    output = []
    args = list(args)
    for arg in args:
        if not type(arg) == type([]):
            arg = [arg]
        output += arg
    return output


def merge_and_de_dupe(*args):
    """merges and de_dupes"""    
    result = []
    for item in merge(*args):
        if item not in result:
            result.append(item)

    return result


def display_warning(warning):    
    """Shows a warning in fancy colours if supported"""
    term = TerminalController()
    try:
        print term.render('${YELLOW}%s${NORMAL}' % warning)
    except ValueError:
        print warning