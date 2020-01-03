Model import format specification
=================================

Format version: 1

short_codes:
------------

part, postion, arrangement, excited = BSNN


manifest.json
-------------

The manifest.json file should be a valid JSON document that contains the 
following keys:

```json
{
    "version":        1,
    "id":             "<model ID>",
    "created":        "2019-05",
    "released":       "2019-07-09",
    "gender":         "female",
    "gender_comment": "",
    "body_type":      "thin",
    "body_part":      "bust",
    "pose":           "normal",
    "mother":         "vaginal",
    "tags":           ["post_pregnancy"],
    "modification":   ["pregnancy", "breastfed"],
    "comment":        "Model was breastfeeding at the time.",       
    "other":          {}
}
```

id
--

The unique ID of the model

created
-------

A partial ISO 8601 timestamp of when model was created: YYYY-MM


released
--------

An ISO 8601 date of when model was released to on the we are beautiful site: YYYY-MM-DD


gender
------

| Allowable values |
| --------- |
| female |
| male |
| trans-mtf |
| trans-ftm |
| other |

If other is given for gender, a command giving more information must be present in
the "gender_comment" field.



body_type
---------

| Allowable values |
| --------- |
| thin |
| fit |
| full |
| overweight |


bodypart
--------

Allowable values and their short cut codes:

| short| full text |
|------|---------|
| A    |anatomical |
| F    |full body |
| L    |lower body |
| U    |upper body |
| B    |breast |
| K    |buttocks |
| N    |nipple |
| P    |penis |
| T    |torso |
| V    |vulva |


excited 
-------

Allowable values and their short cut codes:

| short|full text |
|------|---------|
| N    |not-excited |
| X    |excited |
| P    |partially excited |


arrangement
-----------

Allowable values and their short cut codes:

| short|full text |
|------|---------|
| S    |spread (have the vulva lips been spread apart?) |
| R    |retracted (is the foreskin retracted?) |
| A    |arranged (arrange in a fashion to illustrate a body feature) |
| N    |natural (as it appears when becoming unclothed) |


pose
----

Allowable values and their short cut codes:

| short|full text |
|------|---------|
| S    |standing |
| T    |sitting |
| L    |lying |


mother
------

Is the model a mother? If so, how was/were the child/children delivered?

| Allowable values |
| --------- |
| not |
| vaginal |
| caesarean |


modification
------------

Indicates modifciation of the model. One of more of the following may be allowed:

| Allowable values |
| --------- |
| pregnancy |
| nursed |
| circumcised |
| augmentated |
| episiotomy |
| masectomy  |
| labiaplasty |
| female-to-male |
| male-to-female |
| fgm |


tags
----

An array of tags (without hashes) that may also apply to this model.

"#large-hips #hip-scar" would be expressed in JSON as:

 `["large-hips", "hip-scar"]`  


comment
-------

General comment about the model not captured in other metadata. Free form text.


other
-----

Free form dictionary for custom data fields -- these fields may be accepted as full fiels in the future.

