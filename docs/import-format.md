Model import format specification
=================================

Format version: 1

File contents
-------------

In order to import an STL file into the site, the file
needs to be in a ZIP compressed file containing:

* manifest.json     - A JSON document that defines the metadata for the model. See below
* model-low-res.stl - An STL file with the model oriented in the way it should be shown on the
                    site by default. The low resolution model should contain enough detail
                    to be viewed on a mobile phone.
* model-medium-res.stl - An STL file in correct orientation, viewable on a larger screen such as 
                       a desktop.
* model-high-res.stl   - An STL file in correct orientation, suitable for download for printing.

manifest.json
-------------

The manifest.json file should be a valid JSON document that contains the 
folowing keys:

```json
{
    "version":        1,
    "id":             "<model ID>",
    "created":        "2019-05",
    "gender":         "female",
    "gender_comment": "",
    "country":        "ES",
    "age":            34,
    "body_type":      "thin",
    "mother":         "false",
    "ethnicity":      "of carribean descent",
    "modification":   "none",
    "comment":        "",       
    "other"           {}
}
```

id
--

The unique ID of the model

created
-------

A partial ISO 8601 timestamp of when model was created: YYYY-MM


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

Is the model a mother? Boolean.


comment
-------

General comment about the model not captured in other metadata.


modification
------------

Indicates modifciation of the model. Accepted values:

   "none", "circumcised"," fgm", "labiaplasty", "masectomy", "female-to-male","male-to-female"

other
-----

Free form dictionary for custom data fields -- these fields may be accepted as full fiels in the future.

