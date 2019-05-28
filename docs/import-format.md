Model import format specification
=================================

Format version: 1

File contents
-------------

In order to import an STL file into the site, the file
needs to be in a ZIP compressed file containing:

manifest.json     - A JSON document that defines the metadata for the model. See below
model-low-res.stl - An STL file with the model oriented in the way it should be shown on the
                    site by default. The low resolution model should contain enough detail
                    to be viewed on a mobile phone.
model-medium-res.stl - An STL file in correct orientation, viewable on a larger screen such as 
                       a desktop.
model-high-res.stl   - An STL file in correct orientation, suitable for download for printing.

manifest.json
-------------

The manifest.json file should be a valid JSON document that contains the 
folowing keys:

  {
      "id":             "<model ID>",                # The unique ID of the model
      "created":        "2019-05-27T23:27:56+00:00"  # An ISO 8601 timestamp of when model was created.
      "gender":         "female",                    # See below for allawable values
      "gender_comment": ""                           # Comment that refines possible gender information.
      "country":        "ES",                        # A two character ISO country code
      "age":            34,                          # Age in years of the model when model was created.
      "ethnicity":      "black"                      # Ethnicity of model. See below
      "body type":      "thin",                      # Body type. See below
      "comment":        "of carribean descent"       # General comments about the model. 
  }

Gender
------

Allowable values: 
 
>  "female", "male", "trans-mtf", "trans-ftm", "other". 

If other is given for gender, a command giving more information must be present in
the "gender_comment" field.


Ethnicity
---------

TBC -- looking for some international standard that we can follow.

We may decide on a smaller list of ethnicities and then also add a ehtnicity_comment field.


Body type
---------

Allowable values:

>  "thin", "fit", "full", "overweight"
