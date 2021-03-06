# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django.db.models.signals import post_save
from django.dispatch import receiver

from pootle.core.delegate import terminology
from pootle_store.constants import TRANSLATED
from pootle_store.models import Unit
from pootle_statistics.models import Submission, SubmissionFields


@receiver(post_save, sender=Submission)
def handle_unit_save(**kwargs):
    sub = kwargs["instance"]
    if sub.type != SubmissionFields.TARGET:
        return
    unit = sub.unit
    if unit.state != TRANSLATED:
        return
    is_terminology = (
        unit.store.name.startswith("pootle-terminology")
        or (unit.store.translation_project.project.code
            == "terminology"))
    if not is_terminology:
        return
    terminology.get(Unit)(unit).stem()
