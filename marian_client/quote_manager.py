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

        This implementation could be much better, but it probably isn't worth the effort

        In [7]: dmp.diff_main("Yeah, he'd've done something 'intelligent' I
        ...: guess.", "Yeah, he's done something 'intelligent'")
        Out[7]:
        [(0, "Yeah, he'"),
        (-1, "d've"),
        (1, 's'),
        (0, " done something 'intelligent'"),
        (-1, ' I guess.')]
        """
        diff = dmp.diff_main(self.simplified, modified_string)
        quotes = self.quote_positions[:]

        requoted = ""
        PREVIOUS_DELETE = False
        PREVIOUS_QUOTE_COUNT = 0, 0
        for kind, substr in diff:
            if kind == 0:
                # this part of the string has not been changed
                for char in list(substr):
                    if Quotes.is_quote(char):
                        requoted += quotes.pop(0)
                    else:
                        requoted += char
            elif kind == -1:
                PREVIOUS_DELETE = True
                PREVIOUS_QUOTE_COUNT = Quotes.count_quotes(substr)
            elif kind == 1:
                if not PREVIOUS_DELETE:
                    # this is addition, not replacement
                    # no need to do anything, leave as dumb quote
                    pass
                else:
                    modified_quote_count = Quotes.count_quotes(substr)
                    if PREVIOUS_QUOTE_COUNT == modified_quote_count:
                        # the edit didn't change the quote count
                        for char in list(substr):
                            if Quotes.is_quote(char):
                                requoted += quotes.pop(0)
                            else:
                                requoted += char
                    else:
                        # the only cases we handle are if a single quote was deleted
                        # everything else is too rare and complicated
                        old_single, old_double = PREVIOUS_QUOTE_COUNT
                        new_single, new_double = modified_quote_count
                        if old_single == 1 and new_single == 0:
                            # find the first single quote in quotes and delete it
                            for i, q in enumerate(quotes):
                                if q in Quotes.singles:
                                    del quotes[i]
                                    break
                        if old_double == 1 and new_double == 0:
                            # find the first double quote in quotes and delete it
                            for i, q in enumerate(quotes):
                                if q in Quotes.doubles:
                                    del quotes[i]
                                    break
                        requoted += substr
                PREVIOUS_DELETE = False
                PREVIOUS_QUOTE_COUNT = 0, 0
            else:
                # kind should only ever be 0, -1, or 1
                pass
        return requoted

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

