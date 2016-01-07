from django.db import models
from advisingumich.mixins import AdvisingUmichDataCleanupMixin
from advising import utils


class UsernameField(models.CharField):
    '''Convert case for data warehouse values. Only handles read situations,
    this implementation would need to be extended if writing to the dataset is
    necessary.'''

    def from_db_value(self, value, expression, connection, context):
        return value.lower()

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(UsernameField, self).get_db_prep_value(
            value, connection, prepared)
        if value is not None:
            return value.upper()
        return value


# "Dimension" models


class Advisor(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ADVSR_KEY')
    username = UsernameField(max_length=16, db_column='ADVSR_UM_UNQNM')
    univ_id = models.CharField(max_length=11, db_column='ADVSR_UM_ID')
    first_name = models.CharField(max_length=500,
                                  db_column='ADVSR_PREF_FIRST_NM')
    last_name = models.CharField(max_length=500, db_column='ADVSR_PREF_SURNM')
    students = models.ManyToManyField('Student', through='StudentAdvisorRole')

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = '"CNLYR002"."DM_ADVSR"'
        managed = False


class Date(models.Model):
    id = models.IntegerField(primary_key=True, db_column='DT_KEY')
    date = models.DateField(db_column='CAL_DT')

    def __unicode__(self):
        return self.date.isoformat()

    class Meta:
        db_table = '"CNLYR001"."DM_DT"'
        managed = False


class Mentor(models.Model):
    id = models.IntegerField(primary_key=True, db_column='MNTR_KEY')
    username = UsernameField(max_length=16, db_column='MNTR_UM_UNQNM')
    univ_id = models.CharField(max_length=11, db_column='MNTR_UM_ID')
    first_name = models.CharField(max_length=500,
                                  db_column='MNTR_PREF_FIRST_NM')
    last_name = models.CharField(max_length=500, db_column='MNTR_PREF_SURNM')
    students = models.ManyToManyField('Student', through='StudentCohortMentor')

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = '"CNLYR002"."DM_MNTR"'
        managed = False


class Status(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ACAD_PERF_KEY')
    code = models.CharField(max_length=20, db_column='ACAD_PERF_VAL')
    description = models.CharField(max_length=50, db_column='ACAD_PERF_TXT')
    order = models.IntegerField(db_column='ACAD_PERF_ORDNL_NBR')

    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ('order',)
        db_table = '"CNLYR002"."DM_ACAD_PERF"'
        managed = False


class Student(models.Model):
    id = models.IntegerField(primary_key=True, db_column='STDNT_KEY')
    username = UsernameField(max_length=16, db_column='STDNT_UM_UNQNM')
    univ_id = models.CharField(max_length=11, db_column='STDNT_UM_ID')
    first_name = models.CharField(max_length=500,
                                  db_column='STDNT_PREF_FIRST_NM')
    last_name = models.CharField(max_length=500, db_column='STDNT_PREF_SURNM')
    mentors = models.ManyToManyField('Mentor', through='StudentCohortMentor')
    cohorts = models.ManyToManyField('Cohort', through='StudentCohortMentor')
    class_sites = models.ManyToManyField('ClassSite',
                                         through='StudentClassSiteStatus')
    statuses = models.ManyToManyField('Status',
                                      through='StudentClassSiteStatus')

    @property
    def advisors(self):
        return utils.aggrate_relationships(self.studentadvisorrole_set.all(),
                                           'advisor', 'role')

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = '"CNLYR002"."DM_STDNT"'
        managed = False


class Term(models.Model):
    id = models.IntegerField(primary_key=True, db_column='TERM_KEY')
    code = models.CharField(max_length=6, db_column='TERM_CD')
    description = models.CharField(max_length=30, db_column='TERM_DES')
    _begin_date = models.DateField(db_column='TERM_BEGIN_DT')
    _end_date = models.DateField(db_column='ACAD_TERM_END_DT')

    @property
    def begin_date(self):
        return Date.objects.get(date=self._begin_date)

    @property
    def end_date(self):
        return Date.objects.get(date=self._end_date)

    def week_end_dates(self):
        from datetime import timedelta
        from datetime import datetime

        print str(self.end_date)
        begin_date = datetime.strptime(str(self.begin_date), '%Y-%m-%d').date()
        end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d').date()

        delta = end_date - begin_date
        dates = []
        for i in range(delta.days + 1):
            date = begin_date + timedelta(days=i)
            if date.weekday() == 5:
                dates.append(Date.objects.get(date=date))

        return dates

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = '"CNLYR001"."DM_TERM"'
        managed = False


class SourceSystem(models.Model):
    id = models.IntegerField(primary_key=True, db_column='SRC_SYS_KEY')
    code = models.CharField(max_length=6, db_column='SRC_SYS_CD')
    description = models.CharField(max_length=30, db_column='SRC_SYS_NM')
    long_description = models.CharField(max_length=30, db_column='SRC_SYS_DES')

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = '"CNLYR002"."DM_SRC_SYS"'
        managed = False


# "Dimension" models that depend on SourceSystem


class AdvisorRole(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ADVSR_ROLE_KEY')
    code = models.CharField(max_length=4, db_column='ADVSR_ROLE_CD')
    description = models.CharField(max_length=30, db_column='ADVSR_ROLE_DES')

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = '"CNLYR002"."DM_ADVSR_ROLE"'
        managed = False


class Assignment(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ASSGN_KEY')
    code = models.CharField(max_length=20, db_column='ASSGN_CD')
    description = models.CharField(max_length=50, db_column='ASSGN_DES')
    source_system = models.ForeignKey(SourceSystem, db_column='SRC_SYS_KEY')

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = '"CNLYR002"."DM_ASSGN"'
        managed = False


class ClassSite(models.Model):
    id = models.IntegerField(primary_key=True, db_column='CLASS_SITE_KEY')
    code = models.CharField(max_length=20, db_column='CLASS_SITE_CD')
    description = models.CharField(max_length=50, db_column='CLASS_SITE_DES')
    terms = models.ManyToManyField('Term', through='ClassSiteTerm')
    source_system = models.ForeignKey(SourceSystem, db_column='SRC_SYS_KEY')

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = '"CNLYR002"."DM_CLASS_SITE"'
        managed = False


class Cohort(models.Model):
    id = models.IntegerField(primary_key=True, db_column='CHRT_KEY')
    code = models.CharField(max_length=20, db_column='CHRT_CD')
    description = models.CharField(max_length=50, db_column='CHRT_DES')
    group = models.CharField(max_length=100, db_column='CHRT_GRP_NM')
    source_system = models.ForeignKey(SourceSystem, db_column='SRC_SYS_KEY')

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = '"CNLYR002"."DM_CHRT"'
        managed = False


class EventType(models.Model):
    id = models.IntegerField(primary_key=True, db_column='EVENT_TYP_KEY')
    source_system = models.ForeignKey(SourceSystem, db_column='SRC_SYS_KEY')
    description = models.CharField(max_length=50, db_column='EVENT_TYP_NM')

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = '"CNLYR002"."DM_EVENT_TYP"'
        managed = False


# "Bridge" models


class ClassSiteTerm(models.Model):
    id = models.IntegerField(primary_key=True, db_column='CLASS_SITE_TERM_KEY')
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY')
    term = models.ForeignKey(Term, db_column='TERM_KEY')

    def __unicode__(self):
        return '%s was held in %s' % (self.class_site, self.term)

    class Meta:
        db_table = '"CNLYR002"."BG_CLASS_SITE_TERM"'
        managed = False


class StudentAdvisorRole(models.Model):
    student = models.ForeignKey(Student, db_column='STDNT_KEY',
                                primary_key=True)
    advisor = models.ForeignKey(Advisor, db_column='ADVSR_KEY',
                                primary_key=True)
    role = models.ForeignKey(AdvisorRole, db_column='ADVSR_ROLE_KEY',
                             primary_key=True)

    def __unicode__(self):
        return '%s advises %s as %s' % (self.advisor, self.student, self.role)

    class Meta:
        db_table = '"CNLYR002"."BG_STDNT_ADVSR_ROLE"'
        managed = False


class StudentCohortMentor(models.Model):
    student = models.ForeignKey(Student, db_column='STDNT_KEY',
                                primary_key=True)
    mentor = models.ForeignKey(Mentor, db_column='MNTR_KEY')
    cohort = models.ForeignKey(Cohort, db_column='CHRT_KEY')

    def __unicode__(self):
        return '%s is in the %s cohort' % (self.student, self.cohort)

    class Meta:
        unique_together = ('student', 'cohort')
        db_table = '"CNLYR002"."BG_STDNT_CHRT_MNTR"'
        managed = False


# "Fact" models


class ClassSiteScore(models.Model):
    class_site = models.ForeignKey(ClassSite, primary_key=True,
                                   db_column='CLASS_SITE_KEY')
    current_score_average = models.FloatField(db_column="CLASS_CURR_SCR_AVG")

    def __unicode__(self):
        return '%s has an average score of %s' % (
            self.class_site, self.current_score_average)

    class Meta:
        db_table = '"CNLYR002"."FC_CLASS_SCR"'
        managed = False


class StudentClassSiteScore(models.Model):
    student = models.ForeignKey(Student, primary_key=True,
                                db_column='STDNT_KEY')
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY')
    current_score_average = models.FloatField(db_column="STDNT_CURR_SCR_AVG")

    def __unicode__(self):
        return '%s has an average score of %s in %s' % (
            self.student, self.current_score_average, self.class_site)

    class Meta:
        unique_together = ('student', 'class_site')
        db_table = '"CNLYR002"."FC_STDNT_CLASS_SCR"'
        managed = False


class StudentClassSiteAssignment(models.Model, AdvisingUmichDataCleanupMixin):
    student = models.ForeignKey(Student, db_column='STDNT_KEY',
                                primary_key=True)
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY')
    assignment = models.ForeignKey(Assignment, db_column='ASSGN_KEY')
    points_possible = models.FloatField(max_length=10,
                                        db_column='STDNT_ASSGN_PNTS_PSBL_NBR')
    points_earned = models.FloatField(max_length=10,
                                      db_column='STDNT_ASSGN_PNTS_ERND_NBR')
    class_points_possible = models.FloatField(
        max_length=10,
        db_column='CLASS_ASSGN_PNTS_PSBL_NBR')
    class_points_earned = models.FloatField(
        max_length=10,
        db_column='CLASS_ASSGN_PNTS_ERND_NBR')
    included_in_grade = models.CharField(max_length=1,
                                         db_column='INCL_IN_CLASS_GRD_IND')
    grader_comment = models.CharField(max_length=4000, null=True,
                                      db_column='STDNT_ASSGN_GRDR_CMNT_TXT')
    weight = models.FloatField(max_length=126,
                               db_column='ASSGN_WT_NBR')
    _due_date = models.ForeignKey(Date, db_column='ASSGN_DUE_SBMT_DT_KEY',
                                  null=True)

    def __unicode__(self):
        return '%s has assignemnt %s in %s' % (self.student, self.assignment,
                                               self.class_site)

    @property
    def due_date(self):
        return self.valid_date_or_none(self._due_date)

    @property
    def percentage(self):
        return self._percentage(self.points_earned,
                                self.points_possible)

    @property
    def class_percentage(self):
        return self._percentage(self.class_points_earned,
                                self.class_points_possible)

    def _percentage(self, x, y):
        if x is None:
            return None
        if y is None:
            return None
        if y == 0:
            return None

        return float(x) / float(y) * 100

    class Meta:
        ordering = ('_due_date',)
        unique_together = ('student', 'class_site', 'assignment')
        db_table = '"CNLYR002"."FC_STDNT_CLASS_ASSGN"'
        managed = False


class StudentClassSiteStatus(models.Model):
    student = models.ForeignKey(Student, db_column='STDNT_KEY',
                                primary_key=True)
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY')
    status = models.ForeignKey(Status, db_column='ACAD_PERF_KEY')

    def __unicode__(self):
        return '%s has status %s in %s' % (self.student, self.status,
                                           self.class_site)

    class Meta:
        unique_together = ('student', 'class_site', 'status')
        db_table = '"CNLYR002"."FC_STDNT_CLASS_ACAD_PERF"'
        managed = False


class WeeklyClassSiteScore(models.Model):
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY',
                                   primary_key=True)
    week_end_date = models.ForeignKey(Date, db_column='WEEK_END_DT_KEY')
    score = models.IntegerField(db_column='CLASS_CURR_SCR_AVG')

    def __unicode__(self):
        return 'Average score is %s in %s on %s' % (
            self.score, self.class_site, self.week_end_date)

    class Meta:
        ordering = ('week_end_date',)
        unique_together = ('class_site', 'week_end_date')
        db_table = '"CNLYR002"."FC_CLASS_WKLY_SCR"'
        managed = False


class WeeklyStudentClassSiteEvent(models.Model):
    student = models.ForeignKey(Student, db_column='STDNT_KEY',
                                primary_key=True)
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY')
    week_end_date = models.ForeignKey(Date, db_column='WEEK_END_DT_KEY')
    event_type = models.ForeignKey(EventType, db_column='EVENT_TYP_KEY')

    event_count = models.IntegerField(db_column='STDNT_WKLY_EVENT_CNT')
    cumulative_event_count = models.IntegerField(
        db_column='STDNT_CUM_EVENT_CNT')
    percentile_rank = models.FloatField(db_column='STDNT_WKLY_PCTL_RNK')
    cumulative_percentile_rank = models.FloatField(
        db_column='STDNT_CUM_PCTL_RNK')

    def __unicode__(self):
        return '%s in %s on %s had %s events (%s %%ile)' % (
            self.student, self.class_site, self.week_end_date,
            self.event_count, self.percentile_rank)

    class Meta:
        ordering = ('week_end_date',)
        unique_together = ('student', 'class_site', 'week_end_date')
        db_table = '"CNLYR002"."FC_STDNT_CLASS_WKLY_EVENT"'
        managed = False


class WeeklyStudentClassSiteScore(models.Model):
    student = models.ForeignKey(Student, db_column='STDNT_KEY',
                                primary_key=True)
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY')
    week_end_date = models.ForeignKey(Date, db_column='WEEK_END_DT_KEY')
    score = models.IntegerField(db_column='STDNT_CURR_SCR_AVG')

    def __unicode__(self):
        return '%s has score %s in %s on %s' % (
            self.student, self.score, self.class_site, self.week_end_date)

    class Meta:
        ordering = ('week_end_date',)
        unique_together = ('student', 'class_site', 'week_end_date')
        db_table = '"CNLYR002"."FC_STDNT_CLASS_WKLY_SCR"'
        managed = False


class WeeklyStudentClassSiteStatus(models.Model):
    student = models.ForeignKey(Student, db_column='STDNT_KEY',
                                primary_key=True)
    class_site = models.ForeignKey(ClassSite, db_column='CLASS_SITE_KEY')
    week_end_date = models.ForeignKey(Date, db_column='WEEK_END_DT_KEY')
    status = models.ForeignKey(Status, db_column='ACAD_PERF_KEY')

    def __unicode__(self):
        return '%s has status %s in %s on %s' % (
            self.student, self.status, self.class_site, self.week_end_date)

    class Meta:
        unique_together = ('student', 'class_site', 'week_end_date', 'status')
        db_table = '"CNLYR002"."FC_STDNT_CLS_WKLY_ACAD_PRF"'
        managed = False
