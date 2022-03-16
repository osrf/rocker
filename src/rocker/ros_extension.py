# Copyright 2019 Open Source Robotics Foundation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentTypeError
import getpass
import os
from rocker.extensions import RockerExtension



# From Section 9.6.2 of DDSI-RTPS Spec
# https://www.omg.org/spec/DDSI-RTPS/2.5/PDF

# TODO answer here too: https://answers.ros.org/question/347630/ros2-port-forwarding/


PB = 7400
DG = 250
PG = 2
d0 = 0
d1 = 10
d2 = 1
d3 = 11

def get_multicast_dds_ports(ros_domain_id):

    discovery_multicast_port = PB + DG * ros_domain_id + d0
    user_multicast_port = PB + DG * ros_domain_id + d2

    return [discovery_multicast_port, user_multicast_port]

def get_unicast_dds_ports(ros_domain_id, number_of_participants):

    ports = []

    for participant_id in range(number_of_participants):
        discovery_unicast_port = PB + DG * ros_domain_id + d3 + PG * participant_id
        user_unicast_port = PB + DG * ros_domain_id + d3 + PG * participant_id
        ports.append(discovery_unicast_port)
        ports.append(user_unicast_port)

    return ports



class RosPorts(RockerExtension):

    name = 'ros_ports'

    @classmethod
    def get_name(cls):
        return cls.name


    def get_docker_args(self, cli_args):
        args = ''
        # only parameterized for testing
        ros_domain_id_str = cli_args.get('ros_domain_id')
        if not ros_domain_id_str:
            ros_domain_id_str = os.environ.get('ROS_DOMAIN_ID', '0')
        ros_domain_id = int(ros_domain_id_str)

        # if cli_args.get('ros_ports_type') == 'multicast':   
        (discovery_multicast_port, user_multicast_port) = get_multicast_dds_ports(ros_domain_id)

        args += ' -p {discovery_multicast_port} -p {user_multicast_port}'.format(**locals())
        args += ' -e ROS_DOMAIN_ID={ros_domain_id_str}'.format(**locals())
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('--ros-ports',
            action='store_true',
            default=defaults.get(RosPorts.get_name(), None),
            help="Expose ROS ports for DDS from container")
        parser.add_argument('--ros-domain-id',
            action='store',
            default=defaults.get('ros_domain_id', None),
            help="Override the ROS_DOMAIN_ID from the automatically detected one in the environment for mapping ROS Ports")
        parser.add_argument('--ros-ports-type',
            action='store',
            choices=['multicast', 'unicast'],
            default=defaults.get('ros_ports_type', 'multicast'),
            help="Override the ROS_DOMAIN_ID from the automatically detected one in the environment for mapping ROS Ports")
