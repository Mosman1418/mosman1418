import unittest
import retrieve
import utilities
import datetime


class TestSeriesFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = retrieve.RSSeriesClient()

    def test_get_identifier(self):
        identifier = self.rs.get_identifier('A1')
        self.assertEqual(identifier, 'A1')

    def test_get_title(self):
        test_title = (
            'Correspondence files, annual single number series '
            '[Main correspondence files series of the agency]'
            )
        title = self.rs.get_title('A1')
        self.assertEqual(title, test_title)

    def test_get_accumulation_dates(self):
        test_dates = {
                'date_str': '01 Jan 1903 - 31 Dec 1938',
                'start_date': {
                        'date': datetime.datetime(1903, 1, 1, 0, 0),
                        'day': True,
                        'month': True
                    },
                'end_date': {
                        'date': datetime.datetime(1938, 12, 31, 0, 0),
                        'day': True,
                        'month': True
                    }
                }
        accumulation_dates = self.rs.get_accumulation_dates('A1')
        self.assertEqual(accumulation_dates, test_dates)

    def test_get_contents_dates(self):
        test_dates = {
                'date_str': '01 Jan 1890 - 31 Dec 1969',
                'start_date': {
                        'date': datetime.datetime(1890, 1, 1, 0, 0),
                        'day': True,
                        'month': True
                    },
                'end_date': {
                        'date': datetime.datetime(1969, 12, 31, 0, 0),
                        'day': True,
                        'month': True
                    }
                }
        contents_dates = self.rs.get_contents_dates('A1')
        self.assertEqual(contents_dates, test_dates)

    def test_get_number_described(self):
        results = {
            'described_note': 'All items from this series are entered on RecordSearch.',
            'described_number': '64439'
        }
        items_described = self.rs.get_number_described('A1')
        self.assertEqual(items_described, results)


class TestItemFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = retrieve.RSItemClient()

    def test_get_title(self):
        test_title = (
                'WRAGGE Clement Lionel Egerton : SERN 647 : '
                'POB Cheadle England : POE Enoggera QLD : '
                'NOK  (Father) WRAGGE Clement Lindley'
            )
        title = self.rs.get_title('3445411')
        self.assertEqual(title, test_title)

    def test_get_digitised_pages(self):
        pages = self.rs.get_digitised_pages('3445411')
        self.assertEqual(pages, '47')


class TestUtilityFunctions(unittest.TestCase):

    def test_process_date(self):
        cases = [
                    ('2 June 1884', [{'date': datetime.datetime(1884, 6, 2), 'day': True, 'month': True}]),
                    ('03 Jul 1921', [{'date': datetime.datetime(1921, 7, 3), 'day': True, 'month': True}]),
                    ('13 Jul. 1921', [{'date': datetime.datetime(1921, 7, 13), 'day': True, 'month': True}]),
                    ('Dec 1778', [{'date': datetime.datetime(1778, 12, 1), 'day': False, 'month': True}]),
                    ('1962', [{'date': datetime.datetime(1962, 1, 1), 'day': False, 'month': False}]),
                    ('2 June 1884 - Sep 1884',
                        [
                            {'date': datetime.datetime(1884, 6, 2), 'day': True, 'month': True},
                            {'date': datetime.datetime(1884, 9, 1), 'day': False, 'month': True},
                        ]
                    ),
                ]
        for case in cases:
            self.assertEqual(utilities.process_date_string(case[0]), case[1])

    def test_convert_date_to_iso(self):
        cases = [
                    ({'date': datetime.datetime(1884, 6, 2), 'day': True, 'month': True}, '1884-06-02'),
                    ({'date': datetime.datetime(1778, 12, 1), 'day': False, 'month': True}, '1778-12'),
                    ({'date': datetime.datetime(1962, 1, 1), 'day': False, 'month': False}, '1962'),
                ]
        for case in cases:
            self.assertEqual(utilities.convert_date_to_iso(case[0]), case[1])

if __name__ == '__main__':
    unittest.main()
