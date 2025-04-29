from b_2j import CagStatistics_2

class TestContentSerials:

    def test_content_serials(self, page=0, size=1):
        cag_statistics_object = CagStatistics_2(page=page, size=size)
        get_xml_all_content = cag_statistics_object.get_all_content_serials()
        cag_statistics_object.get_pages_serials()
        assert not len(cag_statistics_object.list_serials_id_bad), "There is non-working content. Check the results folder"
        assert not len(cag_statistics_object.list_seasons_id_bad), "There is non-working content. Check the results folder"
        assert not len(cag_statistics_object.list_serias_id_bad), "There is non-working content. Check the results folder"
