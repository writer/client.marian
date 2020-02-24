from typing import Tuple

import pytest

from marian_client.quote_manager import Quotes


smart_quotes = [
    "We’ve sent you a couple of emails, but we haven’t heard back.",
    "Yeah, he’d’ve done something ʻsmartʼ I guess.",
    "One of these customers calls in, saying, ‘I’m upset about a bad Yelp review I got and also I don’t understand how this part of my ads program is working.’",
    "You get another phone call and it’s a business that says something.",
    "They say, ‘Hey, I’d like to actually grow my business more and I’d like to spend more money.’",
]

change_words_not_quotes = [
    "We've sent you a couple of emails, but we haven't heard back.",
    "Yeah, she'll've said something 'intelligent' I suppose.",
    "A customers calls in and says, 'I'm not happy with a Yelp review I got and also I don't understand how this part of my ads program is working.'",
    "You get a second phone call and it's a company that says something.",
    "They say, 'I'd like to grow my business and I'd like to spend more money.'",
]

requoted = [
    "We’ve sent you a couple of emails, but we haven’t heard back.",
    "Yeah, she’ll’ve said something ʻintelligentʼ I suppose.",
    "A customers calls in and says, ‘I’m not happy with a Yelp review I got and also I don’t understand how this part of my ads program is working.’",
    "You get a second phone call and it’s a company that says something.",
    "They say, ‘I’d like to grow my business and I’d like to spend more money.’",
]


@pytest.mark.parametrize("text", smart_quotes)
def test_requote_no_change(text: str):
    q = Quotes(text)
    assert q.requote_modified_string(q.simplified) == q.orig


@pytest.mark.parametrize(
    "before_after_correct", list(zip(smart_quotes, change_words_not_quotes, requoted))
)
def test_text_change_but_same_quote_count(before_after_correct: Tuple[str, str, str]):
    before, after, correct = before_after_correct
    q = Quotes(before)
    assert q.requote_modified_string(after) == correct


changed_quote_cases = [
    (
        "Yeah , he’d’ve done something “intelligent”",
        'Yeah , he\'s done something "intelligent"',
        "Yeah , he’s done something “intelligent”",
    ),
    (
        "There are many storeʼs like that one , which Iʼm a fan of",
        "There are many stores like that one , which I'm a fan of",
        "There are many stores like that one , which Iʼm a fan of",
    ),
]


@pytest.mark.parametrize("before_after_correct", changed_quote_cases)
def test_change_quote_count(before_after_correct: Tuple[str, str, str]):
    before, after, correct = before_after_correct
    q = Quotes(before)
    assert q.requote_modified_string(after) == correct
