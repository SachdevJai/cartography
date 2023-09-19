# Okta intel module - Applications
import asyncio
import json
import logging
from typing import Dict
from typing import List
from typing import Any

import neo4j

from cartography.client.core.tx import load
from cartography.graph.job import GraphJob
from okta.client import Client as OktaClient
from okta.models.application import Application as OktaApplication
from cartography.models.okta.application import OktaApplicationSchema
from cartography.util import timeit


logger = logging.getLogger(__name__)

####
# Get Applications
####
@timeit
def sync_okta_applications(
    okta_client: OktaClient,
    neo4j_session: neo4j.Session,
    common_job_parameters: Dict[str, Any],
) -> None:
    """
    Sync Okta applications
    :param okta_client: An Okta client object
    :param neo4j_session: Session with Neo4j server
    :param common_job_parameters: Settings used by all Okta modules
    :return: Nothing
    """

    logger.info("Syncing Okta applications")
    applications = asyncio.run(_get_okta_applications(okta_client))
    transformed_applications = _transform_okta_applications(okta_client, applications)
    _load_okta_applications(
        neo4j_session, transformed_applications, common_job_parameters
    )
    _cleanup_okta_applications(neo4j_session, common_job_parameters)

@timeit
async def _get_okta_applications(okta_client: OktaClient) -> List[OktaApplication]:
    """
    Get Okta applications list from Okta
    :param okta_client: An Okta client object
    :return: List of Okta applications
    """
    output_applications = []
    query_parameters = {"limit": 200}
    applications, resp, _ = await okta_client.list_applications(query_parameters)
    output_applications += applications
    while resp.has_next():
        applications, _ = await resp.next()
        output_applications += applications
        logger.info(f"Fetched {len(applications)} applications")
    return output_applications


@timeit
def _transform_okta_applications(
    okta_client: OktaClient,
    okta_applications: List[OktaApplication],
) -> List[Dict[str, Any]]:
    """
    :param okta_client: An Okta client object
    Convert a list of Okta applications into a format for Neo4j
    :param okta_applications: List of Okta applications
    :return: List of application dicts
    """
    transformed_applications: List[OktaApplication] = []
    logger.info(f"Transforming {len(okta_applications)} Okta applications")
    for okta_application in okta_applications:
        application_props = {}
        application_props["id"] = okta_application.id
        application_props[
            "accessibility_error_redirect_url"
        ] = okta_application.accessibility.error_redirect_url
        application_props[
            "accessibility_login_redirect_url"
        ] = okta_application.accessibility.login_redirect_url
        application_props[
            "accessibility_self_service"
        ] = okta_application.accessibility.self_service

        application_props["created"] = okta_application.created
        application_props[
            "credentials_signing_kid"
        ] = okta_application.credentials.signing.kid
        application_props[
            "credentials_signing_last_rotated"
        ] = okta_application.credentials.signing.last_rotated
        application_props[
            "credentials_signing_next_rotation"
        ] = okta_application.credentials.signing.next_rotation
        application_props[
            "credentials_signing_rotation_mode"
        ] = okta_application.credentials.signing.rotation_mode
        application_props[
            "credentials_signing_use"
        ] = okta_application.credentials.signing.use
        application_props[
            "credentials_user_name_template_push_status"
        ] = okta_application.credentials.user_name_template.push_status
        application_props[
            "credentials_user_name_template_suffix"
        ] = okta_application.credentials.user_name_template.suffix
        application_props[
            "credentials_user_name_template_template"
        ] = okta_application.credentials.user_name_template.template
        application_props[
            "credentials_user_name_template_type"
        ] = okta_application.credentials.user_name_template.type
        application_props["features"] = okta_application.features
        application_props["label"] = okta_application.label
        application_props["last_updated"] = okta_application.last_updated
        # This is not always defined
        # TODO: see if there are other definitions
        if hasattr(okta_application.licensing, "seat_count"):
            application_props[
                "licensing_seat_count"
            ] = okta_application.licensing.seat_count
        else:
            application_props["licensing_seat_count"] = None
        application_props["name"] = okta_application.name
        application_props[
            "settings_app_acs_url"
        ] = okta_application.settings.app.acs_url
        application_props[
            "settings_app_button_field"
        ] = okta_application.settings.app.button_field
        application_props[
            "settings_app_login_url_regex"
        ] = okta_application.settings.app.login_url_regex
        application_props[
            "settings_app_org_name"
        ] = okta_application.settings.app.org_name
        application_props[
            "settings_app_password_field"
        ] = okta_application.settings.app.password_field
        application_props["settings_app_url"] = okta_application.settings.app.url
        application_props[
            "settings_app_username_field"
        ] = okta_application.settings.app.username_field
        application_props[
            "settings_app_implicit_assignment"
        ] = okta_application.settings.implicit_assignment
        application_props[
            "settings_app_inline_hook_id"
        ] = okta_application.settings.inline_hook_id
        application_props[
            "settings_notifications_vpn_help_url"
        ] = okta_application.settings.notifications.vpn.help_url
        application_props[
            "settings_notifications_vpn_message"
        ] = okta_application.settings.notifications.vpn.message
        application_props[
            "settings_notifications_vpn_network_connection"
        ] = okta_application.settings.notifications.vpn.network.connection
        application_props["settings_notifications_vpn_network_exclude"] = json.dumps(
            okta_application.settings.notifications.vpn.network.exclude
        )
        application_props["settings_notifications_vpn_network_include"] = json.dumps(
            okta_application.settings.notifications.vpn.network.include
        )
        if hasattr(okta_application.settings.notes, "admin"):
            application_props[
                "settings_notes_admin"
            ] = okta_application.settings.notes.admin
        if hasattr(okta_application.settings.notes, "enduser"):
            application_props[
                "settings_notes_enduser"
            ] = okta_application.settings.notes.enduser
        # TODO: saml_sign_on
        if hasattr(okta_application.settings, "sign_on"):
            pass
        # oauth_client, sometimes this doesn't exist, sometimes its None
        if (
            hasattr(okta_application.settings, "oauth_client")
            and okta_application.settings.oauth_client
        ):
            application_props[
                "settings_oauth_client_application_type"
            ] = okta_application.settings.oauth_client.application_type.value

            application_props[
                "settings_oauth_client_client_uri"
            ] = okta_application.settings.oauth_client.client_uri
            application_props[
                "settings_oauth_client_consent_method"
            ] = okta_application.settings.oauth_client.consent_method.value
            application_props["settings_oauth_client_grant_Type"] = [
                grant_type.value
                for grant_type in okta_application.settings.oauth_client.grant_types
            ]
            application_props[
                "settings_oauth_client_idp_initiated_login_default_scope"
            ] = json.dumps(
                okta_application.settings.oauth_client.idp_initiated_login.default_scope
            )
            application_props[
                "settings_oauth_client_idp_initiated_login_mode"
            ] = okta_application.settings.oauth_client.idp_initiated_login.mode
            application_props[
                "settings_oauth_client_initiate_login_uri"
            ] = okta_application.settings.oauth_client.initiate_login_uri
            # TODO: This has custom okta models that are part of this
            # application_props[
            #    "settings_oauth_client_jwks"
            # ] = okta_application.settings.oauth_client.jwks
            application_props[
                "settings_oauth_client_logo_uri"
            ] = okta_application.settings.oauth_client.logo_uri
            application_props[
                "settings_oauth_client_policy_uri"
            ] = okta_application.settings.oauth_client.policy_uri
            application_props[
                "settings_oauth_client_post_logout_redirect_uris"
            ] = json.dumps(
                okta_application.settings.oauth_client.post_logout_redirect_uris
            )
            application_props["settings_oauth_client_redirect_uris"] = json.dumps(
                okta_application.settings.oauth_client.redirect_uris
            )
            # TODO: This has custom okta models that are part of this
            # application_props[
            #    "settings_oauth_client_refresh_token"
            # ] = okta_application.settings.oauth_client.refresh_token
            application_props["settings_oauth_client_response_types"] = [
                response_type.value
                for response_type in okta_application.settings.oauth_client.response_types
            ]
            application_props[
                "settings_oauth_client_tos_uri"
            ] = okta_application.settings.oauth_client.tos_uri
            application_props[
                "settings_oauth_client_wildcard_redirect"
            ] = okta_application.settings.oauth_client.wildcard_redirect
        # This value can also be None, in which case it has no value
        if okta_application.sign_on_mode:
            application_props["sign_on_mode"] = okta_application.sign_on_mode.value
        else:
            application_props["sign_on_mode"] = okta_application.sign_on_mode
        application_props["status"] = okta_application.status
        # This returns a dict of somewhat poorly defined value
        # best to treat it as a json blob
        application_props["visibility_app_links"] = json.dumps(
            okta_application.visibility.app_links
        )
        application_props[
            "visibility_auto_launch"
        ] = okta_application.visibility.auto_launch
        application_props[
            "visibility_auto_submit_toolbar"
        ] = okta_application.visibility.auto_submit_toolbar
        # This is an `ApplicationVisibilityHide` model but its
        # really a dict but we'll present it as JSON
        application_props["visibility_hide"] = json.dumps(
            okta_application.visibility.hide.as_dict()
        )
        transformed_applications.append(application_props)
        # Add user assignments
        app_users = asyncio.run(
            _get_application_assigned_users(okta_client, okta_application.id)
        )
        for app_user in app_users:
            match_app = {**application_props, "user_id": app_user}
            transformed_applications.append(match_app)
        # Add group assignments
        app_groups = asyncio.run(
            _get_application_assigned_groups(okta_client, okta_application.id)
        )
        for app_group in app_groups:
            match_app = {**application_props, "group_id": app_group}
            transformed_applications.append(match_app)

    return transformed_applications


@timeit
def _load_okta_applications(
    neo4j_session: neo4j.Session,
    application_list: List[Dict],
    common_job_parameters: Dict[str, Any],
) -> None:
    """
    Load Okta application information into the graph
    :param neo4j_session: session with neo4j server
    :param application_list: list of application
    :param common_job_parameters: Settings used by all Okta modules
    :return: Nothing
    """

    logger.info(f"Loading {len(application_list)} Okta Application")

    load(
        neo4j_session,
        OktaApplicationSchema(),
        application_list,
        OKTA_ORG_ID=common_job_parameters["OKTA_ORG_ID"],
        lastupdated=common_job_parameters["UPDATE_TAG"],
    )


@timeit
def _cleanup_okta_applications(
    neo4j_session: neo4j.Session, common_job_parameters: Dict[str, Any]
) -> None:
    """
    Cleanup application nodes and relationships
    :param neo4j_session: session with neo4j server
    :param common_job_parameters: Settings used by all Okta modules
    :return: Nothing
    """
    GraphJob.from_node_schema(OktaApplicationSchema(), common_job_parameters).run(
        neo4j_session
    )


####
# Get Applications assigned to users
####


@timeit
async def _get_application_assigned_users(
    okta_client: OktaClient, app_id: str
) -> List[str]:
    """
    Get Okta application users list from Okta
    :param okta_client: An Okta client object
    :return: List of Okta application users
    """
    output_application_users = []
    query_parameters = {"limit": 500}
    application_users, resp, _ = await okta_client.list_application_users(
        app_id, query_parameters
    )
    output_application_users += application_users
    while resp.has_next():
        application_users, _ = await resp.next()
        output_application_users += application_users
        logger.info(f"Fetched {len(application_users)} application users")
    output_application_users_ids = [user.id for user in output_application_users]
    return output_application_users_ids


####
# Get Applications assigned to groups
####
@timeit
async def _get_application_assigned_groups(
    okta_client: OktaClient, app_id: str
) -> List[str]:
    """
    Get application data from Okta server
    :param app_client: api client
    :return: application data
    """
    output_application_groups = []
    query_parameters = {"limit": 200}
    application_groups, resp, _ = await okta_client.list_application_group_assignments(
        app_id, query_parameters
    )
    output_application_groups += application_groups
    while resp.has_next():
        application_groups, _ = await resp.next()
        output_application_groups += application_groups
        logger.info(f"Fetched {len(application_groups)} application users")
    output_application_group_ids = [group.id for group in output_application_groups]
    return output_application_group_ids
