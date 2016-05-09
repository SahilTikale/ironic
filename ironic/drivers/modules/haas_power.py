import requests
import time

from ironic.common.i18n import _
from ironic.common.i18n import _LE
from ironic.common.i18n import _LI
from ironic.common.i18n import _LW



from oslo_log import log as logging
from ironic.drivers import base
from ironic.common import exception
from ironic.common import states
from ironic.conductor import task_manager

LOG = logging.getLogger(__name__)


REQUIRED_PROPERTIES = {
    'haas_endpoint': _("Endpoint for HaaS. Required."),
    'haas_nodename': _("Should be same as registerd with HaaS.")
}

OPTIONAL_PROPERTIES = {
    'haas_username': _("HaaS username to access HaaS."),
    'haas_password': _("HaaS password required to access HaaS."),
    'haas_projectname': _("project in HaaS to which nodes belong.")
}

COMMON_PROPERTIES = REQUIRED_PROPERTIES.copy()
COMMON_PROPERTIES.update(OPTIONAL_PROPERTIES)

def _parse_driver_info(node):
    """Gets the parameters required for ipmitool to access the node.

    :param node: the Node of interest.
    :returns: dictionary of parameters.
    :raises: InvalidParameterValue when an invalid value is specified
    :raises: MissingParameterValue when a required ipmi parameter is missing.

    """
    info = node.driver_info or {}
    missing_info = [ key for key in REQUIRED_PROPERTIES if not info.get(key) ]
    if missing_info:
        raise exception.MissingParameterValue(_( 
            "Missing the following haas_power credentials in node's"
            " drivers_info: %s.") % missing_info)

    haas_endpoint = info.get('haas_endpoint')
    haas_username = info.get('haas_username')
    haas_password = info.get('haas_password')
    haas_nodename = info.get('haas_nodename')

    return {
            'haas_endpoint': haas_endpoint, 
            'haas_username': haas_username,
            'haas_password': haas_password,
            'haas_nodename': haas_nodename
            }




class haasPower(base.PowerInterface):


    def get_properties(self):
        return COMMON_PROPERTIES

    def validate(self, task):
        """Validate driver_info for the haas_power driver.

        Check that the node['driver_info'] contains node name 
        as registered with HaaS and HaaS credentials

        :param task: a TaskManager instance containing the node to act on.
        :raises: InvalidParameterValue if required haas_power parameters are missing.
        :raises: MissingParameterValue if a required parameter is missing.

        """

        _parse_driver_info(task.node)

    def get_power_state(self, task):
        """Get the current power state of the task's node.

        :param task: a TaskManager instance containing the node to act on.
        :returns: one of ironic.common.states POWER_OFF, POWER_ON or ERROR.
        :raises: InvalidParameterValue if required ipmi parameters are missing.
        :raises: MissingParameterValue if a required parameter is missing.
        :raises: IPMIFailure on an error from ipmitool (from _power_status
            call).

        """
        driver_info = _parse_driver_info(task.node)
        return task.node.power_state   #This is temporary. HaaS needs to provide this info.

    @task_manager.require_exclusive_lock
    def set_power_state(self, task, pstate):
        """Turn the power on or off.

        :param task: a TaskManager instance containing the node to act on.
        :param pstate: The desired power state, one of ironic.common.states
            POWER_ON, POWER_OFF.
        :raises: InvalidParameterValue if an invalid power state was specified.
       :raises: MissingParameterValue if required ipmi parameters are missing
        :raises: PowerStateFailure if the power couldn't be set to pstate.

        """
#        import pdb; pdb.set_trace()
        driver_info = _parse_driver_info(task.node)
        endpoint = driver_info['haas_endpoint']
        nodename = driver_info['haas_nodename']
        url = endpoint+"/node/"+nodename

        if pstate == states.POWER_ON:
            url_on = url+"/power_cycle"
            ret = requests.post(url_on)
            if ret.status_code == 200:
                state = "power on"
            else:
                state = "HaaS failed to start this node"
        elif pstate == states.POWER_OFF:
            url_off = url+"/power_off"
            ret = requests.post(url_off)
            if ret.status_code == 200:
                state = "power off" 
            else:
                state = "HaaS failed to shut down this node"
        else:
            raise exception.InvalidParameterValue(
                _("set_power_state called "
                  "with invalid power state %s.") % pstate)

        if state != pstate:
            raise exception.PowerStateFailure(pstate=pstate)

    @task_manager.require_exclusive_lock
    def reboot(self, task):
        """Cycles the power to the task's node.

        :param task: a TaskManager instance containing the node to act on.
        :raises: MissingParameterValue if required ipmi parameters are missing.
        :raises: InvalidParameterValue if an invalid power state was specified.
        :raises: PowerStateFailure if the final state of the node is not
            POWER_ON.

        """
        driver_info = _parse_driver_info(task.node)
        endpoint = driver_info['haas_endpoint']
        nodename = driver_info['haas_nodename']
        url = endpoint+"/node/"+nodename
        
        url_off = url+"/power_off"
        ret_off = requests.post(url_off)
        if ret_off.status_code == 200:
            url_on = url+"/power_cycle"
            ret_on = requests.post(url_on)
            if ret_on.status_code == 200:
                state = "power on"

        if state != states.POWER_ON:
            raise exception.PowerStateFailure(pstate=states.POWER_ON)


