class AppRouter:
    def db_for_read(self, model, **hints):
        label = model._meta.app_label
        name  = model.__name__
        if label == 'chat':
            return 'chat_db'
        if label == 'profiles' and name == 'ProfileImage':
            return 'media_db'
        return 'default'

    def db_for_write(self, model, **hints):
        label = model._meta.app_label
        name  = model.__name__
        if label == 'chat':
            return 'chat_db'
        if label == 'profiles' and name == 'ProfileImage':
            return 'media_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'chat':
            return db == 'chat_db'
        if app_label == 'profiles' and model_name == 'profileimage':
            return db == 'media_db'
        if app_label == 'profiles' and model_name != 'profileimage':
            return db == 'default'
        return db == 'default'
