from fastapi.testclient import TestClient

from fhelp.ftest import BaseFastApiTest
from settings import SettingsFastApi

settings = SettingsFastApi()


class TestMainApp(BaseFastApiTest):
    fixtures = [settings.BASE_DIR / "fixtures" / "test_base.json"]

    def setup_method(self):
        super().setup_method()

    def test_read_main(self, client: TestClient):
        excepted_response = [
            {
                "username": "2Petro",
                "email_user": "2Petro@google.com",
                "snils": "1231121245",
                "level": 1,
                "id": 2,
            },
            {
                "username": "Иванов",
                "email_user": "3Gongo@google.com",
                "snils": "453514",
                "level": 3,
                "id": 3,
            },
        ]
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == excepted_response

        response2 = client.get("/async_test")
        assert response2.status_code == 200
        assert response.json() == excepted_response
