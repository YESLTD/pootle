# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from django.utils.translation import get_language
from django.urls import reverse

from pootle.core.delegate import revision
from pootle_app.views.index.index import (
    COOKIE_NAME, IndexView, WelcomeView)
from pootle_score.display import TopScoreDisplay


@pytest.mark.django_db
def test_view_index(client, rf, request_users, language0):
    user = request_users["user"]
    client.login(
        username=user.username,
        password=request_users["password"])
    response = client.get("")
    if not user.is_authenticated:
        assert response.status_code == 200
        assert isinstance(response.context["view"], WelcomeView)
    else:
        assert response.status_code == 302
        assert response["Location"] == reverse("pootle-projects-browse")

    request = rf.get("")
    request.user = user
    request.COOKIES[COOKIE_NAME] = language0.code
    response = IndexView.as_view()(request=request)
    if not user.is_authenticated:
        assert response.status_code == 200
    else:
        assert response.status_code == 302
        assert response["Location"] == reverse(
            "pootle-language-browse",
            kwargs=dict(language_code=language0.code))


@pytest.mark.django_db
def test_view_welcome(client, member, system, project_set):
    response = client.get(reverse('pootle-home'))
    assert isinstance(response.context["top_scorers"], TopScoreDisplay)
    assert isinstance(response.context["view"], WelcomeView)
    assert response.context["view"].request_lang == get_language()
    assert (
        response.context["view"].project_set.directory
        == project_set.directory)
    assert (
        response.context["view"].revision
        == revision.get(project_set.directory.__class__)(
            project_set.directory).get(key="stats"))
    assert (
        response.context["view"].cache_key
        == (
            "%s.%s.%s"
            % (response.wsgi_request.user.username,
               response.context["view"].revision,
               get_language())))
