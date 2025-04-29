from b_1 import CagStatistics

class TestContent:
    def test_content(self, page=0, size=1):
        cag_statistics_object = CagStatistics(page=page, size=size)

        cag_statistics_object.get_pages()
        assert not len(cag_statistics_object.list_films_id_bad), "There is non-working content"



        cag_statistics_object.get_pages_serials()
        assert not len(cag_statistics_object.list_serials_id_bad), \
            "There is non-working content. Check the results folder"
        assert not len(cag_statistics_object.list_seasons_id_bad), \
            "There is non-working content. Check the results folder"
        assert not len(cag_statistics_object.list_serias_id_bad),\
            "There is non-working content. Check the results folder"