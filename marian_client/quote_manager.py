from typing import List, Tuple

from diff_match_patch import diff_match_patch


dmp = diff_match_patch()


class Quotes:
    singles = [
        "｀",
        "΄",
        "＇",
        "ˈ",
        "ˊ",
        "ᑊ",
        "ˋ",
        "ꞌ",
        "ᛌ",
        "𖽒",
        "𖽑",
        "‘",
        "’",
        "י",
        "՚",
        "‛",
        "՝",
        "`",
        "'",
        "′",
        "׳",
        "´",
        "ʹ",
        "˴",
        "ߴ",
        "‵",
        "ߵ",
        "ʻ",
        "ʼ",
        "᾽",
        "ʽ",
        "῾",
        "ʾ",
        "᾿",
    ]
    doubles = ['"', "＂", "〃", "ˮ", "ײ", "″", "״", "‶", "˶", "ʺ", "“", "”", "˝", "‟"]
    ascii_single = "'"
    ascii_double = '"'

    def __init__(self, orignal_string):
        self.orig = orignal_string
        # A list of characters that will be joined into the simplified string
        simplified_split: List[str] = []
        # List of quotes, where index of i means the ith quote in the string
        # is quote_positions[i] type of quote
        self.quote_positions: List[str] = []

        for char in list(self.orig):
            if char in Quotes.singles or char in Quotes.doubles:
                self.quote_positions.append(char)
            if char in Quotes.singles:
                simplified_split.append(Quotes.ascii_single)
            elif char in Quotes.doubles:
                simplified_split.append(Quotes.ascii_double)
            else:
                simplified_split.append(char)

        self.simplified = "".join(simplified_split)

    @staticmethod
    def is_quote(char: str):
        return char in Quotes.singles or char in Quotes.doubles

    @staticmethod
    def count_quotes(text: str) -> Tuple[int, int]:
        chars = list(text)
        single_count = sum(x in Quotes.singles for x in chars)
        double_count = sum(x in Quotes.doubles for x in chars)
        return single_count, double_count

    def requote_same_quote_count(self, modified_string: str):
        requoted_split = []
        quotes = self.quote_positions[:]  # make a copy
        for char in list(modified_string):
            if Quotes.is_quote(char):
                requoted_split.append(quotes.pop(0))
            else:
                requoted_split.append(char)
        return "".join(requoted_split)

    def requote_different_quote_count(self, modified_string: str):
        """
        @TODO - assume this is rare and just make a best effort
        The idea is to use dmp to find diffs where the quotes don't match
        if the quote is an addition, don't touch it
        if the quote is removed, just throw that one away

        In [7]: dmp.diff_main("Yeah, he'd've done something 'intelligent' I
        ...: guess.", "Yeah, he's done something 'intelligent'")
        Out[7]:
        [(0, "Yeah, he'"),
        (-1, "d've"),
        (1, 's'),
        (0, " done something 'intelligent'"),
        (-1, ' I guess.')]
        """
        return modified_string

    def requote_modified_string(self, modified_string: str) -> str:
        requoted = ""
        if self.simplified == modified_string:
            # the easiest case
            requoted = self.orig
        elif Quotes.count_quotes(modified_string) == Quotes.count_quotes(
            self.simplified
        ):
            # assume that if the count of single- and double-quotes hasn't changed
            # then this is not a coincidence
            # What if GEC deleted one quote but added another?
            # Potential bug, but seems so unlikely
            requoted = self.requote_same_quote_count(modified_string)
        else:
            requoted = self.requote_different_quote_count(modified_string)
        return requoted

