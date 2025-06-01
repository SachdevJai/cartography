ingestion_cypher_query = """
    UNWIND $Schedules AS schedule
        MERGE (u:PagerDutySchedule{id: schedule.id})
        ON CREATE SET u.html_url = schedule.html_url,
            u.firstseen = timestamp()
        SET u.type = schedule.type,
            u.summary = schedule.summary,
            u.name = schedule.name,
            u.time_zone = schedule.time_zone,
            u.description = schedule.description,
            u.lastupdated = $update_tag
    """


    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (s:PagerDutySchedule{id: relation.schedule}), (u:PagerDutyUser{id: relation.user})
        MERGE (u)-[r:MEMBER_OF]->(s)
        ON CREATE SET r.firstseen = timestamp()
    """


    ingestion_cypher_query = """
    UNWIND $Layers AS layer
        MERGE (l:PagerDutyScheduleLayer{id: layer._layer_id})
        ON CREATE SET l.name = layer.name,
            l.schedule_id = layer._schedule_id
        SET l.start = layer.start,
            l.end = layer.end,
            l.rotation_virtual_start = layer.rotation_virtual_start,
            l.rotation_turn_length_seconds = layer.rotation_turn_length_seconds,
            l.lastupdated = $update_tag
        with l, layer._schedule_id as schedule_id
        MATCH (s:PagerDutySchedule{id: schedule_id})
        MERGE (s)-[r:HAS_LAYER]->(l)
        ON CREATE SET r.firstseen = timestamp()
    """

    ingestion_cypher_query = """
    UNWIND $Relations AS relation
        MATCH (l:PagerDutyScheduleLayer{id: relation.layer_id}), (u:PagerDutyUser{id: relation.user})
        MERGE (u)-[r:MEMBER_OF]->(l)
        ON CREATE SET r.firstseen = timestamp()
    """
