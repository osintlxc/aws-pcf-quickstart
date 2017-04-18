import json
from subprocess import call

from jinja2 import Template

import settings

from settings import Settings
import om_manager


def configure_opsman_director(my_settings: Settings):
    director_config = '{"ntp_servers_string": "0.amazon.pool.ntp.org,1.amazon.pool.ntp.org,2.amazon.pool.ntp.org,3.amazon.pool.ntp.org"}'

    template_ctx = {
        "zones": my_settings.zones,
        "access_key_id": my_settings.access_key_id,
        "secret_access_key": my_settings.secret_access_key,
        "vpc_id": my_settings.vpc_id,
        "security_group": my_settings.security_group,
        "key_pair_name": my_settings.key_pair_name,
        "ssh_private_key": my_settings.ssh_private_key,
        "region": my_settings.region,
        "encrypted": "false"
    }
    with open("templates/bosh_az_config.j2.json", 'r') as f:
        az_template = Template(f.read())
    # with open("templates/gcp_network_config.j2.json", 'r') as f:
    #     network_template = Template(f.read())
    # with open("templates/gcp_iaas_config.j2.json", 'r') as f:
    #     iaas_template = Template(f.read())
    # with open("templates/gcp_network_assignment.j2.json", 'r') as f:
    #     network_assignment_template = Template(f.read())
    #
    az_config = az_template.render(template_ctx).replace("\n", "").replace("|", "\\n")
    # network_config = network_template.render(template_ctx).replace("\n", "").replace("|", "\\n")
    # network_assignment_config = network_assignment_template.render(template_ctx).replace("\n", "").replace("|", "\\n")
    # iaas_config = iaas_template.render(template_ctx)
    #
    commands = []
    # commands.append("{om_with_auth} configure-bosh --iaas-configuration '{iaas_config}'".format(
    #     om_with_auth=settings.get_om_with_auth(my_settings), iaas_config=iaas_config
    # ))
    # commands.append("{om_with_auth} configure-bosh --director-configuration '{director_config}'".format(
    #     om_with_auth=settings.get_om_with_auth(my_settings), director_config=director_config
    # ))
    commands.append("{om_with_auth} configure-bosh --az-configuration '{az_config}'".format(
        om_with_auth=settings.get_om_with_auth(my_settings), az_config=az_config
    ))
    # commands.append("{om_with_auth} configure-bosh --networks-configuration '{network_config}'".format(
    #     om_with_auth=settings.get_om_with_auth(my_settings), network_config=network_config
    # ))
    # commands.append("{om_with_auth} configure-bosh --network-assignment '{network_assignment}'".format(
    #     om_with_auth=settings.get_om_with_auth(my_settings), network_assignment=network_assignment_config
    # ))
    for cmd in commands:
        exit_code = om_manager.run_command(cmd, my_settings.debug)
        if exit_code != 0:
            return exit_code

    return 0