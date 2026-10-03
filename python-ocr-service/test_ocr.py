from ocr_service import extract_marksheet
import json


result = extract_marksheet(
    "samples/12th.jpg"
)


print(
    json.dumps(
        result,
        indent=4
    )
)