def predict_sentiment(text):
    text = text.lower()
    if any(word in text for word in ["tệ", "dở", "bực", "ghét", "không thích", "thất vọng", "xấu", "kém", "tồi", "chán", "buồn", "khó chịu", "ngu"]):
        return "tiêu cực"
    elif any(word in text for word in ["tốt", "ngon", "hài lòng", "thích", "yêu thích", "tuyệt vời", "đẹp", "hài hước", "thú vị", "đáng yêu", "tích cực"]):
        return "tích cực"
    else:
        return "trung lập"
