MIN_FREETEXT_FIELD_LEN = 5
LOW_RES_SEGMENT_LEN = .5
MEDIUM_RES_SEGMENT_LEN = .3

REQUIRED_KEYS = [ 
    "version", 
    "id", 
    "created", 
    "sex", 
    "gender", 
    "body_type", 
    "body_part", 
    "given_birth", 
    "released", 
    "pose",
    "arrangement",
    "excited"
]

OPTIONAL_KEYS = [ 
    "gender_comment", 
    "sex_comment", 
    "comment", 
    "other", 
    "tags", 
    "history",
    "make_solid_args",
    "links"
]

GENDERS = [
    "woman", 
    "man", 
    "non binary", 
    "transgender",
    "cisgender",
    "other"
]

SEX = [
    "female", 
    "male", 
    "intersex", 
    "other"
]

BODY_TYPES = [
    "thin", 
    "average", 
    "overweight"
]

BODY_PART = { 
     "anatomical" : "A", 
     "full body" : "F", 
     "lower body" : "L", 
     "upper body" : "U", 
     "breast" : "B", 
     "buttocks" : "O", 
     "nipple" : "N", 
     "penis" : "P", 
     "torso" : "T", 
     "vulva" : "V", 
     "hand" : "H", 
}

EXCITED = {
    "not excited" : "N",
    "excited" : "X",
    "partially excited" : "P"
}

ARRANGEMENT = { 
    "spread" : "S", 
    "retracted" : "R", 
    "arranged" : "A", 
    "natural" : "N", 
}

POSE = { 
    "standing" : "S", 
    "sitting" : "T", 
    "lying" : "L", 
    "lying, legs pulled up" : "U", 
}

HISTORY = [ 
    "pregnancy", 
    "nursed", 
    "circumcised", 
    "augmented", 
    "episiotomy",
    "mastectomy", 
    "labiaplasty", 
    "female-to-male", 
    "male-to-female", 
    "fgm", 
]

GIVEN_BIRTH = [
    "no", 
    "vaginal", 
    "caesarean"
]


COUNTRIES = [ "AF", "AL", "DZ", "Sa", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY",
"BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "CV", "KH", "CM", "CA",
"KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CD", "CG", "CK", "CR", "HR", "CU", "CW", "CY", "CZ", "CI", "DK",
"DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA",
"GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "-B", "GY", "HT", "HM", "VA", "HN", "HK",
"HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW",
"KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ",
"MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NC", "NZ", "NI",
"NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA",
"RO", "RU", "RW", "RE", "BL", "a ", "KN", "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG",
"SX", "SK", "SI", "SB", "SO", "ZA", "GS", "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH",
"TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "UM", "US", "UY", "UZ", "VU", "VE",
"VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "AX" ]
