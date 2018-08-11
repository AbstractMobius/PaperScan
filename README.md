# PaperScan
## Utility that enables the comparison of two papers based on word semantics and paragraph structure to validate or invalidate originality

### How to use:
* this method checks to see if two papers are 90% semantically similar, therefore it is highly likely that they cheated.

```python
similarity_threshold = 0.90  # define similarity threshold
scanner = PaperScanner(google_news_binary)  # instantiate scanner
def papers_copied(paper1_file_location, paper2_file_location):
  # if two papers more similar than given threshold
  if (paper.compare(paper1_file_location, paper2_file_location) >= similarity_threshold):
    return True  # then two papers were copied
  return False  # then they were not copied
```

