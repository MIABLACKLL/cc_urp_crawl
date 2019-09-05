# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CcExam(models.Model):
    cc_id = models.CharField(primary_key=True, max_length=20)
    course_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=10, blank=True, null=True)
    begin_time = models.CharField(max_length=20, blank=True, null=True)
    end_time = models.CharField(max_length=20, blank=True, null=True)
    hand_time = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cc_exam'
        unique_together = (('cc_id', 'name', 'course_name'),)


class CcFile(models.Model):
    course_name = models.CharField(max_length=255)
    teacher_name = models.CharField(max_length=255)
    file_name = models.CharField(primary_key=True, max_length=255)
    file_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cc_file'
        unique_together = (('file_name', 'course_name', 'teacher_name'),)


class CcHomework(models.Model):
    cc_id = models.CharField(primary_key=True, max_length=20)
    course_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=10, blank=True, null=True)
    begin_time = models.CharField(max_length=20, blank=True, null=True)
    end_time = models.CharField(max_length=20, blank=True, null=True)
    hand_time = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    finish_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cc_homework'
        unique_together = (('cc_id', 'name', 'course_name'),)


class CcTakes(models.Model):
    cc_id = models.CharField(primary_key=True, max_length=20)
    course_name = models.CharField(max_length=255)
    teacher_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'cc_takes'
        unique_together = (('cc_id', 'course_name', 'teacher_name'),)


class CcUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    cc_id = models.CharField(max_length=20)
    cc_password = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cc_user'


class UrpGrade(models.Model):
    urp_user = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255, blank=True, null=True)
    course_id = models.IntegerField(primary_key=True)
    grade = models.FloatField(blank=True, null=True)
    credit = models.FloatField(blank=True, null=True)
    exam_time = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'urp_grade'
        unique_together = (('course_id', 'urp_user', 'exam_time'),)


class UrpUser(models.Model):
    urp_user = models.CharField(max_length=30)
    user_id = models.IntegerField(primary_key=True)
    urp_password = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'urp_user'


class WxUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'wx_user'
        unique_together = (('user_id', 'uuid'),)
