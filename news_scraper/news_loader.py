import pandas as pd

def load_news(csv_path='data/news.csv', fruit_type=None):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return []

    if fruit_type:
        df = df[df.apply(lambda row: fruit_type.lower() in str(row).lower(), axis=1)]

    return df.to_dict(orient="records")

def get_article_by_id(article_id, csv_path='data/news.csv'):
    try:
        df = pd.read_csv(csv_path)
        article = df[df['id'] == article_id].to_dict(orient="records")
        return article[0] if article else None
    except Exception:
        return None
