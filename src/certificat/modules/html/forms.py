from django import forms
from django.db import models, transaction
from certificat.modules.acme import models as db
from certificat.settings.dynamic import ApplicationSettings
import inject


class BindingScopePersonalOnly(models.TextChoices):
    Personal = "1"


class BindingScope(models.TextChoices):
    Personal = "1"
    Group = "2"


class NewBindingForm(forms.Form):
    settings: ApplicationSettings = inject.attr(ApplicationSettings)
    scope = forms.ChoiceField(
        label="Access",
        widget=forms.RadioSelect,
        choices=BindingScope.choices,
        initial=BindingScope.Personal,
    )
    group = forms.ChoiceField(widget=forms.Select, required=False)
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Account name...", "autocomplete": "off"}
        ),
        max_length=100,
    )
    note = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Notes describing account usage..."}
        ),
        max_length=255,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_groups_choices = [(g.id, g.name) for g in user.groups.order_by("name")]
        self.fields["group"].choices = user_groups_choices

        if len(user_groups_choices) == 0:
            self.fields["scope"].choices = BindingScopePersonalOnly.choices

    def clean(self):
        data = self.cleaned_data
        scope = data.get("scope")
        if scope == BindingScope.Group:
            if data.get("group") is None or data.get("group") == "":
                raise forms.ValidationError("Group name is required")

        return data

    def save(self, request) -> db.AccountBinding:
        with transaction.atomic():
            note = self.cleaned_data["note"]
            name = self.cleaned_data["name"]
            binding = db.AccountBinding.generate(request.user, name, note)

            if self.cleaned_data["scope"] == BindingScope.Group:
                group = request.user.groups.get(id=self.cleaned_data["group"])
                db.AccountBindingGroupScope(binding=binding, group=group).save()

            return binding


class UsageEditForm(forms.Form):
    usage = forms.CharField(widget=forms.Textarea())

    def save(self, request) -> db.Usage:
        return db.Usage.objects.create(text=self.cleaned_data["usage"])
