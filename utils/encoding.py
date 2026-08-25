from typing import TypedDict
from xml.sax.saxutils import escape

from submission.models import FieldAnswer


class JATSField(TypedDict):
    slug: str
    name: str


class JATSFieldAnswer(TypedDict):
    field: JATSField
    answer: str


def encode_string_for_xml(str_to_encode: str) -> str:
    """
    Takes a string and encodes it for XML.
    :param str_to_encode: The string to encode.
    :return: The encoded string.
    """

    # By default, escape doesn't remove quotes.
    return escape(str_to_encode, entities={"'": "&apos;", '"': "&quot;"})


def encode_answer_field(answer_field: FieldAnswer) -> JATSFieldAnswer:
    """
    Encodes an answer field for usage in JATS.
    :param answer_field: The answer field to encode.
    :return: The encoded field.
    """
    field: JATSField = JATSField(
        slug=encode_string_for_xml(answer_field.field.slug),
        name=encode_string_for_xml(answer_field.field.name),
    )
    return JATSFieldAnswer(
        field=field, answer=encode_string_for_xml(answer_field.answer)
    )
