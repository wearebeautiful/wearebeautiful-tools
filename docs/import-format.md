Model import format specification
=================================

Format version: 1

File contents
-------------

In order to import an model files into the site, the file
needs to be in a ZIP compressed file containing:

* manifest.json                - A JSON document that defines the metadata for the model. See below
* model-surface-low-res.obj    - A surface in correct orientation, viewable on a mobile phone or tablet.
* model-surface-medium-res.obj - A surface in correct orientation, viewable on a larger screen such as a desktop.
* model-surface-high-res.obj   - original resolution surface, for archival purposes.
* model-solid-print-res.obj    - print solid in resolution suited for printing.

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
    "country":        "ES",
    "age":            34,
    "body_type":      "thin",
    "mother":         "no",
    "ethnicity":      "of carribean descent",
    "modification":   "none",
    "comment":        "",       
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

Allowable values: 
 
`"female", "male", "trans-mtf", "trans-ftm", "other"`

If other is given for gender, a command giving more information must be present in
the "gender_comment" field.

country
-------

A two character ISO country code

age
---

Age in years of the model when model was created.


ethnicity
---------

This is a free form text field that the model should self declare. There is no existing taxonomy that handles
this well on a glabal scale. 


body_type
---------

Allowable values:

`"thin", "fit", "full", "overweight"`

mother
------

Is the model a mother? 

`"no", "natural", "caesarean"`


comment
-------

General comment about the model not captured in other metadata.


modification
------------

Indicates modifciation of the model. Accepted values, an array of one or more of the following:

   "none", "circumcised"," fgm", "labiaplasty", "masectomy", "female-to-male", "male-to-female", "breastfeeding", "pregnant"


other
-----

Free form dictionary for custom data fields -- these fields may be accepted as full fiels in the future.

