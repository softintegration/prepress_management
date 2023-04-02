
--Here we have to get the old data for the field product_template.gram_weight after the update of the field type from float to integer
UPDATE product_template SET gram_weight=gram_weight_moved0;

--Here we have to get the old data for the field prepress_proof.product_gram_weight after the update of the field type from float to integer
UPDATE prepress_proof SET product_gram_weight=product_gram_weight_moved0;



