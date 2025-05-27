    ingestion_cypher_query = """
    UNWIND $EscalationPolicies AS policy
        MERGE (p:PagerDutyEscalationPolicy{id: policy.id})
        ON CREATE SET p.html_url = policy.html_url,
            p.firstseen = timestamp()
        SET p.type = policy.type,
            p.summary = policy.summary,
            p.on_call_handoff_notifications = policy.on_call_handoff_notifications,
            p.name = policy.name,
            p.num_loops = policy.num_loops,
            p.lastupdated = $update_tag
    """


    ingestion_cypher_query = """
    UNWIND $Rules AS rule
        MERGE (epr:PagerDutyEscalationPolicyRule{id: rule.id})
        ON CREATE SET epr.firstseen = timestamp()
        SET epr.escalation_delay_in_minutes = rule.escalation_delay_in_minutes,
            epr.lastupdated = $update_tag
        WITH epr, rule
        MATCH (ep:PagerDutyEscalationPolicy{id: rule._escalation_policy_id})
        MERGE (ep)-[r:HAS_RULE]->(epr)
        ON CREATE SET r.firstseen = timestamp()
        SET r.order = rule._escalation_policy_order
    """

    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (p:PagerDutyEscalationPolicyRule{id: relation.rule}),
        (u:PagerDutyUser{id: relation.user})
        MERGE (p)-[r:ASSOCIATED_WITH]->(u)
        ON CREATE SET r.firstseen = timestamp()
    """

    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (p:PagerDutyEscalationPolicyRule{id: relation.rule}),
        (s:PagerDutySchedule{id: relation.schedule})
        MERGE (p)-[r:ASSOCIATED_WITH]->(s)
        ON CREATE SET r.firstseen = timestamp()
    """

    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (p:PagerDutyEscalationPolicy{id: relation.escalation_policy}),
        (s:PagerDutyService{id: relation.service})
        MERGE (s)-[r:ASSOCIATED_WITH]->(p)
        ON CREATE SET r.firstseen = timestamp()
    """

    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (p:PagerDutyEscalationPolicy{id: relation.escalation_policy}),
        (t:PagerDutyTeam{id: relation.team})
        MERGE (t)-[r:ASSOCIATED_WITH]->(p)
        ON CREATE SET r.firstseen = timestamp()
    """