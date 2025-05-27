from dataclasses import dataclass

from cartography.models.core.common import PropertyRef
from cartography.models.core.nodes import CartographyNodeProperties
from cartography.models.core.nodes import CartographyNodeSchema
from cartography.models.core.relationships import CartographyRelProperties
from cartography.models.core.relationships import CartographyRelSchema
from cartography.models.core.relationships import LinkDirection
from cartography.models.core.relationships import make_target_node_matcher
from cartography.models.core.relationships import OtherRelationships
from cartography.models.core.relationships import TargetNodeMatcher


@dataclass(frozen=True)
class PagerDutyTeamProperties(CartographyNodeProperties):
    id: PropertyRef = PropertyRef("id")
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)


@dataclass(frozen=True)
class PagerDutyTeamToUserProperties(CartographyRelProperties):
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)


@dataclass(frozen=True)
# (:PagerDutyUser)-[:MEMBER_OF]->(:PagerDutyTeam)
class PagerDutyTeamToUserRel(CartographyRelSchema):
    target_node_label: str = "PagerDutyUser"
    target_node_matcher: TargetNodeMatcher = make_target_node_matcher(
        # WIP: Add the tranform functiion to the intel script
        {"id": PropertyRef("members", one_to_many=True)},
    )
    direction: LinkDirection = LinkDirection.INWARD
    rel_label: str = "MEMBER_OF"
    properties: PagerDutyTeamToUserProperties = (
        PagerDutyTeamToUserProperties()
    )


@dataclass(frozen=True)
class PagerDutyTeamToOrganizationRelProperties(CartographyRelProperties):
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)


@dataclass(frozen=True)
# (:PagerDutyOrganization)-[:RESOURCE]->(:PagerDutyTeam)
class PagerDutyTeamToOrganizationRel(CartographyRelSchema):
    target_node_label: str = "PagerDutyOrganization"
    target_node_matcher: TargetNodeMatcher = make_target_node_matcher(
        {"id": PropertyRef("ORG_ID", set_in_kwargs=True)},
    )
    direction: LinkDirection = LinkDirection.INWARD
    rel_label: str = "RESOURCE"
    properties: PagerDutyTeamToOrganizationRelProperties = (
        PagerDutyTeamToOrganizationRelProperties()
    )


@dataclass(frozen=True)
class PagerDutyTeamSchema(CartographyNodeSchema):
    label: str = "PagerDutyTeam"
    properties: PagerDutyTeamProperties = (
        PagerDutyTeamProperties()
    )
    sub_resource_relationship: PagerDutyTeamToOrganizationRel = (
        PagerDutyTeamToOrganizationRel()
    )
    other_relationsips: OtherRelationships = OtherRelationships(
        [
            PagerDutyTeamToUserRel(),
        ]
    )



ingestion_cypher_query = """
    UNWIND $Teams AS team
        MERGE (t:PagerDutyTeam{id: team.id})
        ON CREATE SET t.html_url = team.html_url,
            t.firstseen = timestamp()
        SET t.type = team.type,
            t.summary = team.summary,
            t.name = team.name,
            t.description = team.description,
            t.default_role = team.default_role,
            t.lastupdated = $update_tag
    """

    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (t:PagerDutyTeam{id: relation.team}), (u:PagerDutyUser{id: relation.user})
        MERGE (u)-[r:MEMBER_OF]->(t)
        ON CREATE SET r.firstseen = timestamp()
        SET r.role = relation.role
    """