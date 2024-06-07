import io
from string import Template
from typing import List, Union

import pytest

from django.core.management import CommandError, call_command

from rdmo.conditions.models import Condition
from rdmo.domain.models import Attribute
from rdmo.options.models import Option
from rdmo.questions.models import Page, Question, QuestionSet, Section
from rdmo.views.models import View

ElementType = Union[Section, Page, QuestionSet, Question, Option, Condition]

ATTRIBUTE_RELATED_MODELS_FIELDS = [i for i in Attribute._meta.get_fields() \
                  if i.is_relation and not i.many_to_many and i.related_model is not Attribute]

EXAMPLE_URI_PREFIX = 'http://example.com/terms'
foo_merge_uri_prefix = 'http://foo-merge.com/terms'
bar_merge_uri_prefix = 'http://bar-merge.com/terms'
EXAMPLE_VIEW_URI_PATH = "views/view_a"
merge_view_template_addition_uri_path = 'individual/single/textarea'
merge_view_template_addition = Template("{% render_value '$new_uri' %}")
EXAMPLE_VIEW_URI = Attribute.build_uri(EXAMPLE_URI_PREFIX, merge_view_template_addition_uri_path)
new_merge_uri_prefixes = [foo_merge_uri_prefix, bar_merge_uri_prefix]

def _prepare_instance_for_copy(instance, uri_prefix=None, uri_path=None):
    instance.pk = None
    instance.id = None
    instance._state.adding = True
    if uri_prefix:
        instance.uri_prefix = uri_prefix
    if uri_path:
        instance.uri_path = uri_path
    return instance

def _get_queryset(related_field, attribute=None):
    model = related_field.related_model
    if model is View:
        return model.objects.filter(**{"template__contains": attribute.path})
    lookup_field = related_field.remote_field.name
    return model.objects.filter(**{lookup_field: attribute})

def _add_new_line_to_view_template(instance: View, new_uri_prefix: str) -> View:
    current_field_value = instance.template
    new_field_value = current_field_value + "\n"
    new_uri = Attribute.build_uri(new_uri_prefix, merge_view_template_addition_uri_path)
    new_field_value += merge_view_template_addition.substitute(new_uri=new_uri)
    instance.template = new_field_value
    return instance

def create_copy_of_view_that_uses_new_attribute(new_prefixes: List[str]):
    # TODO search in View.template for the attribute uri
    # example_uri = f"{EXAMPLE_URI_PREFIX}/{EXAMPLE_VIEW_URI_PATH}"
    # source = Attribute.objects.get(uri=example_uri)
    qs = View.objects.filter(**{"template__contains": EXAMPLE_VIEW_URI_PATH})
    for new_prefix in new_prefixes:
        for instance in qs:
            instance = _prepare_instance_for_copy(instance)
            instance = _add_new_line_to_view_template(instance, new_prefix)
            instance.save()

def create_copies_of_related_models_with_new_uri_prefix(new_prefixes):
    for related_model_field in ATTRIBUTE_RELATED_MODELS_FIELDS:
        model = related_model_field.related_model
        lookup_field = related_model_field.remote_field.name
        # create new model instances from example.com objects with the new uri_prefix
        filter_kwargs = {f"{lookup_field}__uri_prefix": EXAMPLE_URI_PREFIX}
        example_objects = model.objects.filter(**filter_kwargs)

        for new_prefix in new_prefixes:

            if not example_objects:
                continue
            for instance in example_objects:
                instance = _prepare_instance_for_copy(instance, uri_prefix=new_prefix)
                current_attribute = getattr(instance, lookup_field)
                if not isinstance(current_attribute, Attribute):
                    continue
                filter_kwargs = {'path': current_attribute.path, 'uri_prefix': new_prefix}
                new_attribute = Attribute.objects.filter(**filter_kwargs).first()
                setattr(instance, lookup_field, new_attribute)
                instance.save()


def create_copies_of_attributes_with_new_uri_prefix(example_attributes, new_prefixes):
    for attribute in example_attributes:
        for new_prefix in new_prefixes:
            attribute = _prepare_instance_for_copy(attribute, uri_prefix=new_prefix)
            attribute.save()

def get_related_affected_instances(attribute) -> list:

    related_qs = []
    for related_field in ATTRIBUTE_RELATED_MODELS_FIELDS:
        model = related_field.related_model
        lookup_field = related_field.remote_field.name
        qs = model.objects.filter(**{lookup_field: attribute})
        related_qs.append(qs)
    return related_qs


@pytest.fixture
def create_merge_attributes(db, settings):
    """ Creates model instances for merge attributes tests """
    example_attributes = Attribute.objects.filter(uri_prefix=EXAMPLE_URI_PREFIX).all()
    create_copies_of_attributes_with_new_uri_prefix(example_attributes, new_merge_uri_prefixes)
    create_copies_of_related_models_with_new_uri_prefix(new_merge_uri_prefixes)
    create_copy_of_view_that_uses_new_attribute(new_merge_uri_prefixes)


@pytest.mark.parametrize('uri_prefix', new_merge_uri_prefixes)
def test_that_the_freshly_created_merge_attributes_are_present(create_merge_attributes, uri_prefix):
    merge_attributes = Attribute.objects.filter(uri_prefix=uri_prefix).all()
    assert len(merge_attributes) > 2
    unique_uri_prefixes = set(Attribute.objects.values_list("uri_prefix", flat=True))
    # test that the currently selected uri_prefix is in db
    assert uri_prefix in unique_uri_prefixes

    for attribute in merge_attributes:
        original_attribute = Attribute.objects.get(uri_prefix=EXAMPLE_URI_PREFIX, path=attribute.path)
        original_models_qs = [_get_queryset(i, attribute=original_attribute) for i in ATTRIBUTE_RELATED_MODELS_FIELDS]
        if not any(len(i) > 0 for i in original_models_qs):
            continue  # skip this attribute
        models_qs = [_get_queryset(i, attribute=attribute) for i in ATTRIBUTE_RELATED_MODELS_FIELDS]
        assert any(len(i) > 0 for i in models_qs)


@pytest.mark.parametrize('source_uri_prefix', new_merge_uri_prefixes)
@pytest.mark.parametrize('save', [False, True])
@pytest.mark.parametrize('delete', [False, True])
@pytest.mark.parametrize('view', [False, True])
def test_command_merge_attributes(create_merge_attributes, source_uri_prefix, save, delete, view):
    source_attributes = Attribute.objects.filter(uri_prefix=source_uri_prefix).all()
    assert len(source_attributes) > 2
    unique_uri_prefixes = set(Attribute.objects.values_list("uri_prefix", flat=True))
    # test that the currently selected uri_prefix is in db
    assert source_uri_prefix in unique_uri_prefixes

    for source_attribute in source_attributes:
        target_attribute = Attribute.objects.get(uri_prefix=EXAMPLE_URI_PREFIX, path=source_attribute.path)
        stdout, stderr = io.StringIO(), io.StringIO()
        before_source_related_qs = get_related_affected_instances(source_attribute)
        before_source_related_view_qs = View.objects.filter(**{"template__contains": source_attribute.path})
        # before_target_related_qs = get_related_affected_instances(target_attribute)

        command_kwargs = {'source': source_attribute.uri,
                          'target': target_attribute.uri,
                          'save': save, 'delete': delete, 'view': view}
        failed = False
        if source_attribute.get_descendants():
            with pytest.raises(CommandError):
                call_command('merge_attributes',
                             stdout=stdout, stderr=stderr, **command_kwargs)
            failed = True
        elif target_attribute.get_descendants():
            with pytest.raises(CommandError):
                call_command('merge_attributes',
                             stdout=stdout, stderr=stderr, **command_kwargs)
            failed = True
        else:
            call_command('merge_attributes',
                         stdout=stdout, stderr=stderr, **command_kwargs)


        if delete and not failed:
            # assert that the source attribut was deleted
            with pytest.raises(Attribute.DoesNotExist):
                Attribute.objects.get(id=source_attribute.id)
        else:
            assert Attribute.objects.get(id=source_attribute.id)

        after_source_related_qs = get_related_affected_instances(source_attribute)
        after_source_related_view_qs = View.objects.filter(**{"template__contains": source_attribute.path})
        after_target_related_qs = get_related_affected_instances(target_attribute)
        # after_target_related_view_qs = View.objects.filter(**{"template__contains": target_attribute.path})

        if save and not failed:

            if any(i.exists() for i in before_source_related_qs):
                assert not any(i.exists() for i in after_source_related_qs)
                assert any(i.exists() for i in after_target_related_qs)

            if source_attribute.path in merge_view_template_addition_uri_path:
                # assert that the attribute in the view template was replaced as well
                # the EXAMPLE_VIEW_URI is from the target attribute
                # uri_prefix = source_uri_prefix, uri_path = EXAMPLE_VIEW_URI_PATH
                if before_source_related_view_qs.exists():
                    if view and source_attribute.path != target_attribute.path:
                        assert not after_source_related_view_qs.exists()
                        for instance in after_source_related_view_qs:
                            assert any(target_attribute.path in i for i in instance.template.splitlines())
                            assert not any(source_attribute.path in i for i in instance.template.splitlines())
                    else:
                        assert after_source_related_view_qs.exists()

        else:
            if any(i.exists() for i in before_source_related_qs):
                assert any(i.exists() for i in after_source_related_qs)
