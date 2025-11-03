-- migrate:up
-- Run only after importing journal entries
INSERT INTO tags(name, side)
SELECT 
	DISTINCT metadata->>'proposito' AS proposito,
	'debe' -- Default value, check manually for haber tags afterwards
FROM journal_entries
WHERE metadata->'proposito' IS NOT NULL;

INSERT INTO entry_tags(entry_id, tag_id)
SELECT 
	je.id, 
	(SELECT t.id FROM tags t WHERE metadata->>'proposito' = t.name)
FROM journal_entries je
WHERE je.metadata IS NOT NULL;


-- migrate:down
DELETE FROM tags;
DELETE FROM entry_tags;
