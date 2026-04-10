from hypothesis.extra.django import TestCase
from lxml import etree

from plugins.editorial_manager_transfer_service.utils.jats import get_xml_license_code
from submission.models import Article

DTD_VERSION = "1.1d1"
XLMLNS_XLINK = "http://www.w3.org/1999/xlink"
DEFAULT_ARTICLE_TYPE = "research-article"
JOURNAL_ID_TYPE = "publisher"
ARTICLE_ID_PUB_ID_TYPE = "manuscript"


def validate_xml(self: TestCase, root: etree.ElementTree, article: Article) -> None:
    self.assertEqual("article", root.tag)
    validate_article_root_attributes(self, root, article)

    front = root.find("front")
    self.assertIsNotNone(front)
    validate_front(self, front, article)


def validate_article_root_attributes(self: TestCase, root: etree.ElementTree, article: Article) -> None:
    """
    Validates the attributes associated with the root of the article.
    :param self: The testing object.
    :param root: The root to check.
    :param article: The article to verify against.
    """
    dtd_version = root.get("dtd-version")
    self.assertEqual(DTD_VERSION, dtd_version)

    xml_lang = root.get("{http://www.w3.org/XML/1998/namespace}lang")
    self.assertEqual(article.iso639_1_lang_code, xml_lang)

    article_type = root.get("article-type")
    if article.section:
        section = article.section.jats_article_type
    else:
        section = DEFAULT_ARTICLE_TYPE
    self.assertEqual(section, article_type)


def validate_front(self: TestCase, front: etree.ElementTree, article: Article) -> None:
    journal_meta = front.find("journal-meta")
    self.assertIsNotNone(journal_meta)
    validate_journal_meta(self, journal_meta, article)

    article_meta = front.find("article-meta")
    self.assertIsNotNone(article_meta)
    validate_article_meta(self, article_meta, article)


def validate_journal_meta(self: TestCase, journal_meta: etree.ElementTree, article: Article) -> None:
    """
    Validates the Journal Meta block of JATS.
    :param self: The testing object.
    :param journal_meta: The journal meta to check.
    :param article: The article to verify against.
    """
    journal_id = journal_meta.find("journal-id")
    self.assertIsNotNone(journal_id)

    journal_id_text = journal_id.text
    self.assertIsNotNone(journal_id_text)
    self.assertEqual(get_xml_license_code(article.journal), journal_id_text)

    journal_id_type = journal_id.get("journal-id-type")
    self.assertIsNotNone(journal_id_type)
    self.assertEqual(JOURNAL_ID_TYPE, journal_id_type)

    journal_title_group = journal_meta.find("journal-title-group")
    self.assertIsNotNone(journal_title_group)

    journal_title = journal_title_group.find("journal-title")
    self.assertIsNotNone(journal_title)
    self.assertEqual(article.journal.name, journal_title.text)


def validate_article_meta(self: TestCase, article_meta: etree.ElementTree, article: Article) -> None:
    validate_article_meta_article_id(self, article_meta, article)

    if article.data_figure_files.exists():
        validate_article_meta_counts(self, article_meta, article)


def validate_article_meta_article_id(self: TestCase, article_meta: etree.ElementTree, article: Article) -> None:
    """
    Validates the article metadata associated with the article ID.
    :param self: The testing object.
    :param article_meta: The article meta to check.
    :param article: The article to verify against.
    """
    article_id = article_meta.find("article-id")
    self.assertIsNotNone(article_id)

    article_id_pub_id_type = article_id.get("pub-id-type")
    self.assertIsNotNone(article_id_pub_id_type)
    self.assertEqual(ARTICLE_ID_PUB_ID_TYPE, article_id_pub_id_type)

    article_id_text = article_id.text
    self.assertIsNotNone(article_id_text)
    self.assertEqual(str(article.pk), article_id_text)


def validate_article_meta_counts(self: TestCase, article_meta: etree.ElementTree, article: Article) -> None:
    """
    Validates the article metadata associated with the figures.
    :param self: The testing object.
    :param article_meta: The article meta to check.
    :param article: The article to verify against.
    """
    counts = article_meta.find("counts")
    self.assertIsNotNone(counts)

    fig_count = counts.find("fig-count")
    self.assertIsNotNone(fig_count)

    fig_count_count = fig_count.get("count")
    self.assertIsNotNone(fig_count_count)
    self.assertEqual(str(article.data_figure_files.count()), fig_count_count)
