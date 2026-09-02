## Part 1:

```
MATCH (n1:StudyRoot)-[r1]->(n2:StudyValue)
RETURN DISTINCT 'Select' AS Select,
n2.study_number AS StudyID,
n2.study_id_prefix AS StudyName,
n2.study_acronym AS StudyAcronym,
COALESCE(n2.study_subpart_acronym,"No sub study") AS StudySubpart;
```

Select|StudyID|StudyName|StudyAcronym|StudySubpart
--|--|--|--|--
Select|0|CDISC DEV|null|No sub study
Select|0001|CDISC DEV|DDF-SampleData-0001|No sub study
Select|3000|999|DummyStudy 0|No sub study
Select|3001|999|DummyStudy 1|No sub study
Select|3002|999|DummyStudy 2|No sub study
Select|3003|999|DummyStudy 3|No sub study
Select|3004|999|DummyStudy 4|No sub 


## Part 2:

$neodash_studyid -> replace with "0" for example

```
MATCH (n1:StudyRoot)-[r1]->(n2:StudyValue) WHERE n2.study_number = "0"
    RETURN 'Study Name' AS label,
    n2.study_id_prefix AS Value
    UNION
MATCH (n2)-[r2]->(n3:StudyTextField) WHERE n2.study_number = "0" AND n3.field_name = "study_title"
    RETURN 'Study Description' AS label,
    n3.value AS Value
    UNION
MATCH (n1:StudyRoot)-[r1]->(n2:StudyValue) WHERE n2.study_number = "0"
    RETURN 'Protocol Name' AS label,
    n2.study_acronym AS Value;
```

label|Value
-- |--
Study Name|CDISC DEV
Study Description|Title for this Study
Study Description|Title for this Study (new)
Protocol Name|null

## Part 3:

```
MATCH (n1:SponsorModelValue)-[r1:EXTENDS_VERSION]->(n2:DataModelIGValue)
RETURN "Select" AS Select,
n1.name AS SponsorModelIg,
n2.name AS CdiscModelIg,
n2.effective_date AS EffectiveDate,
n2.version_number AS Version;
```

Select|SponsorModelIg|CdiscModelIg|EffectiveDate|Version
--|--|--|--|--
Select|sdtmig_mastermodel_3.2_NN15|SDTMIG v3.2|2013-11-26|3.2
Select|sdtmig_mastermodel_3.3_NN01|SDTMIG v3.3|2018-11-20|3.3
Select|sdtmig_mastermodel_3.3_NN02|SDTMIG v3.3|2018-11-20|3.3
Select|sdtmig_mastermodel_3.3_NN03|SDTMIG v3.3|2018-11-20|3.3


## Part 4:

Fixed Query (OPTIONAL is not possible, a relationship is missing)

```
// Study selection with applicable Visits and Study Activities and Grouping New Version
MATCH ()-[r1:LATEST]->(n2:StudyValue {study_number: "0"})-[r2:HAS_STUDY_VISIT]->(n3:StudyVisit)-[r3:STUDY_VISIT_HAS_SCHEDULE]->(n4:StudyActivitySchedule)<-[r4:STUDY_ACTIVITY_HAS_SCHEDULE]-(n5:StudyActivity)
// Connection between Study Activities to Library Activities and back to the Study Visits
WITH DISTINCT n5
MATCH (n5)-[r9:HAS_SELECTED_ACTIVITY]->(n10:ActivityValue)-[r10:HAS_GROUPING]->(n11:ActivityGrouping)<-[r11:HAS_ACTIVITY]-(n12:ActivityInstanceValue)<-[r12:HAS_SELECTED_ACTIVITY_INSTANCE]-(n13:StudyActivityInstance)
WITH DISTINCT n12
// Looking at the SDTMIG and the connected MasterModel
MATCH (n27:DataModelIGValue)<-[r28:EXTENDS_VERSION]-(n28:SponsorModelValue)  
WHERE n28.name="sdtmig_mastermodel_3.2_NN15"
// Display the Domain connected to the ActivityInstance
//OPTIONAL MATCH (n12)-[r29:CONTAINS_ACTIVITY_ITEM]->(n29:ActivityItem)<-[r30:HAS_ACTIVITY_ITEM]-(n30:ActivityItemClassRoot)-[r31:MAPS_VARIABLE_CLASS]->(n31:VariableClass {uid:'DOMAIN'})-[r32:HAS_INSTANCE]->(n32:VariableClassInstance)<-[r33:IMPLEMENTS_VARIABLE{version_number:n27.version_number}]-(n33:DatasetVariableInstance)<-[r34:HAS_DATASET_VARIABLE {version_number:n27.version_number}]-(n34:DatasetInstance)<-[r35:HAS_INSTANCE]-(n35:Dataset) ,
//               (n29)-[r36:HAS_CT_TERM]->(n36:CTTermRoot)-[r37:HAS_ATTRIBUTES_ROOT]->(n37:CTTermAttributesRoot)-[r38:LATEST]->(n38:CTTermAttributesValue)  
//WHERE n35.uid = n38.code_submission_value
//WITH DISTINCT n34, n35
MATCH (n35)-[r57:HAS_INSTANCE]->(n48:SponsorModelDatasetInstance)
MATCH (n34)-[r58:IMPLEMENTS_DATASET_CLASS]->(n54:DatasetClassInstance)
RETURN DISTINCT n35.uid AS Dataset, n48.label AS Description, n54.label AS Class, n48.structure AS Structure, "Tabulation" AS Purpose, "To be Specify" AS Keys, n34.description AS Documentation, TOLOWER(n35.uid)||".xpt" AS Location;
```

With placeholders:

```
// Study selection with applicable Visits and Study Activities and Grouping New Version
MATCH ()-[r1:LATEST]->(n2:StudyValue {study_number: $neodash_studyid})-[r2:HAS_STUDY_VISIT]->(n3:StudyVisit)-[r3:STUDY_VISIT_HAS_SCHEDULE]->(n4:StudyActivitySchedule)<-[r4:STUDY_ACTIVITY_HAS_SCHEDULE]-(n5:StudyActivity)
// Connection between Study Activities to Library Activities and back to the Study Visits
WITH DISTINCT n5
MATCH (n5)-[r9:HAS_SELECTED_ACTIVITY]->(n10:ActivityValue)-[r10:HAS_GROUPING]->(n11:ActivityGrouping)<-[r11:HAS_ACTIVITY]-(n12:ActivityInstanceValue)<-[r12:HAS_SELECTED_ACTIVITY_INSTANCE]-(n13:StudyActivityInstance)
WITH DISTINCT n12
// Looking at the SDTMIG and the connected MasterModel
MATCH (n27:DataModelIGValue)<-[r28:EXTENDS_VERSION]-(n28:SponsorModelValue)  
WHERE n28.name=$neodash_sponsor_model
// Display the Domain connected to the ActivityInstance
//OPTIONAL MATCH (n12)-[r29:CONTAINS_ACTIVITY_ITEM]->(n29:ActivityItem)<-[r30:HAS_ACTIVITY_ITEM]-(n30:ActivityItemClassRoot)-[r31:MAPS_VARIABLE_CLASS]->(n31:VariableClass {uid:'DOMAIN'})-[r32:HAS_INSTANCE]->(n32:VariableClassInstance)<-[r33:IMPLEMENTS_VARIABLE{version_number:n27.version_number}]-(n33:DatasetVariableInstance)<-[r34:HAS_DATASET_VARIABLE {version_number:n27.version_number}]-(n34:DatasetInstance)<-[r35:HAS_INSTANCE]-(n35:Dataset) ,
//               (n29)-[r36:HAS_CT_TERM]->(n36:CTTermRoot)-[r37:HAS_ATTRIBUTES_ROOT]->(n37:CTTermAttributesRoot)-[r38:LATEST]->(n38:CTTermAttributesValue)  
//WHERE n35.uid = n38.code_submission_value
//WITH DISTINCT n34, n35
MATCH (n35)-[r57:HAS_INSTANCE]->(n48:SponsorModelDatasetInstance)
MATCH (n34)-[r58:IMPLEMENTS_DATASET_CLASS]->(n54:DatasetClassInstance)
RETURN DISTINCT n35.uid AS Dataset, n48.label AS Description, n54.label AS Class, n48.structure AS Structure, "Tabulation" AS Purpose, "To be Specify" AS Keys, n34.description AS Documentation, TOLOWER(n35.uid)||".xpt" AS Location;
```


Dataset|Description|Class|Structure|Purpose|Keys|Documentation|Location
--|--|--|--|--|--|--|--
AE|Adverse Events|null|One record per adverse event per subject|Tabulation|To be Specify|Laboratory Findings|ae.xpt
AG|Procedure Agents|null|One record per recorded intervention occurrence per subject|Tabulation|To be Specify|Laboratory Findings|ag.xpt
APCE|AP Clinical Events|null|One record per event per associated person|Tabulation|To be Specify|Laboratory Findings|apce.xpt
APAE|AP Adverse Events|null|One record per adverse event per associated person|Tabulation|To be Specify|Laboratory Findings|apae.xpt
APCM|AP Concomitant Medications|null|One record per recorded medication occurrence or constant-dosing interval per associated person|Tabulation|To be Specify|Laboratory Findings|apcm.xpt
APDM|AP Demographics|null|One record per associated person|Tabulation|To be Specify|Laboratory Findings|apdm.xpt
APDD|AP Death Details|null|One record per finding per associated person|Tabulation|To be Specify|Laboratory Findings|apdd.xpt
APFACE|AP Findings About Clinical Events|null|One record per finding information per clinical event per associated person|Tabulation|To be Specify|Laboratory Findings|apface.xpt