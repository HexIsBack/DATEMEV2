class AppRouter:
    MEDIA_MODELS = {'profileimage', 'profilephoto'}

    # Apps that must always stay in the default (users.sqlite3) database
    DEFAULT_APPS = {
        'admin', 'auth', 'contenttypes', 'sessions', 'messages',
        'accounts', 'profiles', 'matching',
    }

    def db_for_read(self, model, **hints):
        label = model._meta.app_label
        name  = model.__name__.lower()
        if label == 'chat':
            return 'chat_db'
        if label == 'profiles' and name in self.MEDIA_MODELS:
            return 'media_db'
        return 'default'

    def db_for_write(self, model, **hints):
        label = model._meta.app_label
        name  = model.__name__.lower()
        if label == 'chat':
            return 'chat_db'
        if label == 'profiles' and name in self.MEDIA_MODELS:
            return 'media_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'chat':
            return db == 'chat_db'
        if app_label == 'profiles' and model_name in self.MEDIA_MODELS:
            return db == 'media_db'
        # Everything else (including sessions, auth, accounts, matching, etc.)
        # must only migrate to 'default'
        return db == 'default'
