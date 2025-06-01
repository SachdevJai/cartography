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
class PagerDutyScheduleLayerProperties(CartographyNodeProperties):
    id: PropertyRef = PropertyRef("_layer_id")
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)
    name: PropertyRef = PropertyRef("name")
    schedule_id: PropertyRef = PropertyRef("_schedule_id")
    start: PropertyRef = PropertyRef("start")
    end: PropertyRef = PropertyRef("end")
    rotation_virtual_start: PropertyRef = PropertyRef("rotation_virtual_start")
    rotation_turn_length_seconds: PropertyRef = PropertyRef(
        "rotation_turn_length_seconds"
    )


@dataclass(frozen=True)
class PagerDutyScheduleLayerToScheduleProperties(CartographyRelProperties):
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)


@dataclass(frozen=True)
# (:PagerDutySchedule)-[:HAS_LAYER]->(:PagerDutyScheduleLayer)
class PagerDutyScheduleLayerToScheduleRel(CartographyRelSchema):
    target_node_label: str = "PagerDutySchedule"
    target_node_matcher: TargetNodeMatcher = make_target_node_matcher(
        {"id": PropertyRef("_schedule_id", set_in_kwargs=True)},
    )
    direction: LinkDirection = LinkDirection.INWARD
    rel_label: str = "HAS_LAYER"
    properties: PagerDutyScheduleLayerToScheduleProperties = (
        PagerDutyScheduleLayerToScheduleProperties()
    )


@dataclass(frozen=True)
class PagerDutyScheduleLayerToUserProperties(CartographyRelProperties):
    lastupdated: PropertyRef = PropertyRef("lastupdated", set_in_kwargs=True)


@dataclass(frozen=True)
# (:PagerDutyUser)-[:MEMBER_OF]->(:PagerDutyScheduleLayer)
class PagerDutyScheduleLayerToUserRel(CartographyRelSchema):
    target_node_label: str = "PagerDutyUser"
    target_node_matcher: TargetNodeMatcher = make_target_node_matcher(
        # WIP: Migrate to a one to many transform function
        # MATCH (l:PagerDutyScheduleLayer{id: relation.layer_id}), (u:PagerDutyUser{id: relation.user})
        {"id": PropertyRef("PROJECT_ID", set_in_kwargs=True)},
    )
    direction: LinkDirection = LinkDirection.INWARD
    rel_label: str = "MEMBER_OF"
    properties: PagerDutyScheduleLayerToUserProperties = (
        PagerDutyScheduleLayerToUserProperties()
    )


@dataclass(frozen=True)
class PagerDutyScheduleLayerSchema(CartographyNodeSchema):
    label: str = "PagerDutyScheduleLayer"
    properties: PagerDutyScheduleLayerProperties = PagerDutyScheduleLayerProperties()
    scoped_cleanup: bool = False
    other_relationsips: OtherRelationships = OtherRelationships(
        [
            PagerDutyScheduleLayerToScheduleRel(),
            PagerDutyScheduleLayerToUserRel(),
        ]
    )
