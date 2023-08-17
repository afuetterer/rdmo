import xml.etree.ElementTree as et

from django.urls import reverse

import pytest

from ..models import View

users = (
    ('editor', 'editor'),
    ('reviewer', 'reviewer'),
    ('user', 'user'),
    ('api', 'api'),
    ('anonymous', None),
)

status_map = {
    'list': {'editor': 200, 'reviewer': 200, 'api': 200, 'user': 403, 'anonymous': 401},
    'detail': {'editor': 200, 'reviewer': 200, 'api': 200, 'user': 403, 'anonymous': 401},
    'create': {'editor': 201, 'reviewer': 403, 'api': 201, 'user': 403, 'anonymous': 401},
    'update': {'editor': 200, 'reviewer': 403, 'api': 200, 'user': 403, 'anonymous': 401},
    'delete': {'editor': 204, 'reviewer': 403, 'api': 204, 'user': 403, 'anonymous': 401},
}

urlnames = {
    'list': 'v1-views:view-list',
    'index': 'v1-views:view-index',
    'export': 'v1-views:view-export',
    'detail': 'v1-views:view-detail',
    'detail_export': 'v1-views:view-detail-export',
    'copy': 'v1-views:view-copy',
}


@pytest.mark.parametrize('username,password', users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()


@pytest.mark.parametrize('username,password', users)
def test_index(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['index'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()


@pytest.mark.parametrize('username,password', users)
def test_export(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['export'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.content

    if response.status_code == 200:
        root = et.fromstring(response.content)
        assert root.tag == 'rdmo'
        for child in root:
            assert child.tag in ['view']


@pytest.mark.parametrize('username,password', users)
def test_detail(db, client, username, password):
    client.login(username=username, password=password)
    instances = View.objects.all()

    for instance in instances:
        url = reverse(urlnames['detail'], args=[instance.pk])
        response = client.get(url)
        assert response.status_code == status_map['detail'][username], response.json()


@pytest.mark.parametrize('username,password', users)
def test_create(db, client, username, password):
    client.login(username=username, password=password)
    instances = View.objects.all()

    for instance in instances:
        url = reverse(urlnames['list'])
        data = {
            'uri_prefix': instance.uri_prefix,
            'key': f'{instance.key}_new_{username}',
            'comment': instance.comment,
            'template': instance.template,
            'title_en': instance.title_lang1,
            'title_de': instance.title_lang2,
            'help_en': instance.help_lang1,
            'help_de': instance.help_lang2,
        }
        response = client.post(url, data)
        assert response.status_code == status_map['create'][username], response.json()


@pytest.mark.parametrize('username,password', users)
def test_update(db, client, username, password):
    client.login(username=username, password=password)
    instances = View.objects.all()

    for instance in instances:
        url = reverse(urlnames['detail'], args=[instance.pk])
        data = {
            'uri_prefix': instance.uri_prefix,
            'key': instance.key,
            'comment': instance.comment,
            'template': instance.template,
            'title_en': instance.title_lang1,
            'title_de': instance.title_lang2,
            'help_en': instance.help_lang1,
            'help_de': instance.help_lang2,
        }
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == status_map['update'][username], response.json()


@pytest.mark.parametrize('username,password', users)
def test_delete(db, client, username, password):
    client.login(username=username, password=password)
    instances = View.objects.all()

    for instance in instances:
        url = reverse(urlnames['detail'], args=[instance.pk])
        response = client.delete(url)
        assert response.status_code == status_map['delete'][username], response.json()


@pytest.mark.parametrize('username,password', users)
def test_detail_export(db, client, username, password):
    client.login(username=username, password=password)
    instances = View.objects.all()

    for instance in instances:
        url = reverse(urlnames['detail_export'], args=[instance.pk])
        response = client.get(url)
        assert response.status_code == status_map['list'][username], response.content

        if response.status_code == 200:
            root = et.fromstring(response.content)
            assert root.tag == 'rdmo'
            for child in root:
                assert child.tag in ['view']


@pytest.mark.parametrize('username,password', users)
def test_copy(db, client, username, password):
    client.login(username=username, password=password)
    instances = View.objects.all()

    for instance in instances:
        url = reverse(urlnames['copy'], args=[instance.pk])
        data = {'uri_prefix': instance.uri_prefix + '-', 'key': instance.key + '-'}
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == status_map['create'][username], response.json()


@pytest.mark.parametrize('username,password', users)
def test_copy_wrong(db, client, username, password):
    client.login(username=username, password=password)
    instance = View.objects.first()

    url = reverse(urlnames['copy'], args=[instance.pk])
    data = {'uri_prefix': instance.uri_prefix, 'key': instance.key}
    response = client.put(url, data, content_type='application/json')

    if status_map['create'][username] == 201:
        assert response.status_code == 400, response.json()
    else:
        assert response.status_code == status_map['create'][username], response.json()
