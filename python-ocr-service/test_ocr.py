from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="en",
)

result = ocr.predict(
    "samples/12th.jpg"
)

for res in result:
    texts = res["rec_texts"]
    scores = res["rec_scores"]

    for text, score in zip(texts, scores):
        print(f"{score:.2f}  |  {text}")