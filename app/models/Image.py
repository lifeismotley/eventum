from flask import url_for
from mongoengine import ValidationError
from app import app, db
from datetime import datetime
import PIL, re, os
now = datetime.now


class Image(db.Document):

    date_created = db.DateTimeField(
        default=now, required=True, verbose_name="Date Created",
        help_text="DateTime when the document was created, localized to the server")
    date_modified = db.DateTimeField(
        default=now, required=True, verbose_name="Date Modified",
        help_text="DateTime when the document was last modified, localized to the server")
    filename = db.StringField(
        unique=True, max_length=255, required=True, verbose_name="Filename",
        regex="([a-z]|[A-Z]|[0-9]|\||-|_|@|\(|\))*(" + \
        ('|'.join(app.config['ALLOWED_EXTENSIONS'])+')'),
        help_text="Title of the event (255 characters max)")
    creator = db.ReferenceField(
        'User', required=True, verbose_name="Creator",
        help_text="Reference to the User that uploaded the photo")
    caption = db.StringField(
        verbose_name="Caption", help_text="A caption for the picture.")
    source = db.StringField(
        verbose_name="Image Source",
        help_text="A source credit for the picture, if one is needed.")
    default_path = db.StringField(
        required=True, verbose_name="Default Path to Image",
        help_text="The path the the version of the image that should be used by default")
    versions = db.DictField(
        required=True, verbose_name="File Versions",
        help_text="A dictionary of sizes to file paths.")

    def url(self):
        return url_for('media.file', filename=self.filename)

    def clean(self):
        """Update date_modified and populate the versions dict."""
        VALID_PATHS = re.compile("^("+app.config['BASEDIR']+"|http://|https://).*$")
        self.date_modified = now()
        print self.default_path
        print app.config['BASEDIR']
        if not VALID_PATHS.match(self.default_path):
            self.default_path = os.path.join(app.config['BASEDIR'], self.default_path)
        if self.default_path and self.default_path not in self.versions.values():
            try:
                width, height = PIL.Image.open(self.default_path).size
                self.versions['%sx%s' % (width, height)] = self.default_path
            except IOError:
                raise ValidationError('File %s does not exist.' % self.default_path)


    def pre_validate(form):
        """Ensure that the versions dictionary contains keys of the form: <width>x<height>, where
        `width` and `height` are the size of the image at the path."""
        for size,path in form.versions:
            try:
                width, height = PIL.Image.open(path).size
                if size != '%sx%s' % (width, height):
                    raise ValidationError('Key %s improperly describes image %s', (size, path))
            except IOError:
                raise ValidationError('File %s does not exist.' % form.default_path)

    meta = {
        'allow_inheritance': True,
        'indexes': ['creator'],
        'ordering': ['-date_created']
    }

    def __unicode__(self):
        return self.title

    def __repr__(self):
        rep = 'Photo(filename=%r, default_path=%r, caption=%r)' % \
        (self.filename, self.default_path, self.caption)
        return rep
