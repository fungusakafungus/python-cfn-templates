class Facts(dict):

    def to_json(self):
        return '\n'.join(['---'] + list('{0}: {1}'.format(k,v) for k,v in sorted(self.items()))) + '\n'
