    ingestion_cypher_query = """
    UNWIND $Integrations AS integration
        MERGE (i:PagerDutyIntegration{id: integration.id})
        ON CREATE SET i.html_url = integration.html_url,
            i.firstseen = timestamp()
        SET i.type = integration.type,
            i.summary = integration.summary,
            i.name = integration.name,
            i.created_at = integration.created_at,
            i.lastupdated = $update_tag
        WITH i, integration
        MATCH (v:PagerDutyVendor{id: integration.vendor.id})
        MERGE (i)-[vr:HAS_VENDOR]->(v)
        ON CREATE SET vr.firstseen = timestamp()
        SET vr.lastupdated = $update_tag
        WITH i, integration
        MATCH (s:PagerDutyService{id: integration.service.id})
        MERGE (s)-[sr:HAS_INTEGRATION]->(i)
        ON CREATE SET sr.firstseen = timestamp()
        SET sr.lastupdated = $update_tag
    """