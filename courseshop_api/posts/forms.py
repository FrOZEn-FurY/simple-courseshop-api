from django import forms

from ckeditor.widgets import CKEditorWidget

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'body': CKEditorWidget
        }


class PostDataAdminFormset(forms.models.BaseInlineFormSet):
    def clean(self) -> None:
        try:
            for form in self.forms:
                if form.cleaned_data['file_type'] == 'P' and not form.cleaned_data['file']:
                    raise forms.ValidationError("When file_type is set to picture, a picture file must be procided.")
                elif form.cleaned_data['file_type'] == 'V' and not form.cleaned_data['video_url']:
                    raise forms.ValidationError("When file_type is set to video, a video url must be procided.")
                elif form.cleaned_data['file'] and form.cleaned_data['video_url']:
                    raise forms.ValidationError("Can't assign both video_url and picture file.")
        except AttributeError:
            pass