from unittest import TestCase
from inzerator.bazos.rss import AuthorDataParser, AuthorData, AuthorValidator

from os import path

basepath = path.dirname(__file__)
filepath = path.abspath(path.join(basepath, "invalid_author.html"))


LISTING_URLS = [
    'https://reality.bazos.sk/inzerat/143032833/kpt-nalepku-3-izb-prazsky-typ-6-m-loggia-kosice-stare-mesto.php',
    'https://reality.bazos.sk/inzerat/143025816/muskatova-ul-15-izb-byt-kosice-zapad-terasa-5-posch.php',
    'https://reality.bazos.sk/inzerat/143025269/priestranny-4-izb-byt-82-m2-loggia-bukurestska-ul-kosice.php',
    'https://reality.bazos.sk/inzerat/143026375/rodinny-dom-8-km-od-kosic-vajkovce-okres-kosice-okolie.php',
    'https://reality.bazos.sk/inzerat/142533898/2-izb-byt-so-6-m-loggiou-9-posch-kosice.php',
    'https://reality.bazos.sk/inzerat/142823475/3-izb-byt-so-6-m-logiou-po-kompletnej-rekonstrukcii-maurerova-ul-kosic.php',
    'https://reality.bazos.sk/inzerat/142260284/tatranska-ul-3-izb-byt-s-loggiou-3-posch-74-m2-kosice-stare-mesto.php',
    'https://reality.bazos.sk/inzerat/142262921/2-izb-byt-s-loggiou-4posch-viedenska-ul-kosice-ov.php',
    'https://reality.bazos.sk/inzerat/142155382/terasa-3-izb-prazsky-typ-6-m-loggia-kysucka-ul-kosice-zapad.php',
    'https://reality.bazos.sk/inzerat/142825330/prenajom-3-izb-byt-s-loggiou-tatranska-ul-74-m2-kosice-stare-mesto.php',
    'https://reality.bazos.sk/inzerat/142263858/prenajom-2-izb-zariadeny-byt-popradska-ul-kosice-zapad-terasa.php',
    'https://reality.bazos.sk/inzerat/141719075/2-izb-tehlovy-byt-po-rekonstrukcii-kosice-stare-mesto-zimna-ul.php',
    'https://reality.bazos.sk/inzerat/141718834/muskatova-ul-15-izb-byt-kosice-zapad-terasa-5posch.php',
    'https://reality.bazos.sk/inzerat/142087646/rodinny-dom-ulica-kupeckeho-kosice-juh.php',
    'https://reality.bazos.sk/inzerat/142189692/rodinny-dom-iba-8-km-od-kosic-vajkovce-okres-kosice-okolie.php',
    'https://reality.bazos.sk/inzerat/142153347/rodinny-dom-na-prenajom-novostavba-4-izby-kosice-krasna.php',
    'https://reality.bazos.sk/inzerat/141700328/prenajom-luxusne-zariadeneho-rodinneho-domu-kosice.php']


class AuthorParserTest(TestCase):

    def test_valid(self):
        parser = AuthorDataParser()
        with open(filepath) as f:
            result = parser.parse(f.read(), "aaa")
            expected = AuthorData('Ing. Jožko Mrkvička', 17, LISTING_URLS,
                                  "aaa")
            self.assertEqual(result, expected)

    def test_name_validation(self):
        validator = AuthorValidator(3)
        self.assertTrue(validator.validate_name("aaa"))
        self.assertTrue(validator.validate_name("aaaaaa"))
        self.assertTrue(validator.validate_name("aaa aaa"))
        self.assertTrue(validator.validate_name("Jozko Mrkvicka"))
        self.assertTrue(validator.validate_name("Ing. Jožko Mrkvička"))
        self.assertFalse(validator.validate_name("aaaBBBaaa"))
        self.assertFalse(validator.validate_name("moja realitka neviem"))
        self.assertFalse(validator.validate_name("moja Realitka neviem"))
        self.assertFalse(validator.validate_name("moja s.r.o"))
        self.assertFalse(validator.validate_name("moja s.r.o."))
        self.assertFalse(validator.validate_name("moja S.R.O."))

    def test_url_validation(self):
        validator = AuthorValidator(3)
        self.assertFalse(validator.validate_listings(LISTING_URLS))
        self.assertFalse(validator.validate_listings(LISTING_URLS[:3]))
        self.assertTrue(validator.validate_listings([LISTING_URLS[0]]))
        self.assertTrue(validator.validate_listings(["https://stroje.bazos.sk/inzerat/141700328/aaa.php", LISTING_URLS[0], "https://elektro.bazos.sk/inzerat/141700328/aaa.php", "https://pc.bazos.sk/inzerat/141700328/bbb.php", "https://hudba.bazos.sk/inzerat/141700328/aaa.php"]))
        self.assertTrue(validator.validate_listings(["https://stroje.bazos.sk/inzerat/141700328/aaa.php", *LISTING_URLS[:2], "https://elektro.bazos.sk/inzerat/141700328/aaa.php", "https://pc.bazos.sk/inzerat/141700328/bbb.php", "https://hudba.bazos.sk/inzerat/141700328/aaa.php"]))
