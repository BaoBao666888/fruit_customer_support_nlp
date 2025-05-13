import pandas as pd

def search_product(query, csv_path='data/products.csv'):
    df = pd.read_csv(csv_path)
    query = query.lower()
    
    for _, row in df.iterrows():
        if row['name'].lower() in query:
            return f"{row['name']} có giá {row['price']}đ/kg, xuất xứ {row['origin']}, mùa {row['season']}."
    
    return None
