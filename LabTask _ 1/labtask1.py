def symbolic(score, complete, credits=30, clean_record=True):
 return "Review" if complete and score >= 70 and credits >= 30 and clean_record else "Hold"

def threshold(probability):
 return "Review" if probability >= 0.70 else "Hold"

cases = [
 ("complete_high", 82, True, 0.81, 45, True, "Review", "All conditions met"),
 ("complete_low", 68, True, 0.74, 20, True, "Hold", "Credits below 30"),
 ("incomplete_high", 91, False, 0.88, 40, False, "Hold", "Record violation and incomplete"),
 ("boundary", 70, True, 0.70, 30, True, "Review", "Exact boundary values for score and credits")
 ]

print("case | symbolic | threshold | disagreement")

for name, score, complete, probability, credits, clean_record, expected, reason in cases:
 a, b = symbolic(score, complete, credits, clean_record), threshold(probability)

 print(name, a, b, a != b, sep=" | ") 
 print("input:", (score, complete, credits, clean_record), "| expected:", expected, "| actual:", a, "| reason:", reason)
