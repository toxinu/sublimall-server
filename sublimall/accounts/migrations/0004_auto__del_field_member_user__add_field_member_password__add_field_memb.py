# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from sublimall.accounts.utils import get_hash


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Member.user'
        db.delete_column('accounts_member', 'user_id')

        # Adding field 'Member.password'
        db.add_column('accounts_member', 'password',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128),
                      keep_default=False)

        # Adding field 'Member.last_login'
        db.add_column('accounts_member', 'last_login',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Member.is_superuser'
        db.add_column('accounts_member', 'is_superuser',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Member.email'
        db.add_column('accounts_member', 'email',
                      self.gf('django.db.models.fields.EmailField')(unique=False, blank=True, default=lambda: get_hash(), max_length=75),
                      keep_default=False)

        # Adding field 'Member.is_staff'
        db.add_column('accounts_member', 'is_staff',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Member.date_joined'
        db.add_column('accounts_member', 'date_joined',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding M2M table for field groups on 'Member'
        m2m_table_name = db.shorten_name('accounts_member_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('member', models.ForeignKey(orm['accounts.member'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['member_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'Member'
        m2m_table_name = db.shorten_name('accounts_member_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('member', models.ForeignKey(orm['accounts.member'], null=False)),
            ('permission', models.ForeignKey(orm['auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['member_id', 'permission_id'])


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Member.user'
        raise RuntimeError("Cannot reverse this migration. 'Member.user' and its values cannot be restored.")

        # The following code is provided here to aid in writing a correct migration        # Adding field 'Member.user'
        db.add_column('accounts_member', 'user',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True),
                      keep_default=False)

        # Deleting field 'Member.password'
        db.delete_column('accounts_member', 'password')

        # Deleting field 'Member.last_login'
        db.delete_column('accounts_member', 'last_login')

        # Deleting field 'Member.is_superuser'
        db.delete_column('accounts_member', 'is_superuser')

        # Deleting field 'Member.email'
        db.delete_column('accounts_member', 'email')

        # Deleting field 'Member.is_staff'
        db.delete_column('accounts_member', 'is_staff')

        # Deleting field 'Member.date_joined'
        db.delete_column('accounts_member', 'date_joined')

        # Removing M2M table for field groups on 'Member'
        db.delete_table(db.shorten_name('accounts_member_groups'))

        # Removing M2M table for field user_permissions on 'Member'
        db.delete_table(db.shorten_name('accounts_member_user_permissions'))


    models = {
        'accounts.member': {
            'Meta': {'object_name': 'Member'},
            'api_key': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '40'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'False', 'blank': 'True', 'max_length': '75'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True', 'related_name': "'user_set'", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'related_name': "'user_set'", 'symmetrical': 'False'})
        },
        'accounts.registration': {
            'Meta': {'object_name': 'Registration'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'member': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Member']", 'unique': 'True'})
        },
        'accounts.usertemp': {
            'Meta': {'object_name': 'UserTemp'},
            'api_key': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '40'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'blank': 'True', 'max_length': '75'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True', 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accounts']
