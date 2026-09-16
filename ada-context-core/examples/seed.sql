-- Illustrative only. Replace with reviewed canonical records during migration.
INSERT INTO tool_registry(tool_name,side_effect_class,mutation_type,requires_receipt,requires_snapshot,requires_live_verification,default_decision)
VALUES
 ('wp_read','READ',NULL,false,false,false,'ALLOW'),
 ('wp_update_metadata','WRITE','METADATA_UPDATE',true,true,true,'ALLOW'),
 ('wp_publish','WRITE','PUBLISH',true,true,true,'ESCALATE'),
 ('wp_delete','DELETE','DELETE',true,true,true,'ESCALATE')
ON CONFLICT(tool_name) DO NOTHING;

-- Example shadow passport: reads only.
INSERT INTO agent_passports(agent_id,task_type,allowed_sites,allowed_tools,allowed_mutation_types,max_batch_size,approval_classes)
VALUES('mistral-shadow','academic_content',ARRAY['teznevise.ir'],ARRAY['wp_read'],ARRAY[]::text[],1,ARRAY['DELETE','WRITE','EXTERNAL_MESSAGE'])
ON CONFLICT DO NOTHING;
