from django import forms
from hc.api.models import Channel
from ckeditor.fields import RichTextField
from hc.front.models import Category, Blog, Comment, FrequentlyAskedQuestion


class NameTagsForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    tags = forms.CharField(max_length=500, required=False)

    def clean_tags(self):
        l = []

        for part in self.cleaned_data["tags"].split(" "):
            part = part.strip()
            if part != "":
                l.append(part)

        return " ".join(l)


class TimeoutForm(forms.Form):
    timeout = forms.IntegerField(min_value=60, max_value=31104000)
    grace = forms.IntegerField(min_value=60, max_value=31104000)


class AddChannelForm(forms.ModelForm):

    class Meta:
        model = Channel
        fields = ['kind', 'value']

    def clean_value(self):
        value = self.cleaned_data["value"]
        return value.strip()


class AddWebhookForm(forms.Form):
    error_css_class = "has-error"

    value_down = forms.URLField(max_length=1000, required=False)
    value_up = forms.URLField(max_length=1000, required=False)

    def get_value(self):
        return "{value_down}\n{value_up}".format(**self.cleaned_data)

class AddCategoryForm(forms.Form):
    category = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(AddCategoryForm, self).clean()
        category = cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('category name required!')
    
    class Meta:
        model = Category
        fields = ['category']

class AddBlogForm(forms.ModelForm):

    title = forms.CharField(max_length=100)
    category = forms.ModelChoiceField(Category.objects.all())
    body = RichTextField()
    def clean(self):
        cleaned_data = super(AddBlogForm, self).clean()
        title = cleaned_data.get('title')
        body = cleaned_data.get('body')
        if not title and not body:
            raise forms.ValidationError('Fill in all fields')

    class Meta:
        model = Blog
        fields = ['title','category','body']



class AddCommentForm(forms.Form):
    comment = forms.CharField(max_length=4000,
                           widget=forms.Textarea(),
                           help_text="write comment here!")    
    def clean(self):
        cleaned_data = super(AddCommentForm, self).clean()
        comment = cleaned_data.get('comment')
        if not comment:
            raise forms.ValidationError('Fill in all fields')

    class Meta:
        model = Comment
        fields = ['comment']

class FaqForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FaqForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['question'].required = True
    class Meta:
        model = FrequentlyAskedQuestion
        fields = ('email', 'question')
