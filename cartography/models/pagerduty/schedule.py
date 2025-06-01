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
class PagerDutyScheduleProperties(CartographyNodeProperties):
    id: PropertyRef = PropertyRef("id")
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)
    html_url: PropertyRef = PropertyRef("html_url")
    type: PropertyRef = PropertyRef("type")
    summary: PropertyRef = PropertyRef("summary")
    name: PropertyRef = PropertyRef("name", extra_index=True)
    time_zone: PropertyRef = PropertyRef("time_zone")
    description: PropertyRef = PropertyRef("description")


@dataclass(frozen=True)
class PagerDutyScheduleToUserProperties(CartographyRelProperties):
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)


@dataclass(frozen=True)
# (:PagerDutyUser)-[:MEMBER_OF]->(:PagerDutySchedule)
class PagerDutyScheduleToUserRel(CartographyRelSchema):
    target_node_label: str = "PagerDutyUser"
    target_node_matcher: TargetNodeMatcher = make_target_node_matcher(
        # WIP: Migrate to a one to many transform function
        #  MATCH (s:PagerDutySchedule{id: relation.schedule}), (u:PagerDutyUser{id: relation.user})
        {"id": PropertyRef("PROJECT_ID", set_in_kwargs=True)},
    )
    direction: LinkDirection = LinkDirection.INWARD
    rel_label: str = "MEMBER_OF"
    properties: PagerDutyScheduleToUserProperties = PagerDutyScheduleToUserProperties()


@dataclass(frozen=True)
class PagerDutyScheduleSchema(CartographyNodeSchema):
    label: str = "PagerDutySchedule"
    properties: PagerDutyScheduleProperties = PagerDutyScheduleProperties()
    scoped_cleanup: bool = False
    other_relationsips: OtherRelationships = OtherRelationships(
        [
            PagerDutyScheduleToUserRel(),
        ]
    )
