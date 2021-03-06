from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.template import loader
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from . import models
from .conf import settings
from filer.models.imagemodels import Image


class FilerFolderPlugin(CMSPluginBase):
    module = 'Filer'
    model = models.FilerFolder
    name = _("Folder")
    TEMPLATE_NAME = 'cmsplugin_filer_folder/plugins/folder/%s.html'
    render_template = TEMPLATE_NAME % 'default'
    text_enabled = False
    admin_preview = False

    fieldsets = (
        (None, {'fields': ['title', 'folder']}),
    )
    if settings.CMSPLUGIN_FILER_FOLDER_STYLE_CHOICES:
        fieldsets[0][1]['fields'].append('style')

    def get_folder_files(self, folder, user):
        qs_files = folder.files.filter(image__isnull=True)
        if user.is_staff:
            return qs_files
        else:
            return qs_files.filter(is_public=True)

    def get_folder_images(self, folder, user):
        qs_files = folder.files.instance_of(Image)
        if user.is_staff:
            return qs_files
        else:
            return qs_files.filter(is_public=True)

    def get_children(self, folder):
        return folder.get_children()

    def render(self, context, instance, placeholder):
        self.render_template = select_template((
            'cmsplugin_filer_folder/folder.html',  # backwards compatibility. deprecated!
            self.TEMPLATE_NAME % instance.style,
            self.TEMPLATE_NAME % 'default')
        ).template

        folder_files = self.get_folder_files(instance.folder,
                                             context['request'].user)
        folder_images = self.get_folder_images(instance.folder,
                                               context['request'].user)
        folder_folders = self.get_children(instance.folder)

        context.update({
            'object': instance,
            'folder_files': sorted(folder_files),
            'folder_images': sorted(folder_images),
            'folder_folders': folder_folders,
            'placeholder': placeholder
        })
        return context



plugin_pool.register_plugin(FilerFolderPlugin)
