import pytest
from django.urls import reverse

from pythonpro.leads.models import Lead


@pytest.fixture()
def new_resp(client):
    return client.post(
        reverse('leads:new'),
        {
            'name': 'Renzo',
            'email': 'renzo@python.pro.br'
        }
    )


@pytest.mark.django_db(transaction=True)
def test_new_lead_status(new_resp):
    assert 302 == new_resp.status_code


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("new_resp")
def test_saved_lead():
    assert Lead.objects.exists()


@pytest.fixture()
def blank_resp(client):
    return client.post(
        reverse('leads:new'),
        {
            'name': '',
            'email': ''
        }
    )


@pytest.mark.django_db(transaction=True)
def test_error_status(blank_resp):
    assert 200 == blank_resp.status_code


@pytest.mark.parametrize(
    'form_content',
    [
        '<form action="." method="post"',
        '<input type="text" name="name"',
        '<input type="email" name="email"',
        '<button type="submit"'
    ]
)
def test_lead_form(form_content, dj_assert_contains, blank_resp):
    dj_assert_contains(blank_resp, form_content)


def test_lead_error_msgs(dj_assert_contains, blank_resp):
    dj_assert_contains(blank_resp, 'Este campo é obrigatório.', 2)


@pytest.mark.django_db(transaction=True)
def test_dup_not_revealed(client):
    """Duplicates would expose what emails are already on lead database. It's better not sharing this info"""
    new_resp(client)
    dup_resp = new_resp(client)
    assert 302 == dup_resp.status_code
