import requests


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    @property
    def headers(self) -> dict:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    @staticmethod
    def _raise_for_response(response: requests.Response) -> None:
        if response.ok:
            return
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        if isinstance(detail, list):
            detail = "; ".join(str(item) for item in detail)
        raise ApiError(str(detail), response.status_code)

    def login(self, email: str, password: str) -> dict:
        response = requests.post(
            f"{self.base_url}/token",
            data={
                "grant_type": "password",
                "username": email.strip(),
                "password": password,
            },
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def change_password(self, old_password: str, new_password: str) -> dict:
        response = requests.post(
            f"{self.base_url}/change-password",
            json={"old_password": old_password, "new_password": new_password},
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def health_check(self) -> bool:
        response = requests.get(f"{self.base_url}/docs", timeout=2)
        return response.status_code == 200

    # ---------- Users ----------
    def list_users(self) -> list:
        response = requests.get(
            f"{self.base_url}/users",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def create_user(self, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/users",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def delete_user(self, user_id: int) -> dict:
        response = requests.delete(
            f"{self.base_url}/users/{user_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    # ---------- KPI ----------
    def get_kpi_lots(self, product_id: int | None = None) -> list:
        params = {"product_id": product_id} if product_id else {}
        response = requests.get(
            f"{self.base_url}/kpis/lots",
            params=params,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def get_kpi_analytics(self, fourniture_id: int) -> dict:
        response = requests.get(
            f"{self.base_url}/kpis/analytics/{fourniture_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    # ---------- Products ----------
    def list_products(self) -> list:
        response = requests.get(
            f"{self.base_url}/products",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def get_product(self, product_id: int) -> dict:
        response = requests.get(
            f"{self.base_url}/products/{product_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def create_product(self, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/products",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def update_product(self, product_id: int, payload: dict) -> dict:
        response = requests.put(
            f"{self.base_url}/products/{product_id}",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def delete_product(self, product_id: int) -> dict:
        response = requests.delete(
            f"{self.base_url}/products/{product_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    # ---------- Fournitures ----------
    def list_fournitures(self) -> list:
        response = requests.get(
            f"{self.base_url}/fournitures",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def get_fourniture(self, fourniture_id: int) -> dict:
        response = requests.get(
            f"{self.base_url}/fournitures/{fourniture_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def create_fourniture(self, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/fournitures",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def update_fourniture(self, fourniture_id: int, payload: dict) -> dict:
        response = requests.put(
            f"{self.base_url}/fournitures/{fourniture_id}",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def delete_fourniture(self, fourniture_id: int) -> dict:
        response = requests.delete(
            f"{self.base_url}/fournitures/{fourniture_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    # ---------- Ventes ----------
    def list_ventes(self) -> list:
        response = requests.get(
            f"{self.base_url}/ventes",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def get_vente(self, vente_id: int) -> dict:
        response = requests.get(
            f"{self.base_url}/ventes/{vente_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def create_vente(self, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/ventes",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def update_vente(self, vente_id: int, payload: dict) -> dict:
        response = requests.put(
            f"{self.base_url}/ventes/{vente_id}",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def delete_vente(self, vente_id: int) -> dict:
        response = requests.delete(
            f"{self.base_url}/ventes/{vente_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    # ---------- Commandes Retour ----------
    def list_commandes_retour(self) -> list:
        response = requests.get(
            f"{self.base_url}/commandes-retour",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def get_commande_retour(self, retour_id: int) -> dict:
        response = requests.get(
            f"{self.base_url}/commandes-retour/{retour_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def create_commande_retour(self, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/commandes-retour",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def update_commande_retour(self, retour_id: int, payload: dict) -> dict:
        response = requests.put(
            f"{self.base_url}/commandes-retour/{retour_id}",
            json=payload,
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()

    def delete_commande_retour(self, retour_id: int) -> dict:
        response = requests.delete(
            f"{self.base_url}/commandes-retour/{retour_id}",
            headers=self.headers,
            timeout=5,
        )
        self._raise_for_response(response)
        return response.json()
