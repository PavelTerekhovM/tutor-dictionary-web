import xml.etree.ElementTree as ET
from _elementtree import ParseError

from slugify import slugify

from dictionary.models import Word


class XmlParser:
    """
    Parser uploaded xml dictionaries, to validate file and
    create new dictionary instance:
        - take parts of file in for-cycle  and add them
        in byte-string
        - find title of dictionary-file, create a new
        instance of dictionary
        - parse byte-string and find all cards, take words,
        translations and examples
        - create new instance of words for each card
        - assign all new word instances to the created dictionary
    """
    def xml(self, obj=None):
        try:
            file = b''
            for line in self.uploaded_file:
                file += line
            tree = ET.ElementTree(ET.fromstring(file))
            root = tree.getroot()
            cards = [card for card in root.iter('card')]
            if not obj:
                return None if not cards else self.uploaded_file

            # find name of file or set default "Без имени"
            title = root.attrib.get('title', 'Без имени')
            obj.title = title or 'Без имени'
            obj.slug = slugify(obj.title)
            # otherwise can't add many-to-many objects
            obj.save()

            for card in cards:
                # need to clean variable from value of previous card
                example = ''
                for translations in card.iter('translations'):
                    # find translation of word
                    translations = translations.find('word').text
                for word in card.iter('word'):
                    if word.attrib:
                        body = word.text  # find text of word
                        slug = slugify(body)
                for example in card.iter('example'):
                    example = example.text  # find example of word

                # create and save new word in DB
                new_word = Word.objects.create(
                    body=body,
                    slug=slug,
                    translations=translations,
                    example=example)
                new_word.save()
                obj.word.add(new_word)
            obj.save()
            return obj

        except ParseError:
            return None


class CsvParser:
    """
    Parser uploaded csv dictionaries.
    NOT IMPLEMENTED
    """
    def csv(self, obj=None):
        return None


class DictionaryFileManager(XmlParser, CsvParser):
    """
    Class responsible to clean and save dictionary uploaded to site.
    get_handler() - dispatch which method should parse file
    clean_file() and parse_file() interfaces provided to form.save()
    """
    allowed_extension = ['xml', 'csv']

    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file

    def get_handler(self):
        extension = self.uploaded_file.name.split(".")[-1].lower()
        if extension in self.allowed_extension:
            return getattr(self, extension, None)
        return None

    def clean_file(self):
        handler = self.get_handler()
        if handler:
            if handler():
                return self.uploaded_file
        return None

    def parse_file(self, obj=None):
        handler = self.get_handler()
        if handler:
            return handler(obj)
        return None
