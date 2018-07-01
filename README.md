# PaperScan
## Utility that enables the comparison of two papers based on semantics to validate or invalidate originality

### How to use:
-  similarity_threshold = 0.90
-  scanner = PaperScanner()
-  def papers_copied(file_loc_p1, file_loc_p2):
-    if (paper.compare(file_loc_p1, file_loc_p2) >= similarity_threshold):
-        return True
-    return False
- 
 this method checks to see if two papers are 90% semantically similar, therefore it is highly likely that they cheated.
