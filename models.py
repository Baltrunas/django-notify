from __future__ import unicode_literals
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models


class Notify(models.Model):
	name = models.CharField(_('Name'), max_length=128)
	description = models.TextField(_('Description'), blank=True, null=True)
	content_type = models.ManyToManyField(ContentType, verbose_name=_('Models'))

	BACKEND = (
		('apps.notify.tests.console', _('Console')),
		('helpful.easy_email.mail', _('Easy e-mail')),
		('helpful.sms.send_sms', _('SMS.RU')),
	)
	backend = models.CharField(_('Backend'), max_length=128, choices=BACKEND)
	on_create = models.BooleanField(_('On create'), default=True)
	on_change = models.BooleanField(_('On change'), default=False)

	public = models.BooleanField(_('Public'), default=True)
	created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
	updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

	def send(self, instance):
		backend_def = import_string(self.backend)
		backend_args = {}

		for arg in self.property.all():
			if arg.value.startswith('!!!EXEC:'):
				str_exec = arg.value[8:]
				# !!!EXEC:'from %s to %s' % (instance.from, instance.to)
				# !!!EXEC:{'instance': instance}
				exec 'value = ' + str_exec
				backend_args[arg.key] = value

			else:
				backend_args[arg.key] = arg.value

		backend_def(**backend_args)


	def __unicode__(self):
		return self.name

	class Meta:
		ordering = ['name']
		verbose_name = _('Notify')
		verbose_name_plural = _('Notifies')


class NotifyProperty(models.Model):
	notify = models.ForeignKey(Notify, verbose_name=_('Notify'), related_name='property')
	name = models.CharField(_('Name'), max_length=128)
	key = models.SlugField(_('Key'), max_length=128)
	value = models.TextField(_('Value'), null=True, blank=True)

	def __unicode__(self):
		return self.name

	class Meta:
		ordering = ['notify', 'name']
		verbose_name = _('Notify property')
		verbose_name_plural = _('Notify properties')


@receiver(post_save)
def send_notify(sender, instance, created, **kwargs):

	content_type = ContentType.objects.get_for_model(sender)
	notify_list = Notify.objects.filter(public=True, content_type__in=[content_type])

	if created:
		notify_list = notify_list.filter(on_create=True)
	else:
		notify_list = notify_list.filter(on_change=True)

	for notify in notify_list:
		notify.send(instance)
