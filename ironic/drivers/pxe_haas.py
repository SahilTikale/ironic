# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
PXE Driver and supporting meta-classes.
"""

from oslo_utils import importutils

from ironic.common import exception
from ironic.common.i18n import _
from ironic.drivers import base
from ironic.drivers.modules import agent
from ironic.drivers.modules.amt import management as amt_management
from ironic.drivers.modules.amt import power as amt_power
from ironic.drivers.modules.amt import vendor as amt_vendor
from ironic.drivers.modules.cimc import management as cimc_mgmt
from ironic.drivers.modules.cimc import power as cimc_power
from ironic.drivers.modules import iboot
from ironic.drivers.modules.ilo import console as ilo_console
from ironic.drivers.modules.ilo import deploy as ilo_deploy
from ironic.drivers.modules.ilo import inspect as ilo_inspect
from ironic.drivers.modules.ilo import management as ilo_management
from ironic.drivers.modules.ilo import power as ilo_power
from ironic.drivers.modules.ilo import vendor as ilo_vendor
from ironic.drivers.modules import inspector
from ironic.drivers.modules import ipminative
from ironic.drivers.modules import ipmitool
from ironic.drivers.modules.irmc import inspect as irmc_inspect
from ironic.drivers.modules.irmc import management as irmc_management
from ironic.drivers.modules.irmc import power as irmc_power
from ironic.drivers.modules import iscsi_deploy
from ironic.drivers.modules.msftocs import management as msftocs_management
from ironic.drivers.modules.msftocs import power as msftocs_power
from ironic.drivers.modules import pxe
from ironic.drivers.modules import seamicro
from ironic.drivers.modules import snmp
from ironic.drivers.modules import ssh
from ironic.drivers.modules.ucs import management as ucs_mgmt
from ironic.drivers.modules.ucs import power as ucs_power
from ironic.drivers.modules import virtualbox
from ironic.drivers.modules import wol
from ironic.drivers.modules import haas_power
from ironic.drivers import utils


class PXEAndHaaSDriver(base.BaseDriver):
    """PXE + IPMITool driver.

    This driver implements the `core` functionality, combining
    :class:`ironic.drivers.modules.ipmi.IPMI` for power on/off
    and reboot with
    :class:`ironic.drivers.modules.iscsi_deploy.ISCSIDeploy` for
    image deployment. Implementations are in those respective
    classes; this class is merely the glue between them.
    """
    def __init__(self):
#        self.power = haas.IPMIPower()
        self.power = haas_power.haasPower()
        self.deploy = iscsi_deploy.ISCSIDeploy()
#        self.management = ipmitool.IPMIManagement()
        self.inspect = inspector.Inspector.create_if_enabled(
            'PXEAndHaaSDriver')
        self.iscsi_vendor = iscsi_deploy.VendorPassthru()
        self.ipmi_vendor = ipmitool.VendorPassthru()
