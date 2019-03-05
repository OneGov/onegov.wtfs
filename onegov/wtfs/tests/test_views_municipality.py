from onegov.core.request import CoreRequest
from unittest.mock import patch
from webtest.forms import Upload


def test_views_municipality(client):
    client.login_admin()

    # Add groups
    add = client.get('/user-groups').click(href='add')
    add.form['name'] = "Gruppe Adlikon"
    assert "Benutzergruppe hinzugefügt." in add.form.submit().follow()

    add = client.get('/user-groups').click(href='add')
    add.form['name'] = "Gruppe Aesch"
    assert "Benutzergruppe hinzugefügt." in add.form.submit().follow()

    # Add a municipality
    add = client.get('/municipalities').click(href='add')
    add.form['name'] = "Gemeinde Adlikon"
    add.form['bfs_number'] = '21'
    add.form['group_id'].select(text="Gruppe Adlikon")
    added = add.form.submit().follow()
    assert "Gemeinde hinzugefügt." in added
    assert "Gemeinde Adlikon" in added

    # View the municipality
    view = client.get('/municipalities').click("Gemeinde Adlikon")
    assert "Gemeinde Adlikon" in view
    assert "21" in view
    assert "Gruppe Adlikon" in view
    assert "7.0" in view

    # Edit the municipality
    edit = view.click("Bearbeiten")
    edit.form['name'] = "Gemeinde Aesch"
    edit.form['bfs_number'] = '241'
    edit.form['group_id'].select(text="Gruppe Aesch")
    edit.form['price_per_quantity'] = '21.25'
    edit.form['address_supplement'] = "Zusatz"
    edit.form['gpn_number'] = "12321"
    edited = edit.form.submit().follow()
    assert "Gemeinde geändert." in edited
    assert "Gemeinde Aesch" in edited
    view = edited.click("Gemeinde Aesch")
    assert "Gruppe Aesch" in view
    assert "21.25" in view
    assert "12321" in view

    # Upload some dates
    upload = client.get('/municipalities').click("Daten importieren")
    upload.form['file'] = Upload(
        'test.csv',
        "Gemeinde-Nr,Vordefinierte Termine\n241,12.2.2015".encode('utf-8'),
        'text/csv'
    )
    uploaded = upload.form.submit().follow()
    assert "Gemeindedaten importiert." in uploaded
    assert "12.02.2015" in client.get('/municipalities')\
        .click("Gemeinde Aesch")

    # Delete some dates
    clear = client.get('/municipalities').click("Gemeinde Aesch")\
        .click("Abholtermine löschen")
    cleared = clear.form.submit().follow()
    assert "Abholtermine gelöscht." in cleared
    assert "12.02.2015" not in client.get('/municipalities')\
        .click("Gemeinde Aesch")

    # Delete the municipality
    deleted = client.get('/municipalities').click("Gemeinde Aesch")\
        .click("Löschen")
    assert deleted.status_int == 200
    assert "Gemeinde Aesch" not in client.get('/municipalities')


@patch.object(CoreRequest, 'assert_valid_csrf_token')
def test_views_municipality_permissions(mock_method, client):
    client.login_admin()

    add = client.get('/municipalities').click(href='add')
    add.form['name'] = "Gemeinde Adlikon"
    add.form['bfs_number'] = '21'
    assert "Gemeinde hinzugefügt." in add.form.submit().follow()
    id = client.get('/municipalities')\
        .click("Gemeinde Adlikon").request.url.split('/')[-1]

    client.logout()

    urls = [
        '/municipalities',
        '/municipalities/add',
        f'/municipality/{id}',
        f'/municipality/{id}/edit'
    ]

    for url in urls:
        client.get(url, status=403)
    client.delete(f'/municipality/{id}', status=403)

    client.login_member()
    for url in urls:
        client.get(url, status=403)
    client.delete(f'/municipality/{id}', status=403)
    client.logout()

    client.login_editor()
    for url in urls:
        client.get(url, status=403)
    client.delete(f'/municipality/{id}', status=403)
    client.logout()

    client.login_admin()
    for url in urls:
        client.get(url)
    client.delete(f'/municipality/{id}')
    client.logout()
