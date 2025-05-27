    ingestion_cypher_query = """
    UNWIND $Vendors AS vendor
        MERGE (v:PagerDutyVendor{id: vendor.id})
        ON CREATE SET v.firstseen = timestamp()
        SET v.type = vendor.type,
            v.summary = vendor.summary,
            v.name = vendor.name,
            v.website_url = vendor.website_url,
            v.logo_url = vendor.logo_url,
            v.thumbnail_url = vendor.thumbnail_url,
            v.description = vendor.description,
            v.integration_guide_url = vendor.integration_guide_url,
            v.lastupdated = $update_tag
    """