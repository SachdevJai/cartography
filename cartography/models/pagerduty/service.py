    ingestion_cypher_query = """
    UNWIND $Services AS service
        MERGE (s:PagerDutyService{id: service.id})
        ON CREATE SET s.html_url = service.html_url,
            s.firstseen = timestamp()
        SET s.type = service.type,
            s.summary = service.summary,
            s.name = service.name,
            s.description = service.description,
            s.auto_resolve_timeout = service.auto_resolve_timeout,
            s.acknowledgement_timeout = service.acknowledgement_timeout,
            s.created_at = service.created_at,
            s.status = service.status,
            s.alert_creation = service.alert_creation,
            s.alert_grouping_parameters_type = service.alert_grouping_parameters_type,
            s.incident_urgency_rule_type = service.incident_urgency_rule.type,
            s.incident_urgency_rule_during_support_hours_type = service.incident_urgency_rule.during_support_hours.type,
            s.incident_urgency_rule_during_support_hours_urgency = service.incident_urgency_rule.during_support_hours.urgency,
            s.incident_urgency_rule_outside_support_hours_type = service.incident_urgency_rule.outside_support_hours.type,
            s.incident_urgency_rule_outside_support_hours_urgency = service.incident_urgency_rule.outside_support_hours.urgency,
            s.support_hours_type = service.support_hours.type,
            s.support_hours_time_zone = service.support_hours.time_zone,
            s.support_hours_start_time = s.support_hours.start_time,
            s.support_hours_end_time = s.support_hours.end_time,
            s.support_hours_days_of_week = s.support_hours.days_of_week,
            s.lastupdated = $update_tag
    """  # noqa: E501

    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (t:PagerDutyTeam{id: relation.team}), (s:PagerDutyService{id: relation.service})
        MERGE (t)-[r:ASSOCIATED_WITH]->(s)
        ON CREATE SET r.firstseen = timestamp()
    """