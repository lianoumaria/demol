class SClass:
    def to_dict(self):
        return {
            key: val for key, val in self.__dict__.items() \
            if not key.startswith('_') and key not in ('parent')
        }


