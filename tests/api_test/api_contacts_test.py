from datetime import date


contact_data = {"first_name": "name",
                "second_name": "second name",
                "email": "email@example.com",
                "phone_number": "+38052047329",
                "birthday": date.today().isoformat(), }
contact_data_update = {"first_name": "Andrew",
                       "second_name": "second name",
                       "email": "email@example.com",
                       "phone_number": "+38052047329",
                       "birthday": date.today().isoformat(), }

def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == contact_data.get("first_name")
    assert "id" in data


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == contact_data.get("first_name")
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == contact_data.get("first_name")
    assert "id" in data[0]


def test_update_contact(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json=contact_data_update,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == contact_data_update.get("first_name")
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contacts/2",
        json={"first_name": "Andrew"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == contact_data_update.get("first_name")
    assert "id" in data


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
