from dataclasses import dataclass

from cartography.models.core.common import PropertyRef
from cartography.models.core.nodes import CartographyNodeProperties
from cartography.models.core.nodes import CartographyNodeSchema
from cartography.models.core.relationships import CartographyRelProperties
from cartography.models.core.relationships import CartographyRelSchema
from cartography.models.core.relationships import LinkDirection
from cartography.models.core.relationships import make_target_node_matcher
from cartography.models.core.relationships import TargetNodeMatcher


@dataclass(frozen=True)
class PagerDutyUserProperties(CartographyNodeProperties):
    id: PropertyRef = PropertyRef("id")
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)
    html_url: PropertyRef = PropertyRef("html_url")
    type: PropertyRef = PropertyRef("type")
    summary: PropertyRef = PropertyRef("summary")
    name: PropertyRef = PropertyRef("name", extra_index=True)
    email: PropertyRef = PropertyRef("email", extra_index=True)
    time_zone: PropertyRef = PropertyRef("time_zone")
    color: PropertyRef = PropertyRef("color")
    role: PropertyRef = PropertyRef("role")
    avatar_url: PropertyRef = PropertyRef("avatar_url")
    description: PropertyRef = PropertyRef("description")
    invitation_sent: PropertyRef = PropertyRef("invitation_sent")
    job_title: PropertyRef = PropertyRef("job_title")


@dataclass(frozen=True)
class PagerDutyUserToOrganizationRelProperties(CartographyRelProperties):
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)


@dataclass(frozen=True)
# (:PagerDutyOrganization)-[:RESOURCE]->(:PagerDutyUser)
class PagerDutyUserToOrganizationRel(CartographyRelSchema):
    target_node_label: str = "PagerDutyOrganization"
    target_node_matcher: TargetNodeMatcher = make_target_node_matcher(
        {"id": PropertyRef("ORG_ID", set_in_kwargs=True)},
    )
    direction: LinkDirection = LinkDirection.INWARD
    rel_label: str = "RESOURCE"
    properties: PagerDutyUserToOrganizationRelProperties = (
        PagerDutyUserToOrganizationRelProperties()
    )


@dataclass(frozen=True)
class PagerDutyUserSchema(CartographyNodeSchema):
    label: str = "PagerDutyUser"
    properties: PagerDutyUserProperties = (
        PagerDutyUserProperties()
    )
    sub_resource_relationship: PagerDutyUserToOrganizationRel = (
        PagerDutyUserToOrganizationRel()
    )
