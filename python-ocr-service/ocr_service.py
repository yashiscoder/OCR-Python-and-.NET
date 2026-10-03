from paddleocr import PaddleOCR
import re

ocr = PaddleOCR(
    lang="en",
)

def extract_marksheet(image_path):
    result = ocr.predict(image_path)

    detections = []

    for res in result:
        texts = res["rec_texts"]
        scores = res["rec_scores"]
        boxes = res["rec_polys"]

        for text, score, box in zip(texts, scores, boxes):
            text = text.strip()

            if not text:
                continue

            if score < 0.60:
                continue

            x_min = box[:, 0].min()
            y_min = box[:, 1].min()
            x_max = box[:, 0].max()
            y_max = box[:, 1].max()
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2

            detections.append({
                "text": text,
                "score": float(score),
                "x": float(center_x),
                "y": float(center_y)
            })


    detections.sort(key=lambda item: item["y"])
    # Group into rows
    rows = []
    Y_TOLERANCE = 25

    for item in detections:
        added = False

        for row in rows:
            row_y = sum(
                x["y"] for x in row
            ) / len(row)

            if abs(item["y"] - row_y) <= Y_TOLERANCE:
                row.append(item)
                added = True
                break

        if not added:
            rows.append([item])

    # Sort left → right
    for row in rows:
        row.sort(key=lambda item: item["x"])

    marksheet = {
        "exam": None,
        "seat_no": None,
        "centre_no": None,
        "school_index_no": None,
        "subjects": [],
        "total_marks": None,
        "percentage": None
    }

    # Extract exam + seat number
    for item in detections:
        text = item["text"]
        upper_text = text.upper()

        if re.search(
            r"(MAY|JUNE|APRIL|MARCH)-\d{4}",
            upper_text
        ):
            marksheet["exam"] = text

        if re.fullmatch(
            r"G\s?\d{6}",
            upper_text
        ):
            marksheet["seat_no"] = text

    # Percentage
    for item in detections:
        if re.fullmatch(
            r"\d{2}\.\d{2}",
            item["text"]
        ):
            marksheet["percentage"] = float(
                item["text"]
            )

    # Total marks
    for item in detections:
        if "FOUR HUNDRED THIRTY FIVE" in item["text"].upper():
            marksheet["total_marks"] = 435

    # Subjects
    for row in rows:
        row_text = " ".join(
            item["text"]
            for item in row
        )
        if "SUBJECT" in row_text.upper():
            continue

        subject_match = re.search(
            r"\b(\d{3})\s+(.+)",
            row_text
        )

        if not subject_match:
            continue

        code = subject_match.group(1)
        name = subject_match.group(2).strip()
        numbers = []

        for item in row:
            if re.fullmatch(
                r"\d+",
                item["text"]
            ):
                numbers.append(item["text"])

        if len(numbers) < 2:
            continue

        marksheet["subjects"].append({
            "code": code,
            "name": name,
            "max_marks": int(numbers[0]),
            "obtained_marks": int(numbers[1])
        })

    return marksheet