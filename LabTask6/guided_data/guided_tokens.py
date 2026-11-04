import re

text = "I can't submit CS4944 late!"
whitespace = text.split()
words = re.findall(r"\b\w+\b", text)

if __name__ == "__main__":
    print("Whitespace:", whitespace, len(whitespace))
    print("Word-like:", words, len(words))
    print("Original:", text)
