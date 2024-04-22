# DD2477-Final-Project
Final project for DD2477

## Structure of data stored in Elasticsearch
Two indexes are maintained INSERT INDEX NAMES HERE. 

The index for books stores the books as dictionaries with the structure:
```
{
  "title": str,
  "author": str,
  "abstract": str,
  "genres": [str],
  "rating": float,
  "n_ratings": int,
  "n_reviews": int,
  "book_id": str,
  "url": str,
  "img_url": str,
}
```
The index for the user profiles stores the profiles as dictionaries with the structure:

```
{
  "name": str
  "books": [str]
  "gen_weight": dict(str, float)
  "abs_weight": dict(str, float)
}
```
