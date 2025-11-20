from typing import List

from core.models import Organization
from submission.models import FrozenAuthor


class JATSFrozenAuthor:
    """
    Adds some small details for the Frozen Author we need for JATS configuration.
    """
    people_id: str | None

    person: FrozenAuthor | None

    def __init__(self, author: FrozenAuthor = None, people_id: str = None):
        self.person = author
        self.people_id = people_id


class JATSFrozenAffiliation:
    """
    Adds some small details for the organizations from FrozenAuthor we need for JATS configuration.
    """
    ringgold_id: str | None

    affiliation: Organization | None

    def __init__(self, affiliation: Organization = None, ringgold_id: str = None):
        self.affiliation = affiliation
        self.ringgold_id = ringgold_id


class FrozenAuthorForJats:
    """
    A class for managing a stub relationship.
    """
    author: JATSFrozenAuthor | None

    affiliations: List[JATSFrozenAffiliation]

    def __init__(self):
        self.author = None
        self.affiliations = []
